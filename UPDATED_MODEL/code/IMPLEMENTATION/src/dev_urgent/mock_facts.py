"""
Mock Fact Store - Bypasses the full ingestion pipeline.
Provides hardcoded facts for immediate testing.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class MockFact(BaseModel):
    """Simplified fact model matching RetrievedFact structure."""

    fact_id: str
    content: str
    source: str
    as_of: datetime
    current: bool = True
    confidence: float = 0.95
    citation: str = ""
    entity_id: str = None
    predicate: str = None
    object_value: str = None


class MockFactStore:
    """In-memory store of mock facts."""

    def __init__(self):
        self.facts: List[MockFact] = []
        self._initialize_facts()

    def _initialize_facts(self):
        """Create hardcoded facts for demo."""
        self.facts = [
            MockFact(
                fact_id="fact_001",
                content="Operation Alpha has status APPROVED",
                source="document_1.pdf",
                as_of=datetime(2024, 1, 15, 10, 0, 0),
                current=True,
                confidence=0.95,
                citation="Source: document_1.pdf, p.1 | Extracted: text (docling) | As-of: 2024-01-15T10:00:00Z",
                entity_id="operation_alpha",
                predicate="status",
                object_value="APPROVED",
            ),
            MockFact(
                fact_id="fact_002",
                content="Operation Alpha budget is $500,000",
                source="document_1.pdf",
                as_of=datetime(2024, 1, 15, 10, 0, 0),
                current=True,
                confidence=0.90,
                citation="Source: document_1.pdf, p.2 | Extracted: text (docling) | As-of: 2024-01-15T10:00:00Z",
                entity_id="operation_alpha",
                predicate="budget",
                object_value="$500,000",
            ),
            MockFact(
                fact_id="fact_003",
                content="Operation Beta has status PENDING",
                source="document_2.pdf",
                as_of=datetime(2024, 1, 10, 8, 0, 0),
                current=True,
                confidence=0.85,
                citation="Source: document_2.pdf, p.1 | Extracted: text (docling) | As-of: 2024-01-10T08:00:00Z",
                entity_id="operation_beta",
                predicate="status",
                object_value="PENDING",
            ),
            MockFact(
                fact_id="fact_004",
                content="The commander of operation Alpha is Captain Smith",
                source="document_1.pdf",
                as_of=datetime(2024, 1, 15, 10, 0, 0),
                current=True,
                confidence=0.92,
                citation="Source: document_1.pdf, p.1 | Extracted: text (docling) | As-of: 2024-01-15T10:00:00Z",
                entity_id="operation_alpha",
                predicate="commander",
                object_value="Captain Smith",
            ),
            MockFact(
                fact_id="fact_005",
                content="Operation Alpha is scheduled to begin on March 1, 2024",
                source="document_1.pdf",
                as_of=datetime(2024, 1, 15, 10, 0, 0),
                current=True,
                confidence=0.88,
                citation="Source: document_1.pdf, p.3 | Extracted: text (docling) | As-of: 2024-01-15T10:00:00Z",
                entity_id="operation_alpha",
                predicate="start_date",
                object_value="2024-03-01",
            ),
        ]

    def search(
        self,
        query: str,
        as_of: Optional[datetime] = None,
        mode: str = None,
        limit: int = 5,
    ) -> List[MockFact]:
        """
        Search mock facts by query.
        Simple keyword matching for demo purposes.
        """
        query_lower = query.lower()

        # Filter by temporal constraints
        if as_of:
            results = [f for f in self.facts if f.current and f.as_of <= as_of]
        else:
            results = [f for f in self.facts if f.current]

        # Simple keyword matching
        matched = []
        for fact in results:
            if query_lower in fact.content.lower():
                matched.append(fact)

        # If no matches, return top facts
        if not matched:
            matched = results[:limit]

        return matched[:limit]

    def get_current_facts(self, entity_id: str = None) -> List[MockFact]:
        """Get all current facts, optionally filtered by entity."""
        results = [f for f in self.facts if f.current]
        if entity_id:
            results = [f for f in results if f.entity_id == entity_id]
        return results


# Global singleton
mock_fact_store = MockFactStore()
