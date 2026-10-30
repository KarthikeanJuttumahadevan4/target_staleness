# 11_Handoff_Checklist — Tech Lead Kickoff (post-Architect)

> Status: **Ready for tech lead** (pending human sign-off of open security items).
> All decisions below are recorded; rationale in `08_Decisions_Log.md`.

## Tech Lead First Actions (Days 1–3)

1. **Verify environment**
   ```bash
   tesseract --version
   ffmpeg -version
   python -c "import docling, graphiti_core, qdrant_client, neo4j; print('ok')"
   ```
2. **Spin up Neo4j (on-prem) + Qdrant (docker)**
   - Neo4j: `bolt://localhost:7687`
   - Qdrant: `http://localhost:6333`
3. **Install system deps**
   - `sudo apt-get install tesseract-ocr ffmpeg libgl1 poppler-utils`
4. **Create `.env`** from `.env.example` (no keys committed)
5. **Wire timestamp extractor**
   - Import `extract.py` (legacy) logic; reuse `MetadataExtractor` for mtime
   - Improve for audio/video MOD dates
   - Unit test: `tests/test_timestamp_extractor.py` must pass
6. **Run initial ingest** of `samples5/`
   - `python -m src.intake.watcher` → single pass over samples5
   - Verify ≥5 types produce `NormalizedExtract`

## Modules Tech Lead Must Implement (priority order)

| Priority | Module | File | Spec |
|----------|--------|------|------|
| P0 | Config | `src/config.py` | `08_Decisions_Log` security |
| P0 | Intake | `src/intake/watcher.py`, `router.py`, `queue.py` | `01_Technical_Design` §3 step 1 |
| P0 | Extraction | `src/extraction/*.py` | `02_Intake_Extraction` |
| P0 | Temporal KG | `src/temporal/*.py` | `04_Reconstruction` |
| P0 | Conflict Resolver | `src/reconstruction/conflict_resolver.py` | `04_Reconstruction` |
| P1 | VLM Enrichment | `src/extraction/vlm.py` | `03_VLM_Enrichment` |
| P1 | Hierarchical Indexing | `src/indexing/hierarchical.py` | `04_Database_Design` |
| P1 | Retrieval (3 modes) | `src/retrieval/*.py` | `05_Retrieval` |
| P1 | Answer Generation | `src/generation/answer_gen.py` | `05_Retrieval` |
| P2 | API Server | `src/api/server.py` | `06_API_Contracts` |
| P2 | Audit Logger | `src/audit/logger.py` | `09_Risk_Failure_Modes` |

## Decisions Locked (must not be re-litigated)
- Graph: **Neo4j**
- Vector: **Qdrant**
- LLM: **OpenAI via internal gateway**
- VLM: **GPT-4o/Gemini primary; Qwen2.5-VL-7B-SFT on-prem fallback**
- Temporal engine: **Graphiti + RAGBrain**
- Supersession: **Synchronous**
- `as_of`: **Explicit param (exposed)**
- Query cache: **Disabled by default**
- Entity resolution: **Semantica + Graphiti (two-pass)**
- OCR: **Tesseract + PaddleOCR secondary**
- Video frames: **Scene-change (SSIM 0.3)**
- Snapshots: **Per-ingest + weekly prune (keep 52)**
- `extract.py`: **Improve + reuse**

## Open Security Items Requiring Human Sign-Off (do before coding deploys)
1. PII/classification redaction: intake vs query-time → recommend **intake-time**
2. Multi-tenancy (org_unit scoping): day 1 vs defer → recommend **day 1**
3. File watching: OS-events vs polling → recommend **OS-events + poll fallback**

## Definition of Done (engineering)
- [ ] `uv run pytest -q` green (all existing temporal tests pass)
- [ ] `samples5/` ingest succeeds; ≥5 formats produce facts
- [ ] Supersession demo: add newer conflicting file → old flagged superseded
- [ ] All 3 retrieval modes return newest by default
- [ ] Answers include provenance + timestamp citation
- [ ] `main.py` serves `/query`, `/health`, `/ready`
- [ ] Audit log hash-chained append-only
- [ ] Latency <3s (1k facts) on Neo4j+Qdrant local

## References (in priority order for reading)
1. `UPDATED_MODEL/ARCHITECTURE/01_Technical_Design.md`
2. `UPDATED_MODEL/ARCHITECTURE/08_Decisions_Log.md`
3. `UPDATED_MODEL/ARCHITECTURE/04_Database_Design.md`
4. `UPDATED_MODEL/ARCHITECTURE/03_Coding_Implementation_Plan.md`
5. `UPDATED_MODEL/ARCHITECTURE/05_Directory_Structure.md`
6. `UPDATED_MODEL/ARCHITECTURE/06_API_Contracts.md`

## Handoff
- **From:** Architect → **To:** Tech Lead
- **Date:** (fill at handoff)
- **Sign-offs required:** Tech Lead (design accept), Security officer (open security items), Mission lead (classification redaction scope)

---
*Architect role complete. All planning artifacts delivered in `UPDATED_MODEL/ARCHITECTURE/`.*
