---
format: html
---

# 06_Tech_Lead_Tickets.md - Tech Lead Implementation Tickets

## Gating Policy
All P0 tickets must be completed, tested, and reviewed before any P1 tickets can start. Temporal validity is the primary gating criterion.

## Developer Tickets

### DEV-P0-01 Locate and Wrap extract.py
Priority: P0
Description: Locate existing extract.py in repository. Analyze timestamp extraction logic. Create TimestampExtractor wrapper class that calls extract.py and provides fallback to os.path.getmtime with timestamp_fallback flag.
Acceptance Criteria:
- Wrapper exposes get_as_of(file_path) -> datetime
- Returns timestamp_fallback boolean
- Works for PDF, DOCX, TXT files in samples5/
- Unit test covers missing timestamp case
Dependencies: None

### DEV-P0-02 Knowledge Graph Schema Setup
Priority: P0
Description: Initialize Neo4j instance. Create constraints and indexes for Entity, Fact, Provenance nodes. Ensure temporal attributes as_of, valid_from, valid_to, current, supersedes, superseded_by are present.
Acceptance Criteria:
- Schema creates successfully
- Sample fact insertion succeeds with all temporal attributes
- Cypher query for current facts works
Dependencies: None

### DEV-P0-03 Temporal Conflict Resolution Engine
Priority: P0
Description: Implement upsert_fact service that detects conflicts by subject+predicate, compares as_of, promotes newer fact, demotes older fact, creates supersedes edges, maintains current flag invariant.
Acceptance Criteria:
- Newer as_of promotes and demotes correctly
- Supersedes edge created
- valid_to set on demoted fact
- Transactional per entity-predicate
Dependencies: DEV-P0-02

### DEV-P0-04 Intake & File Watcher
Priority: P0
Description: Implement watchdog for samples5/. On create/modify, emit IngestionEvent with file_path, as_of from TimestampExtractor, ingestion_time.
Acceptance Criteria:
- File creation triggers event
- Event contains correct as_of
Dependencies: DEV-P0-01

### DEV-P0-05 Hierarchical Indexing with Temporal Payload
Priority: P0
Description: Set up Qdrant collection. Generate embeddings for normalized facts. Store payload with fact_id, current, as_of, source_file. Implement update on supersession.
Acceptance Criteria:
- Filter by current=true works
- Payload updated when fact superseded
Dependencies: DEV-P0-03

### DEV-P0-06 Pure RAG Retriever with Temporal Filter
Priority: P0
Description: Implement Pure RAG retriever that queries Qdrant with filter current=true, post-filters results, re-ranks by recency boost.
Acceptance Criteria:
- Returns only current facts
- Superseded facts never returned
Dependencies: DEV-P0-05

### DEV-P0-07 KG-only Retriever
Priority: P0
Description: Implement KG-only retriever using Cypher WHERE f.current = true. Return facts with provenance and temporal justification.
Acceptance Criteria:
- Queries return current facts only
- Answer includes source_file and as_of
Dependencies: DEV-P0-03

### DEV-P0-08 RAG + KG Validator Retriever
Priority: P0
Description: Implement validator that runs Pure RAG then validates each candidate against KG current fact for same subject/predicate, overrides if mismatch.
Acceptance Criteria:
- Stale RAG candidate overridden by KG current fact
- Final answer cites KG fact_id and timestamp
Dependencies: DEV-P0-06, DEV-P0-07

### DEV-P0-09 End-to-End Incremental Update Flow
Priority: P0
Description: Wire Intake → Extraction → Enrichment → Conflict Resolution → Index Update. Ensure atomic update and immediate visibility to retrieval.
Acceptance Criteria:
- New file with conflicting fact updates KG and index
- Old fact current=false
- All three retrieval modes reflect change
Dependencies: DEV-P0-04, DEV-P0-03, DEV-P0-05

### DEV-P1-10 Multi-path Extraction
Priority: P1
Description: Implement text, table, VLM extractors returning RawFacts with extraction_path tag.
Acceptance Criteria:
- Extractors produce facts
Dependencies: DEV-P0-04

### DEV-P1-11 VLM Enrichment & Reconstruction
Priority: P1
Description: Integrate VLM and spaCy for normalization and canonical entity IDs.
Acceptance Criteria:
- Normalized triples produced
Dependencies: DEV-P1-10

## Tester Tickets

### TEST-P0-01 Temporal Validity Unit Tests
Priority: P0
Description: Write unit tests for conflict resolution engine covering newer, older, same timestamp scenarios.
Acceptance Criteria:
- TC-1 newer file update passes
- TC-2 older file arrives later passes
- TC-3 out-of-order ingestion passes
- TC-4 tie-break deterministic
Dependencies: DEV-P0-03

### TEST-P0-02 Retrieval Mode Temporal Tests
Priority: P0
Description: Test Pure RAG, RAG+KG, KG-only return only current facts after supersession.
Acceptance Criteria:
- All three modes return identical current fact
- Superseded facts never returned by default
Dependencies: DEV-P0-06, DEV-P0-07, DEV-P0-08

### TEST-P0-03 Incremental Update Integration Tests
Priority: P0
Description: Simulate file addition to samples5/ and verify supersession chain, current flags, and explainability.
Acceptance Criteria:
- Supersedes edges correct
- Answers include provenance and as_of
Dependencies: DEV-P0-09

### TEST-P1-04 Evaluation Band Tests
Priority: P1
Description: Run existing Evaluation Band metrics on final system.
Acceptance Criteria:
- Metrics meet baseline
Dependencies: DEV-P0-09

## Reviewer Tickets

### REV-P0-01 Temporal Correctness Review
Priority: P0
Description: Review conflict resolution logic, current flag enforcement, retrieval filters. Verify no path returns superseded facts by default.
Acceptance Criteria:
- Code review sign-off on DEV-P0-03, DEV-P0-06, DEV-P0-07, DEV-P0-08
- Explainability requirement verified
Dependencies: DEV-P0-03, DEV-P0-06, DEV-P0-07, DEV-P0-08

### REV-P1-02 Architecture Compliance Review
Priority: P1
Description: Verify full pipeline matches approved Architecture and Design.
Acceptance Criteria:
- All components integrated per design
- Documentation updated
Dependencies: DEV-P0-09

## Tech Lead Handover

The following tickets are formally handed over:

To Developer:
DEV-P0-01 through DEV-P0-09, DEV-P1-10, DEV-P1-11

To Tester:
TEST-P0-01, TEST-P0-02, TEST-P0-03, TEST-P1-04

To Reviewer:
REV-P0-01, REV-P1-02

Gating requirement: No P1 work may start until all P0 tickets are completed, tested, and reviewed with sign-off.

Proceed to Developer/Tester/Reviewer loop.

---
Status: Draft awaiting human approval
