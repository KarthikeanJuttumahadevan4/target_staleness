"""
Hybrid retrieval orchestration module.

This module provides the main entry point for the three retrieval
modes: pure RAG, RAG+KG validator, and KG-only. It orchestrates
the appropriate retrieval strategy based on the query mode.

Usage:
    from src.retrieval.hybrid import query

    results = query("What was the CEO in 2020?", mode="rag_kg_validator")
"""

from __future__ import annotations

from typing import Optional, List
import time
import uuid
from datetime import datetime

from src.models import QueryRequest, RetrievedFact, AnswerResponse
from src.retrieval.pure_rag import pure_rag
from src.retrieval.rag_kg_validator import rag_kg_validator
from src.retrieval.kg_only import kg_only


def query(
    question: str,
    mode: str = "pure_rag",
    as_of: Optional[str] = None,
    include_history: bool = False,
    k: int = 10,
    org_unit: Optional[str] = None,
) -> AnswerResponse:
    """
    Execute a query using the specified retrieval mode.

    This is the main entry point for all retrieval operations.
    It dispatches to the appropriate retrieval mode handler
    and returns a structured result.

    Args:
        question: The user's query string
        mode: Retrieval mode - "pure_rag", "rag_kg_validator", or "kg_only"
        as_of: ISO timestamp for historical query (null = most recent)
        include_history: If True, include superseded facts in results
        k: Number of results to retrieve
        org_unit: Optional organization unit filter for multi-tenancy

    Returns:
        AnswerResponse with results, mode info, and audit tracking

    Raises:
        ValueError: If mode is not one of the supported modes
    """
    start_time = time.time()

    # Validate mode
    valid_modes = {"pure_rag", "rag_kg_validator", "kg_only"}
    if mode not in valid_modes:
        raise ValueError(f"Invalid mode '{mode}'. Must be one of: {valid_modes}")

    # Dispatch to appropriate handler
    if mode == "pure_rag":
        facts = pure_rag(
            question=question, k=k, as_of=as_of, current_only=not include_history
        )
    elif mode == "rag_kg_validator":
        facts = rag_kg_validator(
            question=question, k=k, as_of=as_of, current_only=not include_history
        )
    else:  # kg_only
        facts = kg_only(
            question=question,
            hops=min(k, 5),  # Limit hops to prevent explosion
            as_of=as_of,
            current_only=not include_history,
        )

    latency_ms = int((time.time() - start_time) * 1000)

    # Build result - convert facts to RetrievedFact format if needed
    retrieved_facts = []
    for fact in facts:
        if hasattr(fact, "content"):  # Already a RetrievedFact
            retrieved_facts.append(fact)
        else:  # Need to convert from Fact or dict
            from src.models import RetrievedFact as RF

            retrieved_facts.append(
                RF(
                    fact_id=getattr(fact, "fact_id", str(uuid.uuid4())),
                    content=getattr(fact, "content", str(fact)),
                    source=getattr(fact, "source_file", "unknown"),
                    as_of=getattr(
                        fact, "valid_at", as_of or datetime.now().isoformat()
                    ),
                    current=getattr(fact, "current", True),
                    confidence=getattr(fact, "confidence", 1.0),
                    citation=getattr(fact, "citation", ""),
                    extraction_path=getattr(fact, "extraction_path", None),
                    model_used=getattr(fact, "model_used", None),
                )
            )

    # Build result
    return AnswerResponse(
        answer="",  # Will be filled by generation layer if needed
        facts=retrieved_facts,
        mode=mode,
        confidence=1.0 if retrieved_facts else 0.0,
        audit_id=f"audit_{int(time.time())}",
    )


def build_query_request(
    question: str,
    mode: str = "pure_rag",
    as_of: Optional[str] = None,
    include_history: bool = False,
    k: int = 10,
    org_unit: Optional[str] = None,
) -> QueryRequest:
    """
    Build a QueryRequest for the API layer.
    """
    return QueryRequest(
        question=question,
        mode=mode,
        as_of=as_of,
        include_history=include_history,
        k=k,
        org_unit=org_unit,
    )
