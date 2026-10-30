"""
Query Classifier Module
=======================

Automatically determines the optimal retrieval mode based on query content.
Decides between RAG, KG, or hybrid approaches.

Usage:
    from src.classification.query_classifier import classify_query

    mode = classify_query("Who is the CEO of Microsoft?")
    # Returns: "kg_only" for entity queries

    mode = classify_query("What does the latest policy say about remote work?")
    # Returns: "pure_rag" for content queries
"""

from __future__ import annotations

from typing import Literal, Tuple
import re


# Type alias for clarity
RetrievalMode = Literal["pure_rag", "rag_kg_validator", "kg_only"]


class QueryClassifier:
    """
    Classifies queries to determine the optimal retrieval strategy.

    Classification Rules:
    - Entity/Object queries → KG-only (graph traversal)
    - Content/Fact queries → Pure RAG (vector search)
    - Complex/Validating queries → RAG+KG (hybrid with validation)
    """

    def __init__(self):
        # Entity/object patterns - use KG
        self.entity_patterns = [
            r"\bwho is\b",
            r"\bwhat is\b",
            r"\bwhen is\b",
            r"\bwhere is\b",
            r"\bwhich (company|organization|person|entity)\b",
            r"\bname of\b",
            r"\bidentify\b",
            r"\blist all\b",
            r"\bshow me\b",
            r"\bcount\b",
            r"\bhow many\b",
        ]

        # Content/fact patterns - use RAG
        self.content_patterns = [
            r"\bwhat does\b",
            r"\bwhat are\b",
            r"\bsummarize\b",
            r"\bexplain\b",
            r"\bdescribe\b",
            r"\bcompare\b",
            r"\bdifference\b",
            r"\bhow to\b",
            r"\bsteps to\b",
            r"\bprocess of\b",
            r"\bmethod\b",
            r"\bapproach\b",
            r"\bframework\b",
        ]

        # Complex/validation patterns - use RAG+KG
        self.complex_patterns = [
            r"\bvalidate\b",
            r"\bverify\b",
            r"\bcheck if\b",
            r"\bcross[\s-]reference\b",
            r"\bsource\b",
            r"\bcitation\b",
            r"\baccording to\b",
            r"\bas of\b",
            r"\btemporal\b",
            r"\bchanged?\b",
            r"\bupdated\b",
            r"\breplaced\b",
            r"\bsuperseded\b",
            r"\bhistory\b",
            r"\bprevious\b",
            r"\bformer\b",
            r"\bcurrent\b",
        ]

        # Temporal patterns - prefer KG for time-based queries
        self.temporal_patterns = [
            r"\b20\d{2}\b",
            r"\b\d{4}\b",
            r"\bjanuary|february|march|april|may|june|july|august|september|october|november|december\b",
            r"\bago\b",
            r"\bfuture\b",
            r"\bpast\b",
        ]

    def classify(self, query: str) -> Tuple[RetrievalMode, str]:
        """
        Classify a query and return the optimal retrieval mode.

        Args:
            query: The user's natural language query

        Returns:
            Tuple of (mode, reason) where mode is one of:
            - "kg_only": For entity/object identification
            - "pure_rag": For content/fact retrieval
            - "rag_kg_validator": For validation/complex queries
        """
        query_lower = query.lower().strip()

        # Check for complex patterns first (highest priority)
        for pattern in self.complex_patterns:
            if re.search(pattern, query_lower):
                return (
                    "rag_kg_validator",
                    "Query requires validation or has temporal aspects",
                )

        # Check for temporal patterns
        for pattern in self.temporal_patterns:
            if re.search(pattern, query_lower):
                return ("rag_kg_validator", "Query has temporal element")

        # Check for entity/object patterns
        for pattern in self.entity_patterns:
            if re.search(pattern, query_lower):
                return ("kg_only", "Query seeks entity or object information")

        # Check for content patterns
        for pattern in self.content_patterns:
            if re.search(pattern, query_lower):
                return ("pure_rag", "Query seeks content or explanation")

        # Default: use hybrid for unknown queries
        return ("rag_kg_validator", "Default hybrid mode for unknown query type")

    def get_confidence(self, query: str, mode: RetrievalMode) -> float:
        """
        Estimate confidence in the classification.

        Returns:
            Confidence score between 0.0 and 1.0
        """
        query_lower = query.lower().strip()

        # Count matching patterns
        if mode == "kg_only":
            patterns = self.entity_patterns
        elif mode == "pure_rag":
            patterns = self.content_patterns
        else:  # rag_kg_validator
            patterns = self.complex_patterns + self.temporal_patterns

        matches = sum(1 for p in patterns if re.search(p, query_lower))

        # Higher matches = higher confidence
        if matches == 0:
            return 0.5  # Unknown
        elif matches == 1:
            return 0.7
        elif matches == 2:
            return 0.85
        else:
            return 0.95


def classify_query(query: str) -> Tuple[RetrievalMode, str, float]:
    """
    Convenience function to classify a query.

    Args:
        query: The user's natural language query

    Returns:
        Tuple of (mode, reason, confidence)
    """
    classifier = QueryClassifier()
    mode, reason = classifier.classify(query)
    confidence = classifier.get_confidence(query, mode)
    return (mode, reason, confidence)


def auto_query(
    question: str,
    as_of: str = None,
    include_history: bool = False,
    k: int = 10,
) -> dict:
    """
    Execute a query with automatic mode selection.

    This function classifies the query and routes to the appropriate
    retrieval mode without requiring the user to specify one.

    Args:
        question: The user's query
        as_of: Optional timestamp for historical query
        include_history: Whether to include superseded facts
        k: Number of results to retrieve

    Returns:
        Dictionary with results and metadata
    """
    from src.retrieval.hybrid import query

    # Classify the query
    mode, reason, confidence = classify_query(question)

    # Execute with auto-selected mode
    result = query(
        question=question, mode=mode, as_of=as_of, include_history=include_history, k=k
    )

    return {
        "question": question,
        "auto_mode": mode,
        "classification_reason": reason,
        "classification_confidence": confidence,
        "results": result,
    }


# Test function
if __name__ == "__main__":
    test_queries = [
        "Who is the CEO of Microsoft?",
        "What does the policy say about remote work?",
        "Validate this claim about Acme Corp",
        "List all invoices from 2024",
        "What changed in the company?",
        "Summarize the financial report",
        "When was the contract updated?",
    ]

    classifier = QueryClassifier()

    print("Query Classification Test")
    print("=" * 60)

    for query in test_queries:
        mode, reason = classifier.classify(query)
        confidence = classifier.get_confidence(query, mode)
        print(f"\nQuery: '{query}'")
        print(f"  Mode: {mode}")
        print(f"  Reason: {reason}")
        print(f"  Confidence: {confidence:.2f}")
