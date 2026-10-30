"""
Classification module for automatic query routing.
"""

from .query_classifier import (
    QueryClassifier,
    classify_query,
    auto_query,
)

__all__ = [
    "QueryClassifier",
    "classify_query",
    "auto_query",
]
