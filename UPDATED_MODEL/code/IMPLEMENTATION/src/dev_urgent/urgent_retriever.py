"""
Urgent Retriever - Uses mock facts instead of real KG/Qdrant.
Bypasses the full pipeline for immediate testing.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from UPDATED_MODEL.IMPLEMENTATION.src.dev_urgent.mock_facts import mock_fact_store


class UrgentRetriever:
    """Temporary retrieval using mock facts - bypasses databases."""

    def __init__(self):
        self.fact_store = mock_fact_store

    def search(
        self,
        query: str,
        as_of: Optional[datetime] = None,
        mode: Optional[str] = None,
        limit: int = 5,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Search mock facts and return in expected format.
        Format matches what the system expects for RetrievedFact.
        """
        facts = self.fact_store.search(query, as_of, mode, limit)

        # Convert to dict format expected by the system
        results = []
        for fact in facts:
            fact_dict = fact.model_dump()
            # Ensure datetime is string for JSON serialization
            if isinstance(fact_dict.get("as_of"), datetime):
                fact_dict["as_of"] = fact_dict["as_of"].isoformat() + "Z"
            results.append(fact_dict)

        return results

    def get_current_facts(self, entity_id: str = None) -> List[Dict[str, Any]]:
        """Get current facts by entity."""
        facts = self.fact_store.get_current_facts(entity_id)
        results = []
        for fact in facts:
            fact_dict = fact.model_dump()
            if isinstance(fact_dict.get("as_of"), datetime):
                fact_dict["as_of"] = fact_dict["as_of"].isoformat() + "Z"
            results.append(fact_dict)
        return results


# Global instance
urgent_retriever = UrgentRetriever()
