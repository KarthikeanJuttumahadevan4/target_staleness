"""
Pydantic models for data validation and serialization.

This module defines all the data models used throughout the Temporal-Valid
Knowledge Graph RAG System. These models ensure type safety and provide
clear contracts between components.

All models are designed to be JSON-serializable for API responses and
database storage.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Literal, Optional, List, Dict, Any

from pydantic import BaseModel, Field


# Type aliases for clarity
ModeType = Literal["pure_rag", "rag_kg_validator", "kg_only"]
IngestMethod = Literal["text", "ocr", "table", "vlm", "audio", "video", "archive"]
ConfidenceLevel = Literal["high", "medium", "low"]


class NormalizedExtract(BaseModel):
    """
    Normalized document extraction result.

    This is the output of the multi-path extraction pipeline, containing
    all extracted text, entities, and relationships with temporal metadata.

    Attributes:
        doc_id: Unique document identifier (UUID4)
        source_path: Original file path
        valid_at: ISO-8601 timestamp when this extraction is valid from
        ingest_method: Which extraction path was used
        text: Extracted text content
        entities: List of extracted entities (person, org, concept, etc.)
        relations: List of extracted relationships between entities
        metadata: Additional extraction metadata
        model_used: Name of the model used for extraction
        confidence: Confidence score of the extraction (0.0-1.0)
    """

    doc_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_path: str
    valid_at: str  # ISO-8601 UTC
    ingest_method: str  # text|ocr|table|vlm|audio|video|archive
    text: str
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    relations: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    model_used: str = "docling"
    confidence: float = 1.0


class Fact(BaseModel):
    """
    A fact stored in the temporal knowledge graph.

    Facts are the atomic units of knowledge, with full temporal and
    provenance metadata. They support bi-temporal querying and
    supersession relationships.

    Attributes:
        fact_id: Unique fact identifier
        content: The fact content (text)
        entity_id: Canonical entity identifier (after resolution)
        predicate: Relationship type (e.g., "CEO_OF", "WORKS_AT")
        object_value: Optional object value for the predicate
        valid_at: When this fact became true in the world
        invalid_at: When this fact became invalid (superseded)
        created_at: When this fact was ingested into the system
        expired_at: When the system recorded this as expired
        source_file: Original document that contained this fact
        extraction_path: How this fact was extracted (text/ocr/vlm/etc)
        model_used: Which model extracted this fact
        current: Whether this fact is currently valid (not superseded)
        confidence: Confidence score of the fact
        embedding_id: Qdrant point ID for vector search
        superseded_by: Fact ID that superseded this one (if any)
    """

    fact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    entity_id: str
    predicate: str
    object_value: Optional[str] = None
    valid_at: str
    invalid_at: Optional[str] = None
    created_at: str
    expired_at: Optional[str] = None
    source_file: str
    extraction_path: str
    model_used: str
    current: bool = True
    confidence: float = 1.0
    embedding_id: Optional[str] = None
    superseded_by: Optional[str] = None


class RetrievedFact(BaseModel):
    """
    A fact returned by the retrieval system.

    Includes all provenance and citation information needed to ground
    the LLM's answer.
    """

    fact_id: str
    content: str
    source: str
    as_of: str
    current: bool
    confidence: float
    citation: str
    extraction_path: Optional[str] = None
    model_used: Optional[str] = None


class AnswerResponse(BaseModel):
    """
    Response from the answer generation endpoint.

    Contains the generated answer with full citation information,
    confidence scores, and audit trail reference.
    """

    answer: str
    facts: List[RetrievedFact]
    mode: ModeType
    confidence: float = 0.0
    audit_id: str
    supported_claims: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)


class QueryRequest(BaseModel):
    """
    Request model for the /query endpoint.

    Supports all three retrieval modes and temporal queries.
    """

    question: str
    mode: ModeType = "pure_rag"
    as_of: Optional[str] = None  # ISO-8601 timestamp for historical query
    include_history: bool = False
    org_unit: Optional[str] = None  # For multi-tenancy scoping
    k: int = 10  # Number of results to retrieve


class ReconciliationResult(BaseModel):
    """
    Result of conflict detection between facts.

    Used by the conflict resolver to determine whether a new fact
    supersedes an existing one.
    """

    action: Literal["keep", "supersede"]
    superseded_fact_id: Optional[str] = None
    reason: str = ""


class IngestionResult(BaseModel):
    """
    Result of ingesting a single document.
    """

    doc_id: str
    status: Literal["success", "partial", "failed"]
    error: Optional[str] = None
    facts_created: int = 0
    entities_created: int = 0
    processing_time_ms: int = 0
    ingest_method: str
    valid_at: str
