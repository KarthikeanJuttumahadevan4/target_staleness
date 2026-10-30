# ✅ ARCHITECT QUICK CHECKLIST - Query-to-Output

## The Problem
**Temporal core is built, but there's no data pipeline.** Users cannot query because:
1. No files are being ingested
2. No data is in the KG or vector index
3. Retrieval and UI are not connected

---

## The Solution: 9 Directives in Order

### 🔴 PHASE 1: Get Data In (Days 1-2)

**D1. Implement Intake (`src/intake/`)**  
- [ ] `watcher.py` - Watch `samples5/` directory
- [ ] `queue.py` - SQLite job queue
- [ ] `router.py` - Route by file type (python-magic)
- ✅ **Test:** Drop file in samples5/ → appears in queue

**D2. Implement Extraction (`src/extraction/`)**  
- [ ] `dispatcher.py` - Orchestrate all paths
- [ ] `text.py`, `tables.py`, `ocr.py` - Document parsing
- [ ] `vlm.py`, `audio.py`, `video.py` - Multimedia
- [ ] `archives.py` - ZIP/TAR extraction
- ✅ **Test:** Queue item → NormalizedExtract output

**D3. Connect Reconstruction (`src/reconstruction/`)**  
- [ ] Verify `entity_resolver.py` - Merge entities (Semantica)
- [ ] Verify `conflict_resolver.py` - Most-recent-wins
- [ ] Connect: Extraction → Entity Resolution → KG
- ✅ **Test:** Conflicting facts → single current + superseded history

---

### 🟡 PHASE 2: Store and Index Data (Day 3)

**D4. Set Up Databases**  
- [ ] Neo4j 5.x running
- [ ] Qdrant running
- [ ] `.env` configured (NEO4J_URI, QDRANT_URL)
- [ ] `kg_schema.init_schema()` on startup
- ✅ **Test:** Python can connect to both

**D5. Implement Indexing (`src/indexing/`)**  
- [ ] `vector_indexer.py` - Qdrant + embeddings
- [ ] `hierarchical_indexer.py` - HiRAG communities
- ✅ **Test:** Index fact → search returns it

---

### 🟢 PHASE 3: Enable Query Processing (Day 4)

**D6. Connect Retrieval (`src/retrieval/`)**  
- [ ] `pure_rag.py` → Qdrant with current=true filter
- [ ] `kg_only.py` → Neo4j with current=true filter
- [ ] `rag_kg_validator.py` → RAG + KG validation + RRF
- [ ] `hybrid.py` → Orchestration
- ✅ **Test:** Each mode returns facts

**D7. Implement Generation (`src/generation/`)**  
- [ ] `answer_gen.py` - DSPy answer generation
- [ ] `citations.py` - Format with provenance
- ✅ **Test:** Facts → answer + citations

**D8. Complete API (`src/api/server.py`)**  
- [ ] `POST /query` - Route to retrieval + generation
- [ ] `GET /health` - Service health
- [ ] `GET /ready` - Dependencies ready
- ✅ **Test:** curl query → JSON response

---

### 🔵 PHASE 4: UI Output (Day 5)

**D9. Connect UI**  
- [ ] Choose: Streamlit (`ui_streamlit.py`) or FastAPI (`USER_INTERFACE/app.py`)
- [ ] Connect to API endpoints
- [ ] Display: Answer + citations + timestamps
- ✅ **Test:** Browser query → visible answer

---

## End-to-End Test

```bash
# 1. Drop file
cp SAMPLES/invoice_1.pdf samples5/

# 2. Wait for processing (automatic)
sleep 5

# 3. Query via API
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the invoice total?", "mode": "pure_rag"}'

# 4. Query via UI
# Open browser to Streamlit or FastAPI UI
# Enter query → See answer with citations
```

---

## Status Tracker

| Directive | Module | Status | Started | Completed | Notes |
|-----------|--------|--------|---------|-----------|-------|
| D1 | Intake | ⬜ | | | | |
| D2 | Extraction | ⬜ | | | | |
| D3 | Reconstruction | ⬜ | | | | |
| D4 | Databases | ⬜ | | | | |
| D5 | Indexing | ⬜ | | | | |
| D6 | Retrieval | ⬜ | | | | |
| D7 | Generation | ⬜ | | | | |
| D8 | API | ⬜ | | | | |
| D9 | UI | ⬜ | | | | |

---

## Daily Focus

### Day 1: Data Ingestion
- **Morning:** D1 (Intake)
- **Afternoon:** D2 (Extraction)
- **End of Day:** Files can be dropped in samples5/ and processed

### Day 2: Storage & Indexing
- **Morning:** D3 (Reconstruction) + D4 (Databases)
- **Afternoon:** D5 (Indexing)
- **End of Day:** Data appears in Neo4j and Qdrant

### Day 3: Query Processing
- **Morning:** D6 (Retrieval)
- **Afternoon:** D7 (Generation) + D8 (API)
- **End of Day:** API returns answers to queries

### Day 4: UI
- **Morning:** D9 (UI Connection)
- **End of Day:** Full demo working in browser

---

## Start Here

**Architect's first action:**

```bash
# 1. Read the full directives
cat UPDATED_MODEL/ARCHITECT_DIRECTIVES.md

# 2. Start with D1 - Intake
mkdir -p src/intake
touch src/intake/__init__.py
# Create watcher.py, queue.py, router.py

# 3. Verify D1 works
mkdir -p samples5
echo "test" > samples5/test.txt
# Should see: File detected and queued
```

---

## Acceptance Criteria

| Milestone | Criteria | Status |
|-----------|----------|--------|
| M1 Ingestion | Drop file → appears in queue | ⬜ |
| M2 Extraction | Queue item → NormalizedExtract | ⬜ |
| M3 Reconstruction | Extract → facts in KG with temporal flags | ⬜ |
| M4 Storage | KG has nodes, Qdrant has vectors | ⬜ |
| M5 Retrieval | Query → facts returned | ⬜ |
| M6 Generation | Facts → answer + citations | ⬜ |
| M7 API | curl query → JSON response | ⬜ |
| M8 UI | Browser query → visible answer | ⬜ |

**All boxes must be ✅ for query-to-output to work.**

---

## Quick Reference

- **Full directives:** `ARCHITECT_DIRECTIVES.md`
- **Technical design:** `ARCHITECTURE/01_Technical_Design.md`
- **Code templates:** `CODE DIRECTIONS AND PRODUCTS/04_CODE_SCAFFOLDS.md`
- **API specs:** `ARCHITECTURE/06_API_Contracts.md`

---

## 🎯 The Goal

**5 days from now, you should be able to:**
1. Drop any file into `samples5/`
2. Open the UI in a browser
3. Type a question
4. **Get an answer with citations, timestamps, and provenance**

**Start with D1 (Intake) - everything depends on getting data into the system.**
