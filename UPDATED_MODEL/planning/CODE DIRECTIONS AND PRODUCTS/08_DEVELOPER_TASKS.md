---
format: html
---

# 08_DEVELOPER_TASKS — Implementation Task List

## Phase 0 — Vendored environment
- [ ] DEV-00: Install system deps (tesseract, ffmpeg, libgl1, poppler-utils)
- [ ] DEV-01: `uv sync` (extend pyproject with graphiti-core, ragbrain, qdrant-client, neo4j, sentence-transformers, watchdog, python-magic, fastapi, uvicorn)
- [ ] DEV-02: Spin up Neo4j (on-prem) + Qdrant (docker)
- [ ] DEV-03: Create `.env` from example (no secrets committed)

## Phase 1 — Config + Models
- [ ] DEV-10: Create `src/config.py` (per scaffold)
- [ ] DEV-11: Create `src/models.py` (per interfaces doc)
- [ ] DEV-12: Unit tests importable (tests/test_config.py)

## Phase 2 — Temporal
- [ ] DEV-20: Improve `src/temporal/timestamp_extractor.py` (audio/video MOD)
- [ ] DEV-21: Create `src/temporal/kg_schema.py` (Cypher init)
- [ ] DEV-22: Create `src/temporal/temporal_kg.py` (Neo4j wrapper)
- [ ] DEV-23: Init schema on startup; idempotent

## Phase 3 — Intake
- [ ] DEV-30: Create `src/intake/queue.py`
- [ ] DEV-31: Create `src/intake/router.py`
- [ ] DEV-32: Create `src/intake/watcher.py`
- [ ] DEV-33: Single-file enqueue smoke test

## Phase 4 — Extraction
- [ ] DEV-40: `src/extraction/text.py` (docling)
- [ ] DEV-41: `src/extraction/tables.py`
- [ ] DEV-42: `src/extraction/ocr.py` (Tesseract + Paddle)
- [ ] DEV-43: `src/extraction/archives.py`
- [ ] DEV-44: `src/extraction/audio.py`
- [ ] DEV-45: `src/extraction/video.py`
- [ ] DEV-46: `src/extraction/dispatcher.py`
- [ ] DEV-47: Test all samples5 formats

## Phase 5 — Reconstruction
- [ ] DEV-50: `src/reconstruction/entity_resolver.py`
- [ ] DEV-51: `src/reconstruction/conflict_resolver.py`
- [ ] DEV-52: Wire Graphiti + RAGBrain supersession
- [ ] DEV-53: Temporal correctness test pass (tests/test_conflict_resolver.py)

## Phase 6 — Indexing
- [ ] DEV-60: `src/indexing/vector_indexer.py`
- [ ] DEV-61: `src/indexing/hierarchical.py`
- [ ] DEV-62: Qdrant init + ingest + mark stale

## Phase 7 — Retrieval
- [ ] DEV-70: `src/retrieval/pure_rag.py`
- [ ] DEV-71: `src/retrieval/rag_kg_validator.py`
- [ ] DEV-72: `src/retrieval/kg_only.py`
- [ ] DEV-73: `src/retrieval/hybrid.py`
- [ ] DEV-74: tests/test_retrieval_temporal.py pass

## Phase 8 — Generation
- [ ] DEV-80: `src/generation/answer_gen.py` (DSPy)
- [ ] DEV-81: `src/generation/citations.py`
- [ ] DEV-82: Checked generation + confidence

## Phase 9 — API + Main + Audit
- [ ] DEV-90: `src/api/server.py`
- [ ] DEV-91: `main.py`
- [ ] DEV-92: `src/audit/logger.py`
- [ ] DEV-93: `/health`, `/ready`, `/query` smoke
- [ ] DEV-94: Audit hash-chain verify

## Phase 10 — VLM + Hardening
- [ ] DEV-100: `src/extraction/vlm.py`
- [ ] DEV-101: Eval band run
- [ ] DEV-102: Latency benchmark <3s
- [ ] DEV-103: samples5 full ingest demo

## Definition of Done (engineering)
- [ ] `uv run pytest -q` green
- [ ] samples5 ingest succeeds (≥5 formats produce facts)
- [ ] Supersession demo end-to-end works
- [ ] All 3 modes return newest by default
- [ ] Answers cite provenance + timestamp
- [ ] Audit log hash-chained + append-only
- [ ] README links to ARCHITECTURE/
