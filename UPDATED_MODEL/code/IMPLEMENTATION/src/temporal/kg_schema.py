"""
Neo4j schema definitions for the temporal knowledge graph.

This module provides the Cypher statements for creating constraints
and indexes needed for efficient temporal queries.
"""

from __future__ import annotations

from typing import List

# Cypher statements for schema initialization
# These are idempotent - safe to run multiple times

SCHEMA_STATEMENTS: List[str] = [
    # Uniqueness constraints
    """
    CREATE CONSTRAINT entity_id_unique IF NOT EXISTS 
    FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT fact_id_unique IF NOT EXISTS 
    FOR (f:Fact) REQUIRE f.fact_id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT source_unique IF NOT EXISTS 
    FOR (d:Document) REQUIRE d.source_file IS UNIQUE
    """,
    # Indexes for fast queries
    """
    CREATE INDEX fact_current IF NOT EXISTS 
    FOR (f:Fact) ON (f.current)
    """,
    """
    CREATE INDEX fact_valid_at IF NOT EXISTS 
    FOR (f:Fact) ON (f.valid_at)
    """,
    """
    CREATE INDEX fact_invalid_at IF NOT EXISTS 
    FOR (f:Fact) ON (f.invalid_at)
    """,
    """
    CREATE INDEX fact_entity IF NOT EXISTS 
    FOR (f:Fact) ON (f.entity_id)
    """,
    """
    CREATE INDEX fact_predicate IF NOT EXISTS 
    FOR (f:Fact) ON (f.predicate)
    """,
    """
    CREATE INDEX fact_source IF NOT EXISTS 
    FOR (f:Fact) ON (f.source_file)
    """,
]


def get_schema_statements() -> List[str]:
    """Return the list of schema initialization statements."""
    return SCHEMA_STATEMENTS
