"""
KG-only retrieval module.

This module implements the graph traversal-based retrieval mode
that queries the knowledge graph directly without vector search.
It uses Cypher queries to traverse entity relationships and
retrieve relevant facts.

Usage:
    from src.retrieval.kg_only import kg_only

    results = kg_only("What was the CEO in 2020?", hops=2)
"""

from __future__ import annotations

from typing import List, Optional
import time

from src.models import QueryRequest, RetrievedFact


def kg_only(
    question: str, hops: int = 2, as_of: Optional[str] = None, current_only: bool = True
) -> List[RetrievedFact]:
    """
    Retrieve facts using pure graph traversal.

    This mode bypasses vector search entirely and queries the
    knowledge graph using Cypher traversals. It's useful when
    graph structure is more important than semantic similarity.

    Process:
    1. Extract entity candidates from the question
    2. Traverse the graph from seed entities
    3. Collect facts within N hops
    4. Filter by temporal validity (as_of, current)

    Args:
        question: The query string
        hops: Maximum graph traversal depth
        as_of: Optional ISO timestamp for historical query
        current_only: If True, only return current facts

    Returns:
        List of RetrievedFact objects from graph traversal

    Note:
        Requires integration with Neo4j temporal knowledge graph.
    """
    # TODO: Tech lead - integrate with Neo4j
    # 1. Extract entities from question (NER or seed nodes)
    # 2. Cypher query with MATCH (f:Fact) WHERE f.current=true
    # 3. BFS traversal up to 'hops' depth
    # 4. Return sorted by confidence/temporal relevance

    return []


def traverse_graph(
    seed_entities: List[str], hops: int = 2, as_of: Optional[str] = None
) -> List[dict]:
    """
    Traverse the knowledge graph from seed entities.

    Uses Neo4j's built-in graph traversal algorithms
    to explore relationships.
    """
    # TODO: Tech lead implementation
    pass
