# 📋 TECH LEAD EXECUTIVE ORDER

## MISSION
Deliver a **working Temporal-Valid KG-RAG System with UI** in **2 weeks**.

---

## EXECUTIVE SUMMARY

**The temporal core is built. The data pipeline is NOT.**

Your team must implement **9 missing components** in the correct order to enable:
```
FILE DROP → INGEST → EXTRACT → RECONSTRUCT → INDEX → RETRIEVE → GENERATE → UI DISPLAY
```

**Current Blockers:**
- ❌ No file ingestion (no data enters system)
- ❌ No document processing (no facts created)
- ❌ No database integration (no storage)
- ❌ No vector indexing (no search)
- ❌ No answer generation (no responses)
- ❌ No UI connection (no visible output)

---

## 🎯 YOUR RESPONSIBILITIES

### Week 1:Unblock Data Flow
1. **Day 1:** Assign D1 (Intake) + D4 (Databases) → **CRITICAL PATH**
2. **Day 2:** Assign D2 (Extraction) → Depends on D1
3. **Day 3:** Assign D3 (Reconstruction) + D5 (Indexing) → Depends on D2
4. **Day 4-5:** Integration testing

### Week 2: Unblock Query-to-Output
1. **Day 6:** Assign D6 (Retrieval) + D7 (Generation)
2. **Day 7:** Assign D8 (API) + D9 (UI)
3. **Day 8-9:** End-to-end testing
4. **Day 10:** Demo and delivery

---

## 📊 DIRECTIVES MATRIX

| Priority | Directive | Module | Assign To | Due | Status | Blocks |
|----------|-----------|--------|-----------|-----|--------|--------|
| 🔴 1 | **D1** | Intake | Dev A | Day 1 | ❌ | All |
| 🔴 2 | **D4** | Databases | Dev C | Day 1 | ❌ | D5, D6 |
| 🔴 3 | **D2** | Extraction | Dev B | Day 2 | ❌ | D3, D5 |
| 🔴 4 | **D3** | Reconstruction | Dev B | Day 3 | ⏳ | D5, D6 |
| 🟡 5 | **D5** | Indexing | Dev C | Day 3 | ❌ | D6 |
| 🟡 6 | **D6** | Retrieval | Dev A | Day 4 | ❌ | D7, D8 |
| 🟡 7 | **D7** | Generation | Dev B | Day 5 | ❌ | D8 |
| 🟡 8 | **D8** | API | Dev A | Day 6 | ❌ | D9 |
| 🟢 9 | **D9** | UI | Dev C | Day 7 | ❌ | Demo |

---

## 🎯 DAILY ORDERS

### Day 1 Orders (TODAY)
- [ ] **Tech Lead:** Assign Dev A to D1 (Intake)
- [ ] **Tech Lead:** Assign Dev C to D4 (Databases)
- [ ] **Tech Lead:** Hold architecture review meeting
- [ ] **Dev A:** Implement `src/intake/watcher.py`, `queue.py`, `router.py`
- [ ] **Dev C:** Install Neo4j, Qdrant, configure `.env`
- [ ] **All:** Verify dependencies (`uv sync`)

**Verification Test:**
```bash
cp SAMPLES/test.txt samples5/
# Should print: "📥 File detected: test.txt - enqueued"
```

---

### Day 2 Orders
- [ ] **Dev B:** Implement `src/extraction/dispatcher.py`, `text.py`
- [ ] **Dev A:** Code review for Dev C's database setup
- [ ] **Dev C:** Add database connection code
- [ ] **Tech Lead:** Verify D1 works

**Verification Test:**
```bash
python -c "
from src.extraction.dispatcher import ExtractionDispatcher
d = ExtractionDispatcher()
result = d.extract('samples5/test.txt')
assert result is not None
print('✅ Extraction works')
"
```

---

### Day 3 Orders
- [ ] **Dev B:** Connect Reconstruction (entity + conflict resolution)
- [ ] **Dev C:** Implement `src/indexing/vector_indexer.py`
- [ ] **Dev A:** Start D2 support if Dev B needs help
- [ ] **Tech Lead:** Verify extraction pipeline

**Verification Test:**
```bash
# Check Neo4j has nodes
cypher-shell -u neo4j -p password "MATCH (n:Fact) RETURN count(n);"
# Should return: > 0
```

---

### Day 4 Orders
- [ ] **Dev A:** Connect Retrieval to KG + Qdrant
- [ ] **Dev B:** Implement `src/generation/answer_gen.py`
- [ ] **Dev C:** Support Dev A on retrieval connection
- [ ] **Tech Lead:** Verify full pipeline (file → indexed fact)

**Verification Test:**
```bash
python -c "
from src.retrieval.pure_rag import PureRAGRetriever
r = PureRAGRetriever()
results = r.search('test')
assert len(results) > 0
print('✅ Retrieval works')
"
```

---

### Day 5 Orders
- [ ] **Dev A:** Complete retrieval integration
- [ ] **Dev B:** Complete generation integration
- [ ] **All:** Integration testing
- [ ] **Tech Lead:** MVP verification

**Verification Test:**
```bash
python -c "
from src.generation.answer_gen import AnswerGenerator
gen = AnswerGenerator()
answer = gen.generate('test query', [])
assert answer.answer is not None
print('✅ Generation works')
"
```

---

### Day 6 Orders
- [ ] **Dev A:** Complete API (`src/api/server.py`, `main.py`)
- [ ] **Tech Lead:** Start UI planning
- [ ] **All:** Review API design

**Verification Test:**
```bash
python main.py --port 8000 &
sleep 2
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"test","mode":"pure_rag"}'
# Should return: {"answer": "...", "facts": [...], "audit_id": "..."}
```

---

### Day 7 Orders
- [ ] **Dev C:** Connect UI to API
- [ ] **Dev A:** Code review for API
- [ ] **Tech Lead:** UI design review

**Verification Test:**
```bash
streamlit run ui_streamlit.py
# Open browser: http://localhost:8501
# Enter query → Should show answer
```

---

### Day 8-9 Orders
- [ ] **All:** Bug fixes and optimization
- [ ] **Tech Lead:** Run acceptance tests
- [ ] **All:** End-to-end testing

**Acceptance Tests:**
```bash
uv run pytest -q tests/test_temporal_validity.py tests/test_conflict_resolver.py
uv run pytest -q tests/test_kg_schema.py tests/test_timestamp_extractor.py
```

---

### Day 10 Orders (DELIVERY DAY)
- [ ] **Tech Lead:** Final verification
- [ ] **Tech Lead:** Conduct demo
- [ ] **All:** Documentation updates
- [ ] **Tech Lead:** Sign off

---

## ✅ PASS/FAIL CRITERIA

### MVP (Day 5)
| Test | Criteria | Pass | Fail |
|------|----------|------|------|
| File Ingestion | Drop file → appears in queue | ✅ | ❌ |
| Extraction | File → NormalizedExtract | ✅ | ❌ |
| KG Storage | Facts in Neo4j with timestamps | ✅ | ❌ |
| Vector Index | Vectors in Qdrant | ✅ | ❌ |

### Full System (Day 10)
| Test | Criteria | Pass | Fail |
|------|----------|------|------|
| Pure RAG | Query → answer with citations | ✅ | ❌ |
| RAG+KG | Query → validated answer | ✅ | ❌ |
| KG-only | Query → graph-based answer | ✅ | ❌ |
| Temporal | Newer file supersedes older | ✅ | ❌ |
| UI | Browser query → visible answer | ✅ | ❌ |

---

## 🚨 ESCALATION TRIGGERS

**Immediate Escalation (Stop work):**
- Database setup fails (Neo4j/Qdrant)
- Core dependencies missing (docling, graphiti)
- Intake module not working after 1 day

**Daily Escalation:**
- Any directive takes > 2x estimated time
- Integration tests failing
- Developers blocked > 2 hours

**Tech Lead Action:**
- Reassign resources
- Adjust timeline
- Simplify scope (see MVP below)

---

## 🎯 MINIMUM VIABLE PRODUCT (MVP)

If timeline is at risk, **extend to 3 weeks** and deliver:

### Week 1 MVP:
- ✅ File ingestion (D1)
- ✅ Text extraction only (D2 - skip audio/video)
- ✅ Basic KG storage (D3, D4)
- ✅ Basic retrieval (D6 - pure_rag only)
- ❌ Generation (skip)
- ❌ UI (skip)

**Test:** Can query via API and get facts

### Week 2 MVP:
- ✅ All extraction paths (D2)
- ✅ All retrieval modes (D6)
- ✅ Generation (D7)
- ✅ API (D8)
- ❌ UI (use curl for demo)

**Test:** Can query via curl and get answer + citations

### Week 3 Full:
- ✅ UI connection (D9)
- ✅ All acceptance tests
- ✅ Demo ready

---

## 📋 RESOURCES FOR TEAM

### For All Developers:
- `UPDATED_MODEL/TECH_LEAD_IMPLEMENTATION_PLAN.md` - Detailed implementation
- `UPDATED_MODEL/ARCHITECT_DIRECTIVES.md` - Technical specifications
- `UPDATED_MODEL/ARCHITECTURE/01_Technical_Design.md` - System architecture
- `UPDATED_MODEL/CODE DIRECTIONS AND PRODUCTS/04_CODE_SCAFFOLDS.md` - Code templates

### For Tech Lead:
- `UPDATED_MODEL/TECH_LEAD_QUICK_START.md` - Daily plans
- `UPDATED_MODEL/ARCHITECTURE/07_Milestones.md` - Milestone definitions
- `UPDATED_MODEL/ARCHITECTURE/10_Test_Plan.md` - Testing requirements

---

## 🎯 IMMEDIATE ACTIONS

### Tech Lead - Next 2 Hours:
1. **Read this document** completely
2. **Read `ARCHITECT_DIRECTIVES.md`** for technical details
3. **Identify your Dev A, Dev B, Dev C**
4. **Create team channels** (Slack/Teams) for each directive
5. **Schedule daily standups** at 9:30 AM
6. **Start Day 1 Orders** immediately

### Dev A - Next 2 Hours:
- Read D1 (Intake) specification
- Create `src/intake/` directory
- Implement `watcher.py`, `queue.py`, `router.py`
- Test with sample files

### Dev C - Next 2 Hours:
- Set up Docker for Neo4j and Qdrant
- Install system dependencies
- Configure `.env` file
- Verify database connections

---

## 📞 COMMUNICATION PLAN

| Meeting | Frequency | Attendees | Purpose |
|---------|-----------|-----------|---------|
| Daily Standup | Daily, 9:30 AM | All | Progress, blockers, next steps |
|Architecture Review | Day 1, 2:00 PM | All | Confirm D1 + D4 approach |
| Integration Sync | Day 3, 2:00 PM | All | Confirm pipeline works |
| API Review | Day 6, 2:00 PM | All | Confirm API design |
| Demo Rehearsal | Day 9, 2:00 PM | All | Dry run before delivery |
| Delivery Review | Day 10, 10:00 AM | Tech Lead + Stakeholders | Final demo |

---

## 🚀 SUCCESS DEFINITION

**On Day 10 at 5:00 PM, you will have:**

✅ **Working System:**
- Files dropped in `samples5/` are processed automatically
- Facts stored in Neo4j with temporal attributes
- Vectors stored in Qdrant
- All 3 retrieval modes working
- Answers include citations with source, timestamp, confidence

✅ **Working UI:**
- Accessible at `http://localhost:8501` (Streamlit)
- Users can enter queries
- Results display with proper formatting
- All three modes selectable

✅ **Verification:**
- All acceptance tests pass
- Demo script works
- Documented

---

## 💡 TECH LEAD MANTRA

> **"D1 and D4 first. Everything else depends on getting data into the system."**

---

## 🎯 FINAL ORDER

**TECH LEAD: Assign D1 and D4 today. Start coding immediately. Report progress at 5:00 PM today.**

**The clock is running. 2 weeks. Go.**
