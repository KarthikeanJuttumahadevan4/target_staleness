"""
Temporal module for timestamp extraction and temporal KG operations.

This module provides:
- TimestampExtractor: Extracts as-of timestamps from file metadata
- TemporalKG: Neo4j-backed temporal knowledge graph
- Schema initialization for Neo4j
"""

from .timestamp_extractor import TimestampExtractor, get_as_of
from .temporal_kg import TemporalKG, init_schema
from .kg_schema import SCHEMA_STATEMENTS

__all__ = [
    "TimestampExtractor",
    "get_as_of",
    "TemporalKG",
    "init_schema",
    "SCHEMA_STATEMENTS",
]
