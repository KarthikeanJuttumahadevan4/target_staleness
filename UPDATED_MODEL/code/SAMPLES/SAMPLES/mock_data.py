"""
Mock data setup for testing the UI without databases.

This creates sample facts that can be queried.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import RetrievedFact
import uuid


def create_mock_facts():
    """Create sample facts for testing."""
    facts = [
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
            source="SAMPLES/hybrid_extraction_guide.pdf",
            as_of="2024-02-01T00:00:00Z",
            current=True,
            confidence=0.93,
            citation="Introduction",
            extraction_path="text",
        ),
    ]
    return facts


def mock_retriever():
    """Mock retriever that returns sample facts."""
    from src.models import AnswerResponse
    import time

    facts = create_mock_facts()

    def query(question, mode="pure_rag", as_of=None, include_history=False, k=10):
        # Handle auto mode - convert to specific mode
        if mode == "auto":
            if any(
                word in question.lower()
                for word in ["who", "what is", "where", "which"]
            ):
                mode = "kg_only"
            elif any(
                word in question.lower()
                for word in ["summarize", "explain", "what does"]
            ):
                mode = "pure_rag"
            else:
                mode = "rag_kg_validator"
        # Simple keyword matching
        results = []
        question_lower = question.lower()

        for fact in facts:
            if not fact.current and not include_history:
                continue
            # Match based on keywords
            content_lower = fact.content.lower()
            if any(word in question_lower for word in ["acme", "supplier", "corp"]):
                results.append(facts[0])
            if any(
                word in question_lower
                for word in ["revenue", "financial", "report", "profit"]
            ):
                results.append(facts[1])
            if any(
                word in question_lower
                for word in ["contract", "beta", "signed", "services"]
            ):
                results.append(facts[2])
            if any(
                word in question_lower
                for word in ["ai", "targeting", "decision", "accuracy"]
            ):
                results.append(facts[3])
            if any(
                word in question_lower
                for word in ["hybrid", "llm", "extraction", "document"]
            ):
                results.append(facts[4])

        # Deduplicate
        seen_ids = set()
        unique = []
        for f in results:
            if f.fact_id not in seen_ids:
                seen_ids.add(f.fact_id)
                unique.append(f)

        return AnswerResponse(
            answer=f"Results for: {question}",
            facts=unique[:k],
            mode=mode,
            confidence=len(unique) / k if unique else 0.0,
            audit_id=f"audit_{int(time.time())}",
            supported_claims=[f.content for f in unique[:k]],
            unsupported_claims=[],
        )

    return query


if __name__ == "__main__":
    # Test the mock system
    query_func = mock_retriever()

    print("=== Mock Data System Test ===\n")

    test_queries = [
        "Who is the CEO?",
        "What is the revenue?",
        "What changed in 2024?",
        "hybrid extraction",
        "Summarize the financial report",
        "AI targeting results",
    ]

    for q in test_queries:
        result = query_func(q, mode="auto", k=5)
        print(f"Query: '{q}'")
        print(f"  Mode: {result.mode}")
        print(f"  Results: {len(result.facts)} facts")
        if result.facts:
            for fact in result.facts[:2]:
                print(f"    ✅ {fact.content[:50]}...")
        print()
