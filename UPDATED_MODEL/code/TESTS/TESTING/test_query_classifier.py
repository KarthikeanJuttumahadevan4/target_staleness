"""
Tests for the Query Classifier module.
"""

import pytest
from src.classification.query_classifier import (
    QueryClassifier,
    classify_query,
    auto_query,
)


class TestQueryClassifier:
    """Test the query classification logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = QueryClassifier()

    def test_entity_query_classifies_to_kg(self):
        """Entity questions should use KG-only."""
        queries = [
            "Who is the CEO of Microsoft?",
            "What is the name of the president?",
            "Where is the headquarters?",
            "Which company owns this?",
        ]

        for query in queries:
            mode, reason = self.classifier.classify(query)
            assert mode == "kg_only", f"'{query}' should be kg_only"

    def test_content_query_classifies_to_rag(self):
        """Content/fact queries should use Pure RAG."""
        queries = [
            "What does the policy say?",
            "Summarize the report",
            "Explain the process",
            "Describe the framework",
            "How to file taxes?",
        ]

        for query in queries:
            mode, reason = self.classifier.classify(query)
            assert mode == "pure_rag", f"'{query}' should be pure_rag"

    def test_complex_query_classifies_to_hybrid(self):
        """Complex/validation queries should use RAG+KG."""
        queries = [
            "Validate this claim",
            "Check if the information is correct",
            "What changed in 2024?",
            "What was updated?",
            "Compare with previous version",
        ]

        for query in queries:
            mode, reason = self.classifier.classify(query)
            assert mode == "rag_kg_validator", f"'{query}' should be hybrid"

    def test_temporal_query_classifies_to_hybrid(self):
        """Temporal queries should use RAG+KG."""
        queries = [
            "What was the policy in 2020?",
            "List invoices from January 2024",
            "What happened last year?",
        ]

        for query in queries:
            mode, reason = self.classifier.classify(query)
            assert mode == "rag_kg_validator", f"'{query}' should be hybrid"

    def test_confidence_calculation(self):
        """Confidence should increase with pattern matches."""
        high_confidence_query = "Who is the CEO of Microsoft?"
        low_confidence_query = "Tell me something"

        mode1, _ = self.classifier.classify(high_confidence_query)
        conf1 = self.classifier.get_confidence(high_confidence_query, mode1)

        mode2, _ = self.classifier.classify(low_confidence_query)
        conf2 = self.classifier.get_confidence(low_confidence_query, mode2)

        assert conf1 > conf2, "High match count should have higher confidence"

    def test_classify_query_function(self):
        """Test the convenience function."""
        mode, reason, confidence = classify_query("Who is the CEO?")

        assert mode == "kg_only"
        assert isinstance(reason, str)
        assert 0.0 <= confidence <= 1.0


class TestAutoQuery:
    """Test the auto-query functionality."""

    def test_auto_query_returns_proper_structure(self):
        """Auto query should return proper result structure."""
        # Note: This will fail if database isn't available
        # We're just testing the structure
        try:
            result = auto_query("Who is the CEO?", k=5)

            assert "question" in result
            assert "auto_mode" in result
            assert "classification_reason" in result
            assert "classification_confidence" in result
            assert "results" in result

            assert result["question"] == "Who is the CEO?"
            assert result["auto_mode"] == "kg_only"

        except ImportError:
            pytest.skip("src.retrieval.hybrid not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
