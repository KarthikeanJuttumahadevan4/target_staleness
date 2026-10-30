---
format: html
---

# 02_MODULE_SPECS — Per-Module Developer Contract

> All paths relative to repo root. Python ≥3.10. Pydantic v2. All code thread-safe
> for FastAPI `Depends`. All timestamps UTC ISO-8601 with `Z`.

## A. `src/config.py` (config module)
- **Class `Settings(BaseSettings)`** fields exactly as in ARCHITECTURE/04 & 08.
- **Function `get_settings() -> Settings`** (cached singleton).
- Reads `.env` from CWD. Raises `ValidationError` if required missing (caller handles).
- Never logs `openai_api_key`.

## B. `src/models/__init__.py` (or `src/models.py`)
- Pydantic models listed in `03_INTERFACES_MODELS.md`. No logic.

## C. `src/intake/watcher.py`
- `class FileWatcherHandler(FileSystemEventHandler)`:
  - `on_created`, `on_modified` filter only `samples5/` subtree.
  - Resolve symlinks (must reject path traversal).
  - Enqueue via `queue.enqueue(path, mtime)`.
  - Ignore files >500MB and archive ratio >100:1.
- `def start(watch_dir, queue) -> None`.
- Loop: `Observer().schedule(...)` and join.

## D. `src/intake/router.py`
- `def route(path: str) -> HandlerName` returns one of:
  `text`, `tables`, `audio`, `video`, `archive`, `vlm`, `unsupported`.
- Priority: archive → audio/video → by extension MIME.
- Uses `python-magic` + extension fallback.

## E. `src/intake/queue.py`
- `class JobQueue` (SQLite-backed, single-writer).
  - `enqueue(path, mtime)`
  - `dequeue() -> Job | None`
  - `mark_done(job_id, status)`
  - `list_pending()`
- Idempotent by `(source_path, mtime)`.

## F. `src/extraction/dispatcher.py`
- `def extract(path: str) -> NormalizedExtract`.
- Calls each path selected by router; merges.
- Always runs text path; runs others conditionally.
- Records `ingest_method`, `model_used`, `timestamp`.

## G. `src/extraction/text.py`
- `def extract_text(path) -> ExtractedText` (docling).
- If PDF and len(text)<80: trigger OCR fallback.

## H. `src/extraction/tables.py`
- `def extract_tables(path) -> list[Table]`.

## I. `src/extraction/ocr.py`
- `def ocr_pdf(path) -> str` (Tesseract then PaddleOCR if available).
- Returns confidence; if <0.5 flag low confidence.

## J. `src/extraction/audio.py`
- `def extract_audio(path) -> (text, segments)` via docling/Whisper small.

## K. `src/extraction/video.py`
- `def extract_video(path) -> (text, segments)`:
  - scene-change frames @ SSIM 0.3
  - audio via Whisper.

## L. `src/extraction/archives.py`
- `def extract_archive(path, depth=3) -> list[str]`.
- Rejects path traversal + ratio bombs.

## M. `src/extraction/vlm.py`
- `def enrich(images: list[bytes], prompt_type: str) -> list[VlmFact]`.
- Default backend Qwen2.5-VL-7B (on-prem); fallback GPT-4o via gateway.
- Returns list of `{content, bbox, confidence, model_used}`.

## N. `src/temporal/timestamp_extractor.py` (REUSE + IMPROVE)
- `class TimestampExtractor`:
  - `get_as_of(file_path) -> (datetime, fallback_used)`
  - `get_mtime(file_path) -> datetime`
- Improve for audio/video metadata mod times.

## O. `src/temporal/temporal_kg.py`
- `class TemporalKG` (Neo4j driver via Graphiti):
  - `upsert_fact(fact, valid_at, provenance) -> fact_id`
  - `get_current_facts(entity_id, predicate) -> list[Fact]`
  - `get_facts_as_of(entity_id, predicate, as_of) -> list[Fact]`
  - `supersede(old_fact_id, new_fact_id, at) -> None`
  - `get_supersession_chain(fact_id) -> list[Fact]`
  - `snapshot() -> SnapshotID`
  - `close()`.

## P. `src/temporal/kg_schema.py`
- Cypher schema init: constraints + indexes (idempotent).
- `def init_schema(driver)`.

## Q. `src/reconstruction/entity_resolver.py`
- `def resolve_entities(entities, strategy="fuzzy") -> list[dict]`.
- Semantica merge (fuzzy) then Graphiti canonical.

## R. `src/reconstruction/conflict_resolver.py`
- `def reconcile(new_fact, existing) -> ReconciliationResult`:
  - Compare by entity_id + predicate.
  - If newer `valid_at`: supersede older.
  - Return `{action: keep|supersede, superseded_fact_id}`.
  - Synchronous (no queue).

## S. `src/indexing/vector_indexer.py`
- `class VectorIndexer` (Qdrant):
  - `upsert_fact(fact, embedding) -> point_id`
  - `mark_stale(fact_id)` (set current=false payload)
  - `search(query_emb, filter_current=True, as_of=None, k=10) -> list[ScoredFact]`.

## T. `src/indexing/hierarchical.py`
- `class HierarchicalIndexer`:
  - `build_communities(facts) -> list[Community]`
  - `expand(hit_facts, hops=1) -> list[Fact]`.

## U. `src/retrieval/pure_rag.py`
- `def pure_rag(q, k, as_of=None, current_only=True) -> RetrievalResult`.

## V. `src/retrieval/rag_kg_validator.py`
- `def rag_kg_validator(q, k, as_of=None) -> RetrievalResult`.
  - Vector top-k → KG current check → RRF → checked gen flag.

## W. `src/retrieval/kg_only.py`
- `def kg_only(q, hops, as_of=None) -> RetrievalResult`.

## X. `src/retrieval/hybrid.py`
- `def query(q, mode, as_of=None, include_history=False, ...) -> RetrievedFacts`.

## Y. `src/generation/answer_gen.py`
- DSPy signature `AnswerGenerator`.
- `def answer(q, facts, mode) -> AnswerResponse` (checked generation, citations, confidence).

## Z. `src/generation/citations.py`
- `def build_citation(fact: RetrievedFact) -> str`.

## AA. `src/audit/logger.py`
- `class AuditLogger`: append-only JSONL with SHA-256 hash chain.

## AB. `src/api/server.py`
- FastAPI app with `/query`, `/health`, `/ready`.

## AC. `main.py`
- Uvicorn entry: loads settings, inits schema, starts watcher in thread, runs server.
- `--port`, `--watch-dir`.

## AD. `extract.py` (legacy shim)
- Keep CLI; delegate to new intake if possible, else old path.

## Cross-cutting rules
- All functions raise `ValueError` (not silent) on invalid input.
- All DB access via FastAPI `Depends`.
- All errors captured into `notes` field when generating answers (no crashes).
- No global mutable state except cached settings.
- Timestamps UTC; convert input to UTC on ingest.
- Pydantic models are the sole IO boundary (no dicts cross module boundary without validation).

## Module file size guidance
- Each module ≤300 lines; split if larger.
- One public class/function surface per module preferred.

## Import style
- Absolute imports from `src.` preferred.
- Heavy deps (docling, graphiti) imported inside functions (lazy) to keep startup fast.

## Environment variables (see .env.example)
- `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `MODEL`
- `VLM_MODEL`
- `NEO4J_URI/USER/PASSWORD`
- `QDRANT_URL`
- `WATCH_DIR`, `AUDIT_LOG_PATH`
