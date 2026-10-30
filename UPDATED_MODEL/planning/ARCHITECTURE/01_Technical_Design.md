# 01_Technical_Design — System Architecture

## 1. System Boundaries

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ENCLAVE (Air-Gapped)                          │
│                                                                       │
│  ┌──────────────┐    ┌────────────────────┐    ┌────────────────┐  │
│  │  samples5/   │──▶│  INTAKE + EXTRACTOR │──▶│  TEMPORAL KG    │  │
│  │  (files)     │    │  (docling, docling- │    │  (Neo4j)       │  │
│  │              │    │   graph, Tesseract, │    │  + Qdrant      │  │
│  └──────────────┘    │   Whisper)          │    │  (vectors)     │  │
│                      └────────────────────┘    └────────┬───────┘  │
│                                                        │           │
│                                              ┌─────────┴──────┐    │
│                                              │  RETRIEVAL SVC │    │
│                                              │  (3 modes)     │    │
│                                              └─────────┬──────┘    │
│                                                        │           │
│                                              ┌─────────┴──────┐    │
│                                              │  LLM GATEWAY   │    │
│                                              │  (OpenAI API /  │    │
│                                              │   internal)     │    │
│                                              └─────────────────┘    │
│                                                                       │
│  File watching → watching os event → enqueue job → extract facts      │
└─────────────────────────────────────────────────────────────────────┘
```

External boundary: **only data → LLM gateway**; never raw files. Internal enclave
must have Neo4j + Qdrant + docling + Whisper + Tesseract (offline-installable
packages).

---

## 2. Major Components

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| **IntakeWatcher** | Detects new/modified files in `samples5/` | `watchdog` |
| **FormatRouter** | MIME/ext → handler | `python-magic` |
| **ExtractorDispatcher** | Runs all extraction paths | Docling + Semantica |
| **VCaptionService** | Visual (charts/diagrams/forms) → facts | Qwen2.5-VL-7B-SFT (on-prem) / Docling-Graph |
| **TemporalKG** | Stores entities/relations with temporal props | Neo4j (via Graphiti) |
| **ConflictResolver** | Detects + resolves supersession | Graphiti + RAGBrain |
| **VectorIndex** | Embeds facts for vector search | Qdrant |
| **HybridRetriever** | 3 retrieval modes | Graphiti + RAGBrain + HiRAG |
| **AnswerGenerator** | LLM answer w/ checked generation | DSPy + OpenAI gateway |
| **AuditLogger** | Immutable ingestion + query audit | Append-only JSONL + Qdrant metadata |
| **ConfigManager** | `.env` + YAML config | python-dotenv + Pydantic |

---

## 3. Data Flow (Detailed)

### Step 1 — Intake
`IntakeWatcher` emits `FileEvent(path, event_type, mtime)` → queue.

### Step 2 — Format Routing
- Archives: extract via `zipfile`, recurse (auto, depth-limited 3 levels).
- Audio: `docling.DocumentConverter` (ASR) — synchronous offline.
- Video: frame extraction @1fps (scene-change preferred) + audio → Whisper.
- PDFs: Docling (native text → if `<80 chars`, Tesseract OCR fallback).
- Office: Docling (xlsx/docx/pptx).

### Step 3 — Multi-Path Extraction (Deterministic → VLM)
1. **Text path** (always): library extractors
2. **Table path** (always if structured): Docling's table model
3. **VLM path** (conditional): only if image regions detected by layout
   analyzer, OR if PDF <80 chars, OR if form fields present.
4. **Audio/Video path**: ASR → text → treat as document.

Output: `NormalizedExtract(doc_id, source_path, valid_at, chunks[], entities[], relations[])`.

### Step 4 — Reconstruction (Temporal KG)
```
NormalizedExtract
  → Semantica merge_entities (fuzzy match)
  → Graphiti.add_episode(content, source, valid_at, valid_at, metadata)
  → Conflict detection (entity id + predicate match)
  → If newer: supersede old fact (invalid_at=now, superseded_by=new_id)
  → Create AUDIT node
  → Create vectors in Qdrant (current=true metadata)
  → Hierarchical indexing (HiRAG community summaries)
```

### Step 5 — Retrieval (3 modes)
All read `current=true` by default; `as_of` overrides.

### Step 6 — Answer Generation
DSPy `Predict(AnswerGenerator)` over retrieved facts → checked generation →
citations → stdout + audit log.

---

## 4. Interfaces

### Intake → Extractor
```python
class IntakeResult(BaseModel):
    doc_id: UUID
    source_path: str
    valid_at: datetime          # from extract.py (mtime fallback to ingest time)
    ingest_method: str          # "text"|"ocr"|"audio"|"video"|"vlm"|"table"
    text: str
    entities: list[Entity]
    relations: list[Relation]
    metadata: dict
```

### Extractor → KG
```python
graphiti.add_episode(
    name=source_filename,
    episode_body=text,
    source=EpisodeType.text,
    source_description="military field doc",
    reference_time=valid_at,       # ← temporal authority from extract.py
    content_hash=sha256,
    metadata={"model": "docling:2.x", "extraction_path": ingest_method}
)
```

### KG → Retrieval
```python
class RetrievedFact(BaseModel):
    fact_id: UUID
    content: str
    source: str
    as_of: datetime
    current: bool
    confidence: float
    citation: str
```

### Query API (internal)
```python
POST /query
{
  "question": "...",
  "mode": "pure_rag" | "rag_kg_validator" | "kg_only",
  "as_of": "2024-06-01T00:00:00Z" | null,   # null = most recent
  "include_history": bool,
  "org_unit": "optional scoped filter"
}
→ { "answer": str, "facts": [RetrievedFact], "audit_id": UUID }
```

---

## 5. Dependencies (Locked)

### Python Core
```
python >= 3.10
graphiti-core >= 0.5
ragbrain >= latest
docling[asr,tesserocr]
docling-graph
qdrant-client
neo4j-driver
sentence-transformers (all-mpnet-base-v2, offline)
ms-marco-MiniLM-L-6-v2 (reranker)
dspy
semantica
python-dotenv
watchdog
pydantic >= 2
```

### System (Offline-Installable)
```
tesseract-ocr
tesseract-ocr-eng
ffmpeg
libgl1
poppler-utils
```

### Cloud-Optional (Gateway Only)
- OpenAI API key (gpt-4o for VLM; gpt-4-turbo for answer gen)
- Internal gateway handles auth; no keys in repo.

---

## 6. Simplest Architecture Choice (Deliberate)

- **No message queue** (Redis/RabbitMQ) — SQLite job queue (single-writer).
- **No separate OCR microservice** — Docling in-process.
- **No microservices** — single Python process (FastAPI) with Neo4j/Qdrant as external deps.
- **Graphiti native** handling of episodes/events (avoid building custom temporal logic).
- **Deterministic ordering**: graph DB transactional, no race.

Rationale: military deployments favor minimal moving parts; speed of validation
over distributed complexity.
