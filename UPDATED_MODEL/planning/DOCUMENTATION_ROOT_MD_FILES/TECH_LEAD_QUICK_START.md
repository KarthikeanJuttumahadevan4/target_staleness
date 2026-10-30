---
format: html
---

# 🚀 TECH LEAD QUICK START - Working UI in 2 Weeks

## Your Mission

**Deliver a working Temporal-Valid KG-RAG System UI in 2 weeks** that can:
1. Accept file uploads/drops
2. Process documents automatically
3. Answer queries through a web UI
4. Show citations with timestamps and provenance

---

## Current State

**What's READY (Don't Reimplement):**
- ✅ Temporal Core: `src/temporal/*` (timestamp extraction, KG schema, conflict resolution)
- ✅ Retrieval Modules: `src/retrieval/*` (pure_rag, rag_kg_validator, kg_only, hybrid)
- ✅ API Skeleton: `src/api/server.py`, `main.py`
- ✅ Models: `src/models.py`, `src/config.py`
- ✅ Sample Files: `SAMPLES/`

**What's MISSING:**
- ❌ Intake: `src/intake/` (watcher, queue, router)
- ❌ Extraction: `src/extraction/` (multi-path processing)
- ❌ Reconstruction: Entity resolution integration
- ❌ Indexing: `src/indexing/` (vector + hierarchical)
- ❌ Generation: `src/generation/` (DSPy answer gen)
- ❌ UI Connection: Streamlit/FastAPI frontend

---

## 🎯 2-Week Implementation Plan

### Week 1: Data Pipeline (Days 1-5)
**Goal:** Files can be dropped in `samples5/` and appear as facts in KG + Qdrant

#### Day 1: Environment & Intake (Tech Lead + Dev A)
**Morning - Environment (Tech Lead):**
```bash
# Install system deps
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng ffmpeg libgl1 poppler-utils

# Or macOS:
brew install tesseract ffmpeg python-magic

# Python setup
uv init
uv add graphiti-core ragbrain docling docling-graph qdrant-client neo4j \
      dspy sentence-transformers python-dotenv watchdog python-magic fastapi uvicorn
uv sync
```

**Afternoon - Intake (Dev A):**
```bash
mkdir -p src/intake
touch src/intake/__init__.py

# Create these files (templates in ARCHITECT_DIRECTIVES.md):
# - watcher.py (watchdog for samples5/)
# - queue.py (SQLite)
# - router.py (MIME → handler)
```

**Test:**
```bash
mkdir -p samples5
cp SAMPLES/test.txt samples5/
# Should print: "📥 File detected: test.txt - enqueued for processing"
```

---

#### Day 2: Extraction & Databases (Dev B + Dev C)

**Dev B - Extraction:**
```bash
mkdir -p src/extraction
touch src/extraction/__init__.py

# Create:
# - dispatcher.py (orchestrator)
# - text.py (docling text)
# - ocr.py (tesseract fallback)
# - archives.py (ZIP/TAR)
# (Start with text/PDF only for MVP)
```

**Dev C - Databases:**
```bash
# Start Neo4j
unz neo4j.tar.gz -d data/
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
  -v $(pwd)/data/neo4j:/data -e NEO4J_AUTH=neo4j/password neo4j:5

# Start Qdrant
docker run -d --name qdrant -p 6333:6333 \
  -v $(pwd)/data/qdrant:/qdrant/storage qdrant/qdrant

# Configure .env
cat > .env << EOF
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
QDRANT_URL=http://localhost:6333
EOF
```

**Test:**
```bash
# Extraction test
python -c "from src.extraction.dispatcher import ExtractionDispatcher; print('✅')"

# DB test
python -c "from neo4j import GraphDatabase; from qdrant_client import QdrantClient; print('✅')"
```

---

#### Day 3: Reconstruction & Indexing (Dev B + Dev C)

**Dev B - Reconstruction:**
```bash
# Update src/reconstruction/entity_resolver.py
# Update src/reconstruction/conflict_resolver.py
# Connect to Temporal KG
```

**Dev C - Indexing:**
```bash
mkdir -p src/indexing
touch src/indexing/__init__.py

# Create:
# - vector_indexer.py (Qdrant + embeddings)
# Start with basic vector index
```

**Test:**
```bash
# Drop file in samples5/
cp SAMPLES/invoice_1.pdf samples5/

# Check Neo4j: Should have fact nodes
# Check Qdrant: Should have vectors
```

---

#### Day 4-5: Retrieval & Generation (Dev A + Dev B)

**Dev A - Retrieval:**
```bash
# Connect existing retrieval modules to KG + Qdrant
# Update:
# - pure_rag.py → Qdrant
# - kg_only.py → Neo4j
# - rag_kg_validator.py → both
```

**Dev B - Generation:**
```bash
mkdir -p src/generation
touch src/generation/__init__.py

# Create:
# - answer_gen.py (DSPy)
# - citations.py (format)
```

**Test:**
```bash
# Query test
python -c "
from src.retrieval.pure_rag import PureRAGRetriever
r = PureRAGRetriever()
results = r.search('test query', as_of=None)
print(results)
"
```

---

### Week 2: API & UI (Days 6-10)
**Goal:** Working UI that accepts queries and shows answers

#### Day 6: API Integration (Dev A)
```bash
# Update src/api/server.py
# Implement:
# - POST /query (retrieval + generation)
# - GET /health
# - GET /ready

# Update main.py
# - Start intake watcher on startup
# - Initialize databases
```

**Test:**
```bash
python main.py --port 8000 &
sleep 2
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "mode": "pure_rag"}'
```

---

#### Day 7: UI Connection (Dev C)
```bash
# Option 1: Streamlit (quickest)
# Update ui_streamlit.py

# Option 2: FastAPI frontend
# Update USER_INTERFACE/app.py
```

**Test:**
```bash
streamlit run ui_streamlit.py
# Open browser: http://localhost:8501
# Query should return answer + citations
```

---

#### Day 8-9: Testing & Bug Fixes (All)
```bash
# Run acceptance tests
uv run pytest -q tests/test_temporal_validity.py tests/test_conflict_resolver.py

# Manual tests:
# 1. Drop file → Process → Query → Answer
# 2. Drop conflicting file → Old superseded, new current
# 3. All 3 retrieval modes return current facts
# 4. Citations include source + timestamp
```

---

#### Day 10: Demo & Handoff
```bash
# Full end-to-end demo:
# 1. Start all services
# 2. Drop files in samples5/
# 3. Open UI
# 4. Query and show results

# Tech Lead verification:
# - All acceptance tests pass
# - Demo works as expected
# - Documentation complete
```

---

## 📋 Tech Lead Daily Checklist

### Morning Standup Questions
- [ ] What did you complete yesterday?
- [ ] What are you working on today?
- [ ] Any blockers?

### End of Day Verification
- [ ] Code merged to main branch
- [ ] Tests pass on main
- [ ] No breaking changes

---

## 🎯 Directives to Assign Today

### To Architect:
**"Review ARCHITECT_DIRECTIVES.md and confirm the implementation approach for each module. Identify any gaps in the design before developers start coding."**

### To Developers:

**Dev A (Pipeline Lead):**
- Day 1: Intake module
- Day 2-3: Extraction module
- Day 6: API integration
- Day 7: UI connection

**Dev B (Data Lead):**
- Day 2: Extraction support
- Day 3-4: Indexing + Retrieval connection
- Day 5: Generation module

**Dev C (Infrastructure Lead):**
- Day 1: Environment setup
- Day 2-3: Database integration
- Day 4-5: Testing support

---

## 📊 Success Criteria

### MVP (Minimum Viable Product) - Day 5
- [ ] Files dropped in `samples5/` are processed
- [ ] Facts appear in Neo4j with temporal attributes
- [ ] Vectors appear in Qdrant
- [ ] Can query via Python and get facts

### Full System - Day 10
- [ ] Working UI (Streamlit or FastAPI)
- [ ] All 3 retrieval modes working
- [ ] Answers include citations with:
  - Source file
  - Page/location
  - Extraction path
  - As-of timestamp
  - Confidence score
- [ ] Temporal correctness verified
- [ ] Acceptance tests passing

---

## 🚨 Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Neo4j/Qdrant setup issues | Medium | High | Start databases on Day 1 |
| Docling dependency issues | Medium | High | Test extraction early |
| Integration bugs | High | Medium | Continuous integration testing |
| Performance bottlenecks | Low | Medium | Optimize after MVP |
| UI complexity | Medium | Low | Start with Streamlit |

---

## 📚 Reference Files

| File | When to Use |
|------|-------------|
| `ARCHITECT_DIRECTIVES.md` | Detailed implementation specs |
| `ARCHITECTURE/01_Technical_Design.md` | System architecture |
| `ARCHITECTURE/05_Directory_Structure.md` | File locations |
| `ARCHITECTURE/07_Milestones.md` | Milestone definitions |
| `ARCHITECTURE/10_Test_Plan.md` | Testing requirements |
| `CODE DIRECTIONS AND PRODUCTS/04_CODE_SCAFFOLDS.md` | Code templates |

---

## 🎯 Tech Lead Action Items - Week 1

### Day 1:
- [ ] Assign developers to phases
- [ ] Verify environment setup
- [ ] Start Dev A on Intake (D1)
- [ ] Start Dev C on Environment (D4)
- [ ] Review extraction design with Dev B

### Day 2:
- [ ] Verify Intake working
- [ ] Start Dev B on Extraction (D2)
- [ ] Verify databases running
- [ ] Code review for Intake

### Day 3:
- [ ] Verify Extraction working
- [ ] Start Dev A on Indexing (D5)
- [ ] Start Dev B on Reconstruction (D3)
- [ ] Code review for Extraction

### Day 4:
- [ ] Verify full pipeline (file → KG)
- [ ] Start Dev A on Retrieval (D6)
- [ ] Start Dev B on Generation (D7)
- [ ] All-hands integration testing

### Day 5:
- [ ] MVP verification
- [ ] All لحosof Day 1-4 completed
- [ ] Week 2 planning

---

## 🚀 Quick Reference Commands

```bash
# Start all services
python main.py --port 8000 &
streamlit run ui_streamlit.py &

# Check services
curl http://localhost:8000/health
curl http://localhost:8501

# Test query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the status of operation plan?",
    "mode": "pure_rag",
    "as_of": null,
    "include_history": false
  }'

# Check queues
sqlite3 data/job_queue.db "SELECT * FROM jobs;"

# Check Neo4j
cypher-shell -u neo4j -p password "MATCH (n) RETURN n LIMIT 10;"

# Check Qdrant
curl http://localhost:6333/collections
```

---

## 🎯 Final Deliverable

**A working Temporal-Valid KG-RAG System that:**
1. ✅ Ingests files from `samples5/` automatically
2. ✅ Extracts facts with timestamps and provenance
3. ✅ Stores facts in Neo4j with temporal validity
4. ✅ Indexes facts in Qdrant
5. ✅ Answers queries through all 3 retrieval modes
6. ✅ Returns answers with citations, timestamps, and provenance
7. ✅ Has a working UI for demo purposes
8. ✅ Passes all acceptance tests

**Tech Lead: Start assigning D1 and D4 today. Everything else depends on these.**
