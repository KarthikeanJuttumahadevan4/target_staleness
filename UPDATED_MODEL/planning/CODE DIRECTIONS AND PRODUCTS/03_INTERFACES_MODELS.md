---
format: html
---

# 03_INTERFACES_MODELS — Copy-Paste Pydantic Models

> Place in `src/models.py` (or `src/models/__init__.py`). All module IO uses these.
> Reuses existing `RetrievedFact` shape from `ARCHITECTURE/01_Technical_Design §4`.

```python
from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field
import uuid

ModeType = Literal["pure_rag", "rag_kg_validator", "kg_only"]

class NormalizedExtract(BaseModel):
    doc_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_path: str
    valid_at: str  # ISO-8601 UTC
    ingest_method: str  # text|ocr|table|vlm|audio|video|archive
    text: str
    entities: list[dict] = Field(default_factory=list)
    relations: list[dict] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    model_used: str = "docling"
    confidence: float = 1.0

class Fact(BaseModel):
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
    answer: str
    facts: list[RetrievedFact]
    mode: ModeType
    confidence: float = 0.0
    audit_id: str
    supported_claims: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)

class QueryRequest(BaseModel):
    question: str
    mode: ModeType = "pure_rag"
    as_of: Optional[str] = None
    include_history: bool = False
    org_unit: Optional[str] = None
    k: int = 10
```

## Enum for conflict resolution
```python
class ReconciliationResult(BaseModel):
    action: Literal["keep", "supersede"]
    superseded_fact_id: Optional[str] = None
    reason: str = ""
```

## Database schema init (Cypher) — copy into `src/temporal/kg_schema.py`
```python
SCHEMA_STATEMENTS = [
    "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE",
    "CREATE CONSTRAINT fact_id_unique IF NOT EXISTS FOR (f:Fact) REQUIRE f.fact_id IS UNIQUE",
    "CREATE INDEX fact_current IF NOT EXISTS FOR (f:Fact) ON (f.current)",
    "CREATE INDEX fact_valid_at IF NOT EXISTS FOR (f:Fact) ON (f.valid_at)",
    "CREATE INDEX fact_invalid_at IF NOT EXISTS FOR (f:Fact) ON (f.invalid_at)",
    "CREATE INDEX fact_entity IF NOT EXISTS FOR (f:Fact) ON (f.entity_id)",
    "CREATE INDEX fact_predicate IF NOT EXISTS FOR (f:Fact) ON (f.predicate)",
    "CREATE INDEX doc_source IF NOT EXISTS FOR (d:Document) ON (d.source_path)",
]
```

## Qdrant init (Python)
```python
from qdrant_client.models import (
    VectorParams, Distance, PayloadSchemaType
)

FACTS_COLLECTION = "facts"
VECTOR_DIM = 768
DISTANCE = Distance.COSINE

PAYLOAD_INDEXES = {
    "current": PayloadSchemaType.BOOL,
    "as_of": PayloadSchemaType.DATETIME,
    "entity_id": PayloadSchemaType.KEYWORD,
    "predicate": PayloadSchemaType.KEYWORD,
}
```
