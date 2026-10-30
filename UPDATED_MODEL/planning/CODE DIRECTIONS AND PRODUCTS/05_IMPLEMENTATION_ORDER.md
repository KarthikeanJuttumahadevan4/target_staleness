# 05_IMPLEMENTATION_ORDER — Dependency-Ordered Task List

## Step 0 — Vendored environment (Day 0)
- Install system: tesseract, ffmpeg, libgl1, poppler-utils.
- `uv sync` from pyproject (extended with graphiti-core, ragbrain, qdrant-client, neo4j, sentence-transformers, watchdog, python-magic, fastapi, uvicorn).
- Verify offline packages importable.

## Step 1 — Config + models (P0)
- Create `src/config.py`, `src/models.py` from `03_INTERFACES_MODELS.md`.
- Test: importable; settings load from `.env`.

## Step 2 — Temporal (P0)
- Move/reuse `extract.py` logic into `src/temporal/timestamp_extractor.py` (already exists, improve).
- Create `src/temporal/kg_schema.py`, `src/temporal/temporal_kg.py`.

## Step 3 — Neo4j schema init (P0)
- `src/temporal/kg_schema.init_schema(driver)` runs on startup; idempotent.

## Step 4 — Intake + queue + router (P0)
- `src/intake/{queue,router,watcher}.py`.
- Test single-file enqueue.

## Step 5 — Extraction (P0)
- text, tables, ocr, archives; wire dispatcher.
- Test samples5 formats produce NormalizedExtract.

## Step 6 — Reconstruction (P0)
- `src/reconstruction/{entity_resolver, conflict_resolver}.py`.
- Wire into TemporalKG via Graphiti + RAGBrain.
- Test supersession.

## Step 7 — Vector indexing (P1)
- `src/indexing/{vector_indexer, hierarchical}.py`.
- Qdrant init; ingest facts; mark stale.

## Step 8 — Retrieval (P1)
- `pure_rag`, `rag_kg_validator`, `kg_only`, `hybrid`.

## Step 9 — Generation (P1)
- DSPy `AnswerGenerator` + citations + confidence.

## Step 10 — API + main (P2)
- `src/api/server.py`, `main.py`.

## Step 11 — Audit (P2)
- `src/audit/logger.py` hash-chain.

## Step 12 — VLM enrichment (P2, parallelisable)
- `src/extraction/vlm.py`; conditional triggers.

## Step 13 — Hardening + tests (gate)
- Run `tests/`; eval band; latency benchmark.

## Dependency graph (summary)
```
config, models → temporal → intake → extraction → reconstruction
  → indexing → retrieval → generation → api/main
  audit ← (cross-cuts intake + retrieval + generation)
  vlm ← (extraction path, parallel)
```
Each arrow is a hard dependency; do not skip order without tech lead OK.
