"""
Retrieval module for the Temporal-Valid KG RAG System.

This module provides three retrieval modes:
- pure_rag: Vector-only similarity search
- rag_kg_validator: Hybrid with KG validation
- kg_only: Graph traversal only

Usage:
    from src.retrieval import query

    results = query("Who was CEO?", mode="rag_kg_validator")
"""

from .hybrid import query
from .pure_rag import pure_rag
from .rag_kg_validator import rag_kg_validator
from .kg_only import kg_only

__all__ = ["query", "pure_rag", "rag_kg_validator", "kg_only"]
