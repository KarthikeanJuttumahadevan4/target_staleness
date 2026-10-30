"""
Pure RAG retrieval module.

This module implements the pure RAG retrieval mode which uses only
vector similarity search to retrieve relevant facts. Results are
filtered to current facts only by default.

Usage:
    from src.retrieval.pure_rag import pure_rag

    results = pure_rag("What was the CEO in 2020?", k=10)
"""

from __future__ import annotations

from typing import List, Optional
import time

from src.models import QueryRequest, RetrievedFact, AnswerResponse


def pure_rag(
    question: str, k: int = 10, as_of: Optional[str] = None, current_only: bool = True
) -> List[RetrievedFact]:
    """
    Retrieve facts using pure vector similarity search.

    This is the simplest retrieval mode - encode the query to a vector,
    perform similarity search, and return results. By default, only
    current facts are returned.

    Args:
        question: The query string
        k: Number of results to return
        as_of: Optional ISO timestamp for historical query
        current_only: If True, filter to current=true facts only

    Returns:
        List of RetrievedFact objects sorted by similarity

    Note:
        This is a scaffold - the actual vector store (Qdrant) integration
        needs to be wired by the tech lead.
    """
    # TODO: Tech lead - integrate with Qdrant vector store
    # 1. Encode question to embedding (SentenceTransformer)
    # 2. Query Qdrant with payload filter (current=true if current_only)
    # 3. Map results to RetrievedFact

    # Placeholder return - implement when vector store is ready
    return []


def build_query_request(
    question: str,
    mode: str = "pure_rag",
    as_of: Optional[str] = None,
    k: int = 10,
    include_history: bool = False,
) -> QueryRequest:
    """
    Build a QueryRequest for this retrieval mode.
    """
    return QueryRequest(
        question=question, mode=mode, as_of=as_of, include_history=include_history, k=k
    )
