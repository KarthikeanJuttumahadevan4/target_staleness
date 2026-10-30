---
format: html
---

# 08_Decisions_Log — Question Answers

Each row: Question → Decision → Military Rationale.

## Architecture

| Question | Decision | Rationale |
|----------|----------|-----------|
| Graph backend: Neo4j/FalkorDB/Memgraph? | **Neo4j** | Mature, ACID, Cypher queryable by analysts, audit tooling; on-prem |
| Vector store: Qdrant/Weaviate/Chroma? | **Qdrant** | Rust, low memory, payload filters, on-prem docker |
| LLM provider: OpenAI | **Confirmed — internal gateway** | Military air-gap: gate behind internal LLM gateway; no keys in repo; redact gate |
| VLM: cloud GPT-4o/Gemini | **Confirmed — primary VLM via gateway**; fallback Qwen2.5-VL-7B-SFT on-prem | Cloud better accuracy; on-prem fallback for air-gap |
| Primary temporal engine: Graphiti + RAGBrain | **Confirmed** | Combined stack: episodes + supersession + checked generation |

## Intake & Extraction

| Question | Decision | Rationale |
|----------|----------|-----------|
| Audio/video: Online vs offline batch? | **Offline batch (priority: offline)** | Military docs with audio/vehicle logs must be air-gapped safe |
| ZIP archives: Auto-extract vs manual? | **Auto-extract**, depth ≤3, size caps | Document bundles are commonly zipped field packets; auto-intake needed |
| OCR priority: Tesseract/EasyOCR/PaddleOCR? | **Tesseract (PaddleOCR secondary)** | Tesseract offline installable (system pkg); Paddle better accuracy but heavier deps |
| Video frame extraction: 1fps vs scene-change? | **Scene-change (SSIM threshold 0.3)** | Military video (CCTV/UAV) has long static periods; scene-change saves compute |
| PDF threshold | **80 chars** (per spec) | Proven heuristic; military text dense enough |

## Temporal

| Question | Decision | Rationale |
|----------|----------|-----------|
| Reuse/Improve `extract.py` | **Improve + reuse** (add audio/video MOD dates; reuse mtime) | Timestamp is temporal authority; must handle more formats |
| Supersession: sync vs background? | **Synchronous** | Classified data must resolve conflicts immediately, not eventual |
| Snapshots: per-ingest vs weekly? | **Per-ingest + weekly prune (keep last 52)** | Audit trail mandatory; per-ingest via Semantica TemporalVersionManager |
| Entity resolution: Semantica vs Graphiti? | **Both**: Semantica ML fuzzy first, then Graphiti LLM canonical | Military similar docs benefit from robust dedup; two-pass |

## Retrieval

| Question | Decision | Rationale |
|----------|----------|-----------|
| Reranking: ms-marco vs LLM-as-reranker? | **ms-marco-MiniLM (fast) + LLM-as-reranker for top-20 (optional flag)** | Default fast; critical queries opt into slower LLM |
| Query cache: enable 1-hr TTL? | **DISABLE query cache by default** | Classified queries should not be retained; manual enable per scope |
| `as_of` detection: expose vs auto-detect? | **Expose (explicit `as_of` param)** | Military auditors need explicit control; auto-detect ambiguous |
| Checked generation: always vs Mode 2? | **Always in Mode 2; Mode 3 configurable; Mode 1 never (speed)** | Critical intelligence must be verified |

## Open Items Requiring Human Decision
1. Should classified PII redaction happen at intake or at query-time? **Recommend: intake-time.**
2. Should `samples5/` be polled vs OS-event? **Recommend: OS event (inotify); poll fallback**.
3. Should there be multi-tenancy (org_unit scoping) from day 1? **Recommend: yes, org_unit in schema** to avoid re-migration.
4. Are audio/video transcripts considered classified? **Assume yes; treat like text.**
5. Should export allow only the user's org data? **Recommend: yes, enforce via query filter.**
