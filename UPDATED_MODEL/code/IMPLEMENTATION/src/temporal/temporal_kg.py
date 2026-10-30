"""
Temporal Knowledge Graph module for Neo4j integration.

This module provides the TemporalKG class which manages the temporal
knowledge graph storage in Neo4j. It handles fact upserts, queries,
and supersession relationships.

The knowledge graph stores facts with full temporal metadata:
- valid_at: when the fact was true in the world
- invalid_at: when the fact was superseded
- current: boolean flag for current validity

This enables:
- Temporal queries (what was true on date X?)
- Conflict detection and resolution
- Historical audit trails

Usage:
    from src.temporal.temporal_kg import TemporalKG

    kg = TemporalKG(uri="bolt://localhost:7687", user="neo4j", password="password")
    fact_id = kg.upsert_fact(...)
    facts = kg.get_current_facts(entity_id, predicate)
    kg.close()
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

from neo4j import GraphDatabase

from src.config import get_settings
from src.models import Fact


class TemporalKG:
    """
    Temporal Knowledge Graph backed by Neo4j.

    This class provides methods for storing, querying, and managing
    facts in a temporal knowledge graph. It implements the bi-temporal
    model required by the system.

    Attributes:
        driver: Neo4j driver instance for database connections
        settings: Application settings for configuration
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """
        Initialize the TemporalKG with Neo4j connection.

        Args:
            uri: Neo4j bolt URI (default from settings)
            user: Neo4j username (default from settings)
            password: Neo4j password (default from settings)
        """
        settings = get_settings()
        self._uri = uri or settings.neo4j_uri
        self._user = user or settings.neo4j_user
        self._password = password or settings.neo4j_password
        self.driver = None

    def connect(self) -> None:
        """Establish connection to Neo4j database."""
        if self.driver is None:
            self.driver = GraphDatabase.driver(
                self._uri, auth=(self._user, self._password)
            )

    def close(self) -> None:
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.driver = None

    def get_current_facts(self, entity_id: str, predicate: str) -> List[Dict[str, Any]]:
        """
        Get all current facts for an entity and predicate.

        This returns only facts where current=true, which is the
        default behavior for retrieval modes.

        Args:
            entity_id: The entity identifier to query
            predicate: The relationship type (e.g., "CEO_OF")

        Returns:
            List of fact dictionaries ordered by valid_at descending
        """
        if self.driver is None:
            self.connect()

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (f:Fact) 
                WHERE f.entity_id = $entity_id 
                  AND f.predicate = $predicate 
                  AND f.current = true
                RETURN f 
                ORDER BY f.valid_at DESC
                """,
                entity_id=entity_id,
                predicate=predicate,
            )
            return [dict(record["f"]) for record in result]

    def get_facts_as_of(
        self, entity_id: str, predicate: str, as_of: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get facts valid at a specific point in time.

        This enables historical queries: "what was true on date X?"

        Args:
            entity_id: The entity identifier to query
            predicate: The relationship type
            as_of: The timestamp to query as of

        Returns:
            List of fact dictionaries valid at the given time
        """
        if self.driver is None:
            self.connect()

        as_of_str = as_of.isoformat()

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (f:Fact) 
                WHERE f.entity_id = $entity_id 
                  AND f.predicate = $predicate
                  AND f.valid_at <= $as_of
                  AND (f.invalid_at IS NULL OR f.invalid_at > $as_of)
                RETURN f 
                ORDER BY f.valid_at DESC
                """,
                entity_id=entity_id,
                predicate=predicate,
                as_of=as_of_str,
            )
            return [dict(record["f"]) for record in result]

    def upsert_fact(
        self,
        fact_id: str,
        entity_id: str,
        predicate: str,
        object_value: Optional[str],
        valid_at: datetime,
        source_file: str,
        extraction_path: str,
        model_used: str,
        current: bool = True,
        confidence: float = 1.0,
    ) -> str:
        """
        Insert or update a fact in the knowledge graph.

        This creates a Fact node with all temporal and provenance metadata.
        If a fact with the same fact_id exists, it updates the existing node.

        Args:
            fact_id: Unique identifier for the fact
            entity_id: Canonical entity identifier
            predicate: Relationship type
            object_value: Optional object value
            valid_at: When this fact is valid from
            source_file: Original document path
            extraction_path: How the fact was extracted
            model_used: Which model extracted this fact
            current: Whether this fact is currently valid
            confidence: Confidence score (0.0-1.0)

        Returns:
            The fact_id that was inserted/updated
        """
        if self.driver is None:
            self.connect()

        created_at = datetime.utcnow().isoformat() + "Z"
        valid_at_str = (
            valid_at.isoformat() if isinstance(valid_at, datetime) else valid_at
        )

        with self.driver.session() as session:
            session.run(
                """
                MERGE (f:Fact {fact_id: $fact_id})
                SET f.entity_id = $entity_id,
                    f.predicate = $predicate,
                    f.object_value = $object_value,
                    f.valid_at = $valid_at,
                    f.source_file = $source_file,
                    f.extraction_path = $extraction_path,
                    f.model_used = $model_used,
                    f.current = $current,
                    f.confidence = $confidence,
                    f.created_at = $created_at
                """,
                fact_id=fact_id,
                entity_id=entity_id,
                predicate=predicate,
                object_value=object_value,
                valid_at=valid_at_str,
                source_file=source_file,
                extraction_path=extraction_path,
                model_used=model_used,
                current=current,
                confidence=confidence,
                created_at=created_at,
            )

        return fact_id

    def supersede_fact(self, old_fact_id: str, new_fact_id: str, at: datetime) -> None:
        """
        Mark an old fact as superseded by a new fact.

        This implements the most-recent-wins policy:
        1. Mark old fact as current=false
        2. Set invalid_at to the supersession time
        3. Create SUPERSEDES edge to the new fact

        Args:
            old_fact_id: The fact being superseded
            new_fact_id: The fact that supersedes it
            at: When the supersession occurred
        """
        if self.driver is None:
            self.connect()

        at_str = at.isoformat() if isinstance(at, datetime) else at

        with self.driver.session() as session:
            session.run(
                """
                MATCH (old:Fact {fact_id: $old_id})
                MATCH (new:Fact {fact_id: $new_id})
                SET old.current = false,
                    old.invalid_at = datetime($at),
                    old.expired_at = datetime()
                MERGE (new)-[:SUPERSEDES {at: $at}]->(old)
                """,
                old_id=old_fact_id,
                new_id=new_fact_id,
                at=at_str,
            )

    def get_supersession_chain(self, fact_id: str) -> List[Dict[str, Any]]:
        """
        Get the chain of facts that supersede this fact.

        Returns the full history of supersessions for audit purposes.

        Args:
            fact_id: The starting fact ID

        Returns:
            List of facts in the supersession chain (newest first)
        """
        if self.driver is None:
            self.connect()

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (new:Fact)-[:SUPERSEDES*]->(old:Fact {fact_id: $fid})
                RETURN new
                ORDER BY new.valid_at DESC
                """,
                fid=fact_id,
            )
            return [dict(record["new"]) for record in result]

    def find_by_source(self, source_file: str) -> List[Dict[str, Any]]:
        """
        Find all facts from a specific source file.

        Args:
            source_file: The source document path

        Returns:
            All facts linked to this source
        """
        if self.driver is None:
            self.connect()

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (f:Fact)
                WHERE f.source_file = $source
                RETURN f
                ORDER BY f.valid_at DESC
                """,
                source=source_file,
            )
            return [dict(record["f"]) for record in result]


def init_schema(driver) -> None:
    """
    Initialize the Neo4j schema with constraints and indexes.

    This should be called once when setting up the database.
    All statements are idempotent (safe to run multiple times).

    Args:
        driver: Neo4j driver instance
    """
    schema_statements = [
        # Constraints
        "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE",
        "CREATE CONSTRAINT fact_id_unique IF NOT EXISTS FOR (f:Fact) REQUIRE f.fact_id IS UNIQUE",
        "CREATE CONSTRAINT source_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.source_file IS UNIQUE",
        # Indexes for fast queries
        "CREATE INDEX fact_current IF NOT EXISTS FOR (f:Fact) ON (f.current)",
        "CREATE INDEX fact_valid_at IF NOT EXISTS FOR (f:Fact) ON (f.valid_at)",
        "CREATE INDEX fact_invalid_at IF NOT EXISTS FOR (f:Fact) ON (f.invalid_at)",
        "CREATE INDEX fact_entity IF NOT EXISTS FOR (f:Fact) ON (f.entity_id)",
        "CREATE INDEX fact_predicate IF NOT EXISTS FOR (f:Fact) ON (f.predicate)",
        "CREATE INDEX fact_source IF NOT EXISTS FOR (f:Fact) ON (f.source_file)",
    ]

    with driver.session() as session:
        for stmt in schema_statements:
            session.run(stmt)
