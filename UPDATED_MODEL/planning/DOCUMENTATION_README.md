# Temporal-Valid Knowledge Graph RAG System with Multi-Path Extraction

> **A production system for ingesting, versioning, and querying heterogeneous
> documents (PDF, Excel, Word, audio, video, archives) with bi-temporal
> knowledge graphs, hybrid retrieval, and military-grade audit trails.**

---

## 🎖️ Mission

Built for **military document intelligence** environments. Ingests field packets,
after-action reports, readiness reports, SOPs, equipment logs, comms transcripts,
and **tracks how facts change over time** with full provenance.

**Core principle:** Most-recent-wins + explicit flagging of outdated data.
Every fact carries:
- Provenance (source file, extraction path, model used)
- Temporal validity (as-of timestamp from file metadata, validity interval)
- Current / superseded flag (older versions retained for audit)

---

## 📁 Project Structure

```
mini-extract/
├── pyproject.toml              # uv-managed dependencies
├── uv.lock
├── .env.example                # LLM/VLM gateway config
├── main.py                      # FastAPI service entry point
├── extract.py                   # Legacy CLI shim
├── src/
│   ├── config/                 # ConfigManager (Pydantic)
│   ├── intake/                 # File watcher, queue, router
│   ├── extraction/             # Text, tables, VLM, audio, video, OCR
│   ├── temporal/               # timestamp_extractor (reuses extract.py)
│   ├── reconstruction/         # Entity resolution + conflict resolution
│   ├── indexing/               # Hierarchical indexing (HiRAG)
│   ├── retrieval/              # 3 retrieval modes
│   ├── generation/             # DSPy answer generation + citations
│   ├── audit/                  # Append-only audit log
│   ├── api/                    # FastAPI server
│   └── models/                 # Pydantic models
├── tests/                      # Temporal correctness + eval band tests
├── samples5/                   # Watched drop folder (input documents)
├── data/                       # Neo4j, Qdrant, SQLite, audit
├── 01_Proposal.md              # System proposal (root)
├── UPDATED_MODEL/
│   └── ARCHITECTURE/           # Technical design + plan + decisions
├── artifacts/                  # Specs, proposals, research
├── requirements.txt
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python ≥ 3.10
- `uv` (recommended) or pip
- System packages: `tesseract-ocr`, `ffmpeg`, `libgl1`, `poppler-utils`
- Neo4j 5.x (on-prem) and Qdrant (on-prem docker)

### Install

```bash
uv init
uv add graphiti-core ragbrain docling docling-graph qdrant-client neo4j \
        dspy sentence-transformers semantica watchgod python-dotenv
uv add -D pytest ruff
uv sync
```

### Configure `.env`

```bash
cp .env.example .env
# Edit:
#   OPENAI_API_KEY=...           (internal LLM gateway)
#   OPENAI_BASE_URL=http://llm-gateway.internal/v1
#   MODEL=gpt-4-turbo
#   VLM_MODEL=gpt-4o
#   NEO4J_URI=bolt://localhost:7687
#   QDRANT_URL=http://localhost:6333
```

### Run

```bash
# Service mode (HTTP API)
uv run python main.py --port 8000

# Legacy CLI shim
uv run python extract.py samples5/report.pdf
```

---

## 🔄 Pipeline Stages

```
Intake (watchdog) → Multi-path Extraction (Docling) → VLM Enrichment
→ Reconstruction (Graphiti + RAGBrain, Temporal KG) → Hierarchical Indexing
→ Hybrid Retrieval (3 modes) → Answer Generation (DSPy, checked)
```

### Document Coverage (15+ Formats)

| Category | Formats | Engine |
|----------|---------|--------|
| Text docs | PDF, DOCX, TXT, MD, RTF | Docling |
| Structured | XLSX, CSV, TSV, JSON, XML | Docling / AI-KE |
| Scanned PDFs | PDF (image) | Docling + Tesseract OCR |
| Audio | MP3, WAV, M4A, OGG | Docling (Whisper ASR) |
| Video | MP4, MOV, MKV, WEBM | Frame extraction + Whisper |
| Images / Diagrams | PNG, JPG, etc. | Qwen2.5-VL / GPT-4o VLM |
| Archives | ZIP, TAR.GZ | Auto-extracted (depth ≤3) |

---

## 🧠 Temporal Validity (Non-Negotiable)

Every extracted fact stores:
- `valid_at`, `invalid_at`, `created_at`, `expired_at` (bi-temporal)
- `current` (boolean flag)
- `source_file`, `extraction_path`, `model_used` (provenance)
- `superseded_by` (UUID link to newer fact, audit trail)

**Conflict resolution:** most-recent-wins. Newer fact promoted (`current=true`);
older demoted (`current=false`, `superseded_by=<new>`, `validity_end=<new as-of>`).
Full history retained for audit.

**Retrieval defaults** (all 3 modes): `current=true` only.
History accessible only via `as_of=<timestamp>` or `include_history=True`.

---

## 🎯 Three Retrieval Modes

| Mode | Description | Implementation |
|------|-------------|-----------------|
| **Pure RAG** | Vector search (current-only facts) | Qdrant + `current=true` filter |
| **RAG + KG Validator** | Vector hits → KG current check → RRF fusion → checked generation | Graphiti + RAGBrain |
| **KG-only** | Graph traversal (`current=true`) + optional hierarchy | Neo4j + HiRAG |

---

## 🔍 API Endpoints

```
POST /query
{
  "question": "...",
  "mode": "pure_rag" | "rag_kg_validator" | "kg_only",
  "as_of": "2024-06-01T00:00:00Z",       # null = most recent
  "include_history": false,
  "org_unit": null
}
→ { "answer", "facts": [...], "audit_id", "confidence" }

GET /health
GET /ready
```

**Citation format** (every answer):
```
Fact: <content>
Source: <file>, p.<n>
Extracted via: <path> (<model>)
As-of: <timestamp>
Confidence: <score>
```

---

## 📊 Evaluation & Test Bands

```bash
uv run pytest -q
```

Tests:
- `test_temporal_validity.py` — supersession correctness
- `test_conflict_resolver.py` — conflict handling
- `test_kg_schema.py` — schema validation
- `test_retrieval_temporal.py` — all 3 modes temporal
- `test_incremental_integration.py` — end-to-end ingest
- `test_timestamp_extractor.py` — `extract.py` reuse verification
- `test_evaluation_band.py` — metrics validation

**Targets:** Temporal correctness ≥95%, CFI ≥0.9, Hit@K ≥0.9, MRR ≥0.8,
query latency <3s (1000 facts).

---

## 🔐 Military-Grade Security Posture

- Air-gapped runtime; cloud APIs only via internal LLM gateway (keys redacted)
- No symlinks followed in `samples5/` (input confinement)
- Zip traversal disabled; archive-bomb limits (max 500MB, ratio ≤100:1)
- PII redaction at intake
- Classification-level + org_unit on every node
- Append-only hash-chained audit log (`data/audit.jsonl`)
- Query cache disabled by default (classified retention risk)

---

## 🛠️ Architecture & Planning

Detailed technical design, decisions, risks, and implementation plan in:
- `UPDATED_MODEL/ARCHITECTURE/00_README.md` — start here
- `UPDATED_MODEL/ARCHITECTURE/01_Technical_Design.md`
- `UPDATED_MODEL/ARCHITECTURE/08_Decisions_Log.md` — all Q&A decisions
- `UPDATED_MODEL/` (research + library assembly)
- `artifacts/` (proposal + specs)

---

## 📚 Key Dependencies

| Component | Library | License |
|-----------|---------|---------|
| KG Engine | Graphiti (Zep) | Apache 2.0 |
| Conflict Resolution | RAGBrain | Apache 2.0 |
| Multi-format Extraction | Docling (IBM) | MIT |
| VLM Enrichment | Docling-Graph | MIT |
| Form/Cert Extraction | Qwen2.5-VL-7B-SFT (HIT) | MIT / HF |
| Vector Store | Qdrant | Apache 2.0 |
| Graph DB | Neo4j | GPL/Commercial |
| LLM Orchestration | DSPy (Stanford) | MIT |
| Embeddings | all-mpnet-base-v2 (offline) | Apache 2.0 |

---

## 📜 License & Compliance

- Project code: MIT (see `LICENSE`)
- Compliance support: W3C PROV-O provenance; HIPAA/SOX/GDPR/FDA 21 CFR (via Semantica snapshots)
- Third-party licenses respected — see `UPDATED_MODEL/ARCHITECTURE/06_Model_Inventory.md`

---

## 🤝 Contributing

1. Fork → feature branch
2. Add tests for any new extractor/conflict rule
3. Run `uv run pytest` + `uv run ruff check .`
4. Submit PR

## 📞 Support

- Open issues for bugs/features
- Detailed docs in `UPDATED_MODEL/ARCHITECTURE/` and `artifacts/`
- Test data in `samples4/` and `samples5/`

---

**Version:** 2.0.0-alpha (Temporal KG-RAG rebuild)  
**Status:** Active Development (post-architecture-phase)
