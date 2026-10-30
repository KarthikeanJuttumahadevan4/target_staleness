"""
Data Setup Script for Temporal-Valid KG RAG System
====================================================

This script sets up mock data for testing when databases are not available.
It patches the retrieval functions to return sample results.

Usage:
    python3 SAMPLES/setup_data.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import RetrievedFact, AnswerResponse
import uuid
import time


# Sample facts for testing
MOCK_FACTS = [
    RetrievedFact(
        fact_id=str(uuid.uuid4()),
        content="Acme Corp is a major supplier in the supply chain with annual revenue of $2.5M",
        source="SAMPLES/invoice_1.pdf",
        as_of="2024-01-15T10:00:00Z",
        current=True,
        confidence=0.95,
        citation="Invoice 1, Page 2",
        extraction_path="text",
    ),
    RetrievedFact(
        fact_id=str(uuid.uuid4()),
        content="The Q3 2024 financial report shows revenue of $5.2M and profit of $1.1M",
        source="SAMPLES/reports/Q3-2024-Financial-Report.pdf",
        as_of="2024-01-10T00:00:00Z",
        current=True,
        confidence=0.92,
        citation="Page 5",
        extraction_path="text",
    ),
    RetrievedFact(
        fact_id=str(uuid.uuid4()),
        content="The contract with Beta Supplies was signed on 2024-09-15 for $500K services",
        source="SAMPLES/contracts/NDA-AcmeCorp-2024.docx",
        as_of="2024-09-15T00:00:00Z",
        current=True,
        confidence=0.88,
        citation="Section 1",
        extraction_path="text",
    ),
    RetrievedFact(
        fact_id=str(uuid.uuid4()),
        content="AI-enabled targeting improves decision support accuracy by 35%",
        source="SAMPLES/AI + Human + JTC + Independent Study.pdf",
        as_of="2024-01-01T00:00:00Z",
        current=True,
        confidence=0.90,
        citation="Page 3, Results Section",
        extraction_path="text",
    ),
    RetrievedFact(
        fact_id=str(uuid.uuid4()),
        content="Hybrid LLM extraction combines text, OCR, and VLM for comprehensive document analysis",
        source="SAMPLES/hybrid_extraction_notes.txt",
        as_of="2024-02-01T00:00:00Z",
        current=True,
        confidence=0.93,
        citation="Introduction",
        extraction_path="text",
    ),
]


def setup_mock_retrieval():
    """Setup mock retrieval functions that return sample data."""

    def mock_query(question, mode="pure_rag", as_of=None, include_history=False, k=10):
        """Mock query function that returns sample facts."""

        # Handle auto mode - convert to specific mode
        if mode == "auto":
            if any(
                word in question.lower()
                for word in ["who", "what is", "where", "which", "name of"]
            ):
                mode = "kg_only"
            elif any(
                word in question.lower()
                for word in ["summarize", "explain", "what does", "describe"]
            ):
                mode = "pure_rag"
            else:
                mode = "rag_kg_validator"

        # Simple keyword matching
        results = []
        question_lower = question.lower()

        for fact in MOCK_FACTS:
            if not fact.current and not include_history:
                continue

            content_lower = fact.content.lower()
            # Match based on keywords
            if any(
                word in question_lower
                for word in ["acme", "supplier", "corp", "company"]
            ):
                if MOCK_FACTS[0] not in results:
                    results.append(MOCK_FACTS[0])
            if any(
                word in question_lower
                for word in ["revenue", "financial", "report", "profit", "money"]
            ):
                if MOCK_FACTS[1] not in results:
                    results.append(MOCK_FACTS[1])
            if any(
                word in question_lower
                for word in ["contract", "beta", "signed", "services", "nda"]
            ):
                if MOCK_FACTS[2] not in results:
                    results.append(MOCK_FACTS[2])
            if any(
                word in question_lower
                for word in [
                    "ai",
                    "artificial",
                    "targeting",
                    "decision",
                    "accuracy",
                    "improve",
                ]
            ):
                if MOCK_FACTS[3] not in results:
                    results.append(MOCK_FACTS[3])
            if any(
                word in question_lower
                for word in ["hybrid", "llm", "extraction", "document", "process"]
            ):
                if MOCK_FACTS[4] not in results:
                    results.append(MOCK_FACTS[4])

        return AnswerResponse(
            answer=f"Results for: {question}",
            facts=results[:k],
            mode=mode,
            confidence=len(results) / k if results else 0.0,
            audit_id=f"audit_{int(time.time())}",
            supported_claims=[f.content for f in results[:k]],
            unsupported_claims=[],
        )

    # Patch the retrieval functions
    import src.retrieval.pure_rag as pure_rag
    import src.retrieval.rag_kg_validator as rag_kg_validator
    import src.retrieval.kg_only as kg_only
    import src.retrieval.hybrid as hybrid

    # Replace functions
    pure_rag.pure_rag = mock_query
    rag_kg_validator.rag_kg_validator = mock_query
    kg_only.kg_only = lambda q, hops=2, as_of=None, current_only=True: mock_query(
        q, mode="kg_only", as_of=as_of, include_history=not current_only, k=hops
    )
    hybrid.query = mock_query

    print("✅ Mock data system installed!")
    print(f"   {len(MOCK_FACTS)} sample facts available")
    print("   Query function patched to return mock data")

    return mock_query


def test_queries():
    """Test sample queries."""
    query = setup_mock_retrieval()

    print("\n=== Sample Queries ===")

    test_queries = [
        ("Who is the CEO?", "kg_only"),
        ("What is the revenue?", "kg_only"),
        ("What changed in 2024?", "rag_kg_validator"),
        ("hybrid extraction", "rag_kg_validator"),
        ("Summarize the financial report", "pure_rag"),
        ("AI targeting results", "rag_kg_validator"),
    ]

    for q, expected_mode in test_queries:
        result = query(q, mode="auto", k=5)
        print(f"\nQuery: '{q}'")
        print(f"  Mode: {result.mode}")
        print(f"  Results: {len(result.facts)} facts")
        if result.facts:
            for fact in result.facts[:2]:
                print(f"    ✅ {fact.content[:60]}... [conf: {fact.confidence:.2f}]")
                print(f"       Source: {fact.source}")
        else:
            print("    ⚠️ No facts found")


if __name__ == "__main__":
    test_queries()
