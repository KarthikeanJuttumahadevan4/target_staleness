# 03_Coding_Implementation_Plan

## Phase 0 — Foundation (1 day)
- Set up `uv` project; verify offline deps (Tesseract, FFmpeg).
- Reuse `extract.py`: move into `src/temporal/timestamp_extractor.py`; expose `get_as_of(path)` and `get_mtime(path)`. Improve for audio/video MOD dates.
- Confirm `.env` loads OpenAI gateway URL/key.
- Smoke test: ingest 1 txt file → Graphiti episode.

## Phase 1 — Intake + Format Routing (2 days)
- Implement `src/intake/watcher.py` (watchdog) → SQLite job queue.
- Implement `src/intake/router.py` (MIME + ext) → handler selection.
- Archive extractor: extract ZIP/TAR depth-limited (3), enqueue children.
- Output: `IntakeResult`.

## Phase 2 — Multi-Path Extraction (3 days)
- Text extractor: `Docling DocumentConverter` wrapper (`src/extraction/text.py`).
- Table extractor: Docling table structure model (`src/extraction/tables.py`).
- VLM trigger conditions + call (Qwen2.5-VL via local vLLM; fallback GPT-4o
  via gateway) (`src/extraction/vlm.py`).
- Audio path: `docling` ASR (Whisper small) + timestamps.
- Video path: frame extraction @1fps scene-change + Whisper.
- OCR fallback for PDF <80 chars: Tesseract.
- Output: `NormalizedExtract`.

## Phase 3 — Temporal Reconstruction (3 days)
- Integrate Graphiti + Neo4j.
- Integrate Semantica `merge_entities=True` (LLM fuzzy).
- Conflict Resolver using Graphiti + RAGBrain supersession.
- Implement RAGBrain audit (system-time replay).
- Retain superseded facts; create audit nodes.

## Phase 4 — Hierarchical Indexing (2 days)
- HiRAG community summary generation (1 layer).
- Persist summary nodes in Graphiti.
- Index current facts in Qdrant with `current=true`, `as_of`, `source`, `extraction_path`, `model` metadata.

## Phase 5 — Hybrid Retrieval (3 days)
- Mode A: Qdrant vector search with `current=true` filter.
- Mode B: Vector → KG current-flag check → RRF fusion → RAGBrain checked generation.
- Mode C: Neo4j graph traversal with `current=true` predicate + optional HiRAG expansion.
- Add `as_of` + `include_history` params.

## Phase 6 — Answer Generation (2 days)
- DSPy signature `AnswerGenerator` w/ provenance instructions.
- Citation builder (source, page, bbox, as_of, model).
- Confidence score via ms-marco-MiniLM rerank.
- FastAPI endpoints `/query`, `/health`, `/ready`.

## Phase 7 — Audit & Security (2 days)
- Append-only audit log (JSONL, SHA-256 hashes).
- Redaction gate before LLM gateway (strip PII/classified fields per config).
- Access logging for queries.

## Phase 8 — Testing & Hardening (3 days)
- Unit tests per module.
- Temporal correctness tests (provided test suite).
- Evaluation band metrics (precision/recall on samples5).
- Load test: 1000 facts query <3s.

## Timeline: ~18 working days for one FTE; ~7 days for 2 FTEs.

---

## Acceptance Criteria (per Proposal Success Criteria)
- [ ] System ingests `samples5/` and builds KG + vector index with timestamps.
- [ ] Adding a newer file with conflicting info flags old facts as superseded.
- [ ] All 3 retrieval modes return newest info by default.
- [ ] Answers include provenance + timestamp justification.
- [ ] Evaluation Band metrics met + temporal correctness tests pass.
- [ ] Air-gapped mode: smoke test without OpenAI key (uses dummy) still extracts.
