# 📋 ARCHITECT DIRECTIVES - Actions Required Before Query-to-Output

## Purpose
This document provides **deliberate, actionable directions** for the architect to complete before the system can accept a query through the UI and produce visible output. The temporal core is implemented, but the **data ingestion pipeline and UI integration are incomplete**.

---

## 🎯 Current State

### ✅ **What EXISTS and Works**
- Temporal Core: `src/temporal/*` (timestamp extraction, KG schema, conflict resolution)
- Retrieval Modules: `src/retrieval/*` (pure_rag, rag_kg_validator, kg_only, hybrid)
- API Server: `src/api/server.py`, `main.py`
- Configuration: `src/config.py`, `src/models.py`
- Sample Files: `SAMPLES/` directory with test documents

### ❌ **What's MISSING (Blocking Query-to-Output)**
1. **Intake Pipeline** - No files are being ingested
2. **Extraction Pipeline** - No document processing
3. **Database Connection** - Neo4j and Qdrant not integrated
4. **Indexing Pipeline** - No vectors in Qdrant
5. **Generation Pipeline** - No answer generation
6. **UI-to-API Integration** - No visible output path

---

## 🚨 Critical Path Analysis

For a user query to produce visible output, the following **must** be completed in order:

```
USER QUERY → UI → API (main.py) → RETRIEVAL → GENERATION → OUTPUT
                     ↑
DATA: KG (Neo4j) + Vectors (Qdrant) ← INDEXING ← RECONSTRUCTION ← EXTRACTION ← INTAKE ← samples5/
```

**Blockers:** INTAKE, EXTRACTION, INDEXING, GENERATION, and UI connections are all missing or incomplete.

---

## 📋 DELIBERATE DIRECTIVES FOR ARCHITECT

### 🔴 **PRIORITY 1: Unblock Data Ingestion (M1-M3)**
Without data ingestion, queries have nothing to retrieve. These must be completed first.

#### D1. Implement Intake Module (`src/intake/`)
**Status:** ❌ NOT IMPLEMENTED  
**Blocked:** Nothing - all dependencies available  
**Effort:** 2-4 hours  

**Actions:**
1. Create `src/intake/__init__.py`
2. Create `src/intake/watcher.py` - File system watcher using `watchdog`
   - Monitor `samples5/` directory for new/modified files
   - Emit `FileEvent(path, event_type, mtime)` to queue
3. Create `src/intake/queue.py` - SQLite-based job queue
   - Table: `jobs(id, file_path, status, created_at, updated_at)`
   - Methods: `enqueue(file_path)`, `dequeue()`, `mark_completed(job_id)`
   - Ensure idempotency: same file processed once
4. Create `src/intake/router.py` - Format routing
   - Input: file path
   - Output: handler (text, ocr, audio, video, archive)
   - Use `python-magic` for MIME detection
   - Map to extraction paths

**Verification:**
```bash
# Test: Drop a file into samples5/, verify it appears in queue
mkdir -p samples5
echo "test document" > samples5/test_doc.txt
# Should see: Job enqueued for samples5/test_doc.txt
```

**Reference:**
- `UPDATED_MODEL/ARCHITECTURE/01_Technical_Design.md` - Section 2 (Intake)
- `UPDATED_MODEL/CODE DIRECTIONS AND PRODUCTS/04_CODE_SCAFFOLDS.md` - Intake templates

---

#### D2. Implement Extraction Module (`src/extraction/`)
**Status:** ❌ EXISTS BUT INCOMPLETE (only multi_path_extractor.py)  
**Blocked:** Needs Intake (D1) to feed it files  
**Effort:** 4-6 hours  

**Actions:**
1. Create `src/extraction/dispatcher.py` - Orchestrator
   - Input: file from intake queue
   - Output: `NormalizedExtract` object
   - Coordinate all extraction paths
   - Call `extract.py` for timestamp extraction (reuse existing)

2. Create individual extractors:
   - `src/extraction/text.py` - Docling text extraction
   - `src/extraction/tables.py` - Docling table extraction
   - `src/extraction/vlm.py` - VLM enrichment (Qwen2.5-VL or GPT-4o)
   - `src/extraction/audio.py` - Whisper via Docling
   - `src/extraction/video.py` - Frame extraction + audio
   - `src/extraction/ocr.py` - Tesseract fallback
   - `src/extraction/archives.py` - ZIP/TAR extraction (depth ≤3)

3. Define `NormalizedExtract` model:
   ```python
   class NormalizedExtract(BaseModel):
       doc_id: UUID
       source_path: str
       valid_at: datetime  # from extract.py
       ingest_method: str  # "text"|"ocr"|"audio"|"video"|"vlm"|"table"
       text: str
       entities: list[Entity]
       relations: list[Relation]
       metadata: dict
   ```

**Verification:**
```bash
# Test: Process queued file, verify NormalizedExtract output
# Should produce: doc_id, valid_at timestamp, extracted text
```

**Reference:**
- `02_Intake_Extraction.md` - Extraction details
- `src/extraction/multi_path_extractor.py` - Existing code to reuse/extend

---

#### D3. Implement Reconstruction Module (`src/reconstruction/`)
**Status:** ⏳ PARTIAL (entity_resolver.py and conflict_resolver.py exist)  
**Blocked:** Needs Extraction (D2) output  
**Effort:** 2-3 hours  

**Actions:**
1. Verify `src/reconstruction/entity_resolver.py` - Entity resolution
   - Use Semantica for fuzzy matching
   - Merge entities across extraction paths
   - Input: `NormalizedExtract` from Extraction
   - Output: Merged entities with canonical IDs

2. Verify `src/reconstruction/conflict_resolver.py` - Supersession
   - Already exists and works independently
   - Ensure integration with Temporal KG
   - Input: Conflicting facts
   - Output: Resolved facts with current flags

3. Create pipeline integration:
   - Connect Extraction → Entity Resolution → Conflict Resolution → Temporal KG
   - Implement `process_extract(extract: NormalizedExtract) → list[Fact]`

**Verification:**
```bash
# Test: Extract file, resolve entities, resolve conflicts
# Input: Document with conflicting information
# Output: Single current fact, superseded history
```

---

### 🟡 **PRIORITY 2: Unblock Knowledge Storage (M4)**
Data must be stored in KG and vector index before retrieval can work.

#### D4. Set Up and Integrate Databases
**Status:** ❌ NOT INTEGRATED  
**Blocked:** Nothing - can be done in parallel with D1-D3  
**Effort:** 2-3 hours (setup + integration)  

**Actions:**
1. **Neo4j Setup:**
   - Install Neo4j 5.x locally or in Docker
   - Create `data/neo4j` directory
   - Configure connection in `.env`:
     ```
     NEO4J_URI=bolt://localhost:7687
     NEO4J_USER=neo4j
     NEO4J_PASSWORD=password
     ```

2. **Qdrant Setup:**
   - Docker: `docker run -p 6333:6333 -v data/qdrant:/qdrant/storage qdrant/qdrant`
   - Configure in `.env`:
     ```
     QDRANT_URL=http://localhost:6333
     ```

3. **Initialize Temporal KG Schema:**
   - Run `src/temporal/kg_schema.init_schema()` on startup
   - Create nodes: Entity, Fact, Provenance
   - Create relationships: has_fact, supersedes, derived_from
   - Ensure idempotency (can run multiple times safely)

**Verification:**
```bash
# Test Neo4j connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687'); driver.verify_connectivity()"

# Test Qdrant connection  
python -c "from qdrant_client import QdrantClient; client = QdrantClient('localhost', 6333); print(client.get_collections())"
```

---

#### D5. Implement Indexing Module (`src/indexing/`)
**Status:** ❌ NOT IMPLEMENTED  
**Blocked:** Needs Databases (D4) and Reconstruction (D3)  
**Effort:** 2-3 hours  

**Actions:**
1. Create `src/indexing/vector_indexer.py`:
   - Use Qdrant client
   - Embed facts using `all-mpnet-base-v2` (offline)
   - Store only `current=true` facts by default
   - Support filtering by `as_of` timestamp
   - Implement `index_fact(fact: RetrievedFact)` and `search(query: str, as_of: datetime)`

2. Create `src/indexing/hierarchical_indexer.py`:
   - Implement HiRAG community summaries
   - Group facts by entity type, org_unit, classification
   - Create hierarchical index for efficient retrieval

**Verification:**
```bash
# Test: Index a fact, search for it
# Should: Store embedding, retrieve matching facts
```

**Reference:**
- `05_Retrieval.md` - Indexing requirements
- `ARCHITECTURE/04_Database_Design.md` - Schema details

---

### 🟢 **PRIORITY 3: Unblock Query Processing (M5-M6)**
With data indexed, retrieval and generation can work.

#### D6. Connect Retrieval to Indexed Data
**Status:** ❌ EXISTS BUT NOT CONNECTED  
**Blocked:** Needs Indexing (D5)  
**Effort:** 2-3 hours  

**Actions:**
1. Update `src/retrieval/pure_rag.py`:
   - Connect to Qdrant vector index
   - Filter by `current=true` (default)
   - Re-rank by recency: `score' = score * recency_weight(as_of)`
   - Return `RetrievedFact` objects

2. Update `src/retrieval/kg_only.py`:
   - Connect to Neo4j KG
   - Query: `MATCH (e)-[f]->() WHERE f.current=true AND e.name = ...`
   - Return facts with temporal metadata

3. Update `src/retrieval/rag_kg_validator.py`:
   - Use Pure RAG for candidate generation
   - Query KG for current fact verification
   - Override stale RAG hits with KG facts
   - Use RRF (Reciprocal Rank Fusion) for fusion

4. Update `src/retrieval/hybrid.py`:
   - Orchestrate all 3 modes
   - Ensure consistent temporal filtering

**Verification:**
```bash
# Test each retrieval mode individually
python -c "from src.retrieval.pure_rag import PureRAGRetriever; r = PureRAGRetriever(); print(r.search('test query'))"
```

---

#### D7. Implement Generation Module (`src/generation/`)
**Status:** ❌ NOT IMPLEMENTED  
**Blocked:** Needs Retrieval (D6)  
**Effort:** 2-3 hours  

**Actions:**
1. Create `src/generation/answer_gen.py`:
   - Use DSPy for answer generation
   - Input: Retrieved facts + query
   - Output: Answer with citations
   - Use checked generation (verify facts before answering)

2. Create `src/generation/citations.py`:
   - Format citations per spec:
     ```
     Fact: <content>
     Source: <file>, p.<n>
     Extracted via: <path> (<model>)
     As-of: <timestamp>
     Confidence: <score>
     ```
   - Generate citation strings for each fact

**Verification:**
```bash
# Test: Query → Retrieved Facts → Answer + Citations
# Should: Return structured answer with citations
```

---

#### D8. Complete API Integration
**Status:** ❌ PARTIAL (server exists but handlers incomplete)  
**Blocked:** Needs Generation (D7)  
**Effort:** 1-2 hours  

**Actions:**
1. Update `src/api/server.py`:
   - Implement `POST /query` endpoint:
     ```python
     @app.post("/query")
     async def query_endpoint(query_request: QueryRequest):
         # 1. Route to retrieval mode
         if query_request.mode == "pure_rag":
             facts = pure_rag_retriever.search(query_request.question, query_request.as_of)
         elif query_request.mode == "rag_kg_validator":
             facts = rag_kg_retriever.search(query_request.question, query_request.as_of)
         elif query_request.mode == "kg_only":
             facts = kg_only_retriever.search(query_request.question, query_request.as_of)
         
         # 2. Generate answer
         answer = answer_generator.generate(query_request.question, facts)
         
         # 3. Add audit
         audit_id = audit_logger.log_query(query_request, answer, facts)
         
         return QueryResponse(
             answer=answer.answer,
             facts=facts,
             audit_id=audit_id,
             confidence=answer.confidence
         )
     ```
   
2. Implement `GET /health` and `GET /ready` endpoints:
   - `/health`: Basic service health
   - `/ready`: Check all dependencies (Neo4j, Qdrant, models)

**Verification:**
```bash
# Test: Start server, send query
python main.py --port 8000 &
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"question": "test", "mode": "kg_only"}'
```

---

### 🔵 **PRIORITY 4: UI Integration (M7-M8)**

#### D9. Connect UI to API
**Status:** ❌ UI EXISTS BUT NOT CONNECTED (`USER_INTERFACE/app.py`, `ui_streamlit.py`)  
**Blocked:** Needs API (D8)  
**Effort:** 1-2 hours  

**Actions:**
1. Choose UI framework:
   - Option A: Streamlit (`ui_streamlit.py`) - Quick demo
   - Option B: FastAPI frontend (`USER_INTERFACE/app.py`) - Production

2. Streamlit (Recommended for quick demo):
   ```python
   # ui_streamlit.py
   import streamlit as st
   import requests
   
   API_BASE = "http://localhost:8000"
   
   st.title("Temporal KG-RAG Query Demo")
   
   question = st.text_input("Enter your query:")
   mode = st.selectbox("Retrieval Mode:", ["pure_rag", "rag_kg_validator", "kg_only"])
   
   if st.button("Search"):
       response = requests.post(f"{API_BASE}/query", json={
           "question": question,
           "mode": mode,
           "as_of": None,
           "include_history": False
       })
       result = response.json()
       
       st.subheader("Answer:")
       st.write(result["answer"])
       
       st.subheader("Citations:")
       for fact in result["facts"]:
           st.write(f"- {fact['content']} (Source: {fact['source']}, As-of: {fact['as_of']})")
   ```

3. Run UI:
   ```bash
   # For Streamlit
   streamlit run ui_streamlit.py
   
   # For FastAPI
   python USER_INTERFACE/app.py --port 8501
   ```

**Verification:**
```bash
# Test: Open browser, enter query, see answer with citations
# Should: Display answer + facts + timestamps in browser
```

---

## 📊 Implementation Order Summary

### Phase 1: Data Ingestion (Week 1) - **UNBLOCKS QUERY INPUT**
| Directive | Module | Status | Effort | Dependencies |
|-----------|--------|--------|--------|--------------|
| D1 | Intake | ❌ | 2-4h | None |
| D2 | Extraction | ❌ | 4-6h | D1 |
| D3 | Reconstruction | ⏳ | 2-3h | D2 |

### Phase 2: Knowledge Storage (Week 1-2) - **UNBLOCKS DATA FOR RETRIEVAL**
| Directive | Module | Status | Effort | Dependencies |
|-----------|--------|--------|--------|--------------|
| D4 | Databases | ❌ | 2-3h | None (parallel) |
| D5 | Indexing | ❌ | 2-3h | D3, D4 |

### Phase 3: Query Processing (Week 2) - **UNBLOCKS ANSWER GENERATION**
| Directive | Module | Status | Effort | Dependencies |
|-----------|--------|--------|--------|--------------|
| D6 | Retrieval | ❌ | 2-3h | D5 |
| D7 | Generation | ❌ | 2-3h | D6 |
| D8 | API Integration | ❌ | 1-2h | D7 |

### Phase 4: UI Integration (Week 2-3) - **UNBLOCKS VISIBLE OUTPUT**
| Directive | Module | Status | Effort | Dependencies |
|-----------|--------|--------|--------|--------------|
| D9 | UI Connection | ❌ | 1-2h | D8 |

---

## 🎯 Minimum Viable Path to Query-to-Output

**Fastest path to demo (2-3 days of work):**

### Day 1: Data Ingestion
1. **D1** - Implement Intake (2-4h)
2. **D4** - Set up Databases (2-3h, parallel)
3. **D2** - Implement Extraction (4-6h)

### Day 2: Knowledge & Query
4. **D3** - Connect Reconstruction (2-3h)
5. **D5** - Implement Indexing (2-3h)
6. **D6** - Connect Retrieval (2-3h)

### Day 3: Output
7. **D7** - Implement Generation (2-3h)
8. **D8** - Complete API (1-2h)
9. **D9** - Connect UI (1-2h)

**Milestone:** User can drop file in `samples5/`, open UI, enter query, see answer with citations.

---

## 🚨 What the Architect Should Do FIRST

**Before anything else, the architect must:**

1. **Read these files:**
   - `UPDATED_MODEL/ARCHITECTURE/01_Technical_Design.md` - System architecture
   - `UPDATED_MODEL/ARCHITECTURE/05_Directory_Structure.md` - Where files go
   - `UPDATED_MODEL/CODE DIRECTIONS AND PRODUCTS/04_CODE_SCAFFOLDS.md` - Code templates
   - `UPDATED_MODEL/ARCHITECTURE/10_Test_Plan.md` - Test requirements

2. **Verify current state:**
   ```bash
   # Confirm these exist
   ls -la src/temporal/
   ls -la src/retrieval/
   ls -la src/api/
   
   # Confirm these don't exist
   ls -la src/intake/ 2>&1 | grep "No such"
   ls -la src/extraction/ 2>&1 | grep "No such"
   ls -la src/indexing/ 2>&1 | grep "No such"
   ls -la src/generation/ 2>&1 | grep "No such"
   ```

3. **Start with D1 (Intake) immediately** - This is the/first blocker

---

## ✅ Acceptance Criteria

**Before declaring "ready for demo", verify:**

1. **Data Flow Test:**
   ```bash
   # Drop file in samples5/
   cp SAMPLES/invoice_1.pdf samples5/
   
   # Wait for processing (should be automatic)
   sleep 5
   
   # Query via API
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the invoice total?", "mode": "kg_only"}'
   
   # Should return: Answer with citations and timestamps
   ```

2. **UI Test:**
   - Open UI in browser
   - Enter query: "What documents are in the system?"
   - Select mode: "pure_rag"
   - Click Search
   - **Should see:** Answer text + citations with source files and timestamps

3. **Temporal Test:**
   ```bash
   # Add older file
   touch -d "2024-01-01" SAMPLES/old_invoice.pdf
   cp SAMPLES/old_invoice.pdf samples5/
   
   # Add newer file with conflicting info
   touch -d "2024-02-01" SAMPLES/new_invoice.pdf
   cp SAMPLES/new_invoice.pdf samples5/
   
   # Query should return newest info
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the current invoice total?", "mode": "pure_rag"}'
   
   # Should return: Newest invoice data, not old
   ```

---

## 📋 Summary: Directives Priority Order

| Priority | Directive | Module | Purpose | Blocking? |
|----------|-----------|--------|---------|-----------|
| 🔴 1 | D1 | Intake | Files get into system | **YES** - First blocker |
| 🔴 2 | D4 | Databases | Store KG and vectors | **YES** - Parallel with D1 |
| 🔴 3 | D2 | Extraction | Parse file content | **YES** - Needs D1 |
| 🔴 4 | D3 | Reconstruction | Resolve entities/conflicts | **YES** - Needs D2 |
| 🟡 5 | D5 | Indexing | Make data searchable | **YES** - Needs D3, D4 |
| 🟡 6 | D6 | Retrieval | Connect to indexed data | **YES** - Needs D5 |
| 🟡 7 | D7 | Generation | Create answers | **YES** - Needs D6 |
| 🟡 8 | D8 | API Integration | Expose query endpoint | **YES** - Needs D7 |
| 🟢 9 | D9 | UI Connection | Visible output | **YES** - Final step |

---

## 🎯 Final Note

**The temporal core is complete, but the pipeline is empty.** 

Without implementing **D1-D5**, there is no data in the system. Without **D6-D9**, there is no way to query that data through the UI.

**The architect's first task is D1 (Intake) - everything else depends on getting data into the system.**

Once D1-D9 are complete, you will be able to:
✅ Drop files into `samples5/`
✅ See them automatically processed
✅ Open the UI
✅ Enter a query
✅ **See an answer with citations and timestamps**

---

## 📞 Need Clarification?

If any directive is unclear, the architect should refer to:
- `UPDATED_MODEL/ARCHITECTURE/01_Technical_Design.md` - System overview
- `UPDATED_MODEL/ARCHITECTURE/04_Database_Design.md` - Schema details
- `UPDATED_MODEL/ARCHITECTURE/06_API_Contracts.md` - API specifications
- `UPDATED_MODEL/CODE DIRECTIONS AND PRODUCTS/04_CODE_SCAFFOLDS.md` - Code templates

Each of these files contains detailed specifications that the architect can use to implement the directives above.
