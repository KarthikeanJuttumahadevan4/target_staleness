# 03_Specifications.md - Technical Specification

## 1. Purpose and Scope
Precise technical specification for temporal-valid Knowledge Graph RAG system with multi-path extraction. Defines KG schema, temporal rules, conflict resolution algorithms, retrieval enforcement, and incremental update flow.

## 2. System Overview
Pipeline: Intake → Multi-path Extraction → VLM Enrichment → Reconstruction → Hierarchical Indexing → Hybrid Retrieval

Hybrid Retrieval modes:
1. Pure RAG
2. RAG + KG Validator
3. KG-only

Temporal validity is enforced at KG level and propagated to all retrieval modes.

## 3. Knowledge Graph Schema

### 3.1 Core Nodes

**Entity**
- entity_id: string, canonical identifier
- entity_type: string
- canonical_name: string
- created_at: datetime
- metadata: dict

**Fact / Triple**
- fact_id: uuid
- subject_entity_id: string
- predicate: string
- object_value: string | number | boolean | entity_id
- object_type: string

**Provenance**
- provenance_id: uuid
- source_file_path: string
- extraction_path: enum [text, table, vlm]
- model_version: string
- extraction_timestamp: datetime

### 3.2 Temporal Attributes - Mandatory per Fact
- as_of: datetime, from `extract.py` file modification timestamp
- valid_from: datetime, defaults to as_of on creation
- valid_to: datetime | null
- current: boolean
- supersedes: list<fact_id>
- superseded_by: fact_id | null

### 3.3 Edges
- `has_fact`: Entity → Fact
- `supersedes`: Fact → Fact
- `derived_from`: Fact → Provenance
- `replaces`: Fact → Fact [alias of supersedes]

Schema constraints:
- current = true iff valid_to is null
- If current = false, superseded_by must be non-null
- valid_from <= as_of <= valid_to or valid_to is null

## 4. extract.py Integration

Specification:
- Function: `get_file_timestamps(file_path) -> { modified: datetime, created: datetime }`
- Called during Intake for each file.
- `as_of` for all facts derived from file = modified timestamp.
- If timestamp unavailable, use ingestion time and set flag `timestamp_fallback=true`.
- Timestamp stored in Provenance and copied to Fact.as_of.

## 5. Conflict Detection and Resolution Algorithm

### 5.1 Conflict Definition
Two facts F1 and F2 conflict iff:
- subject_entity_id equal
- predicate equal
- object_value not equal
- facts are not already linked via supersedes

### 5.2 Detection Procedure
On ingestion of new batch B:
1. For each fact f in B:
   a. Query KG: SELECT fact_id FROM facts WHERE subject= f.subject AND predicate= f.predicate AND current=true
   b. If no match → insert as new current fact
   c. If match exists with same object_value → no change, update provenance link
   d. If match exists with different object_value → conflict

### 5.3 Resolution Procedure - Most-Recent-Wins
Given conflicting existing fact E and new fact N:
1. Compare E.as_of vs N.as_of
2. If N.as_of > E.as_of:
   - Set E.current = false
   - E.valid_to = N.as_of
   - E.superseded_by = N.fact_id
   - Set N.current = true
   - N.valid_from = N.as_of
   - N.supersedes = [E.fact_id]
3. If N.as_of < E.as_of:
   - Discard N or insert as historical non-current fact with current=false, valid_to=E.as_of
   - Log demotion
4. If N.as_of == E.as_of:
   - Tie-break by source_file_path lexical order
   - Log ambiguity
   - Promote tie-winner, demote loser

Atomicity: Resolution must be transactional per entity-predicate.

## 6. Incremental Update Flow

Trigger: file added/modified in samples5/

Step 1 Intake
- Detect file change via watcher
- Call extract.py → get as_of
- Create Provenance record

Step 2 Multi-path Extraction
- Extract facts via text/table/vlm paths
- Attach provenance_id

Step 3 VLM Enrichment & Reconstruction
- Normalize entities, resolve coreferences
- Output canonical triples

Step 4 Temporal Conflict Resolution
- Run detection & resolution algorithm per section 5
- Update current flags and validity intervals

Step 5 Hierarchical Indexing
- Update vector store with fact text for current=true facts only
- Update KG with new facts and supersession edges
- Update hierarchical index metadata

Step 6 Retrieval Ready
- System now serves queries with updated current facts

## 7. Retrieval Mode Enforcement

### 7.1 Common Filter
All retrieval queries must include predicate `current=true` unless `include_historical=true` explicitly set by user.

### 7.2 Pure RAG
Implementation:
- Vector search returns top-k candidates with fact_id
- Post-filter: keep only candidates where fact.current=true
- Re-rank: boost score by recency: score' = score * recency_weight(as_of)
- If filtered set empty, return empty with explanation

### 7.3 RAG + KG Validator
Implementation:
- Candidate answer from RAG with supporting fact_ids
- For each candidate fact, query KG for current fact with same subject/predicate
- If KG current fact object differs from RAG candidate → override with KG fact
- Final answer cites KG fact_id, as_of, source_file_path
- Temporal justification included

### 7.4 KG-only
Implementation:
- Query: MATCH (e)-[f]->() WHERE f.current=true AND e.name = ...
- Return facts with temporal metadata
- No vector involvement
- Default excludes superseded facts

## 8. Acceptance Criteria

AC-TEMP-1: Every fact stored has as_of, valid_from, valid_to, current, provenance.
AC-TEMP-2: On new file with newer timestamp conflicting fact, old fact current=false, new fact current=true.
AC-TEMP-3: Supersedes edges exist and are traversable.
AC-TEMP-4: All three retrieval modes return only current facts by default.
AC-TEMP-5: Answers include source file and as_of timestamp.
AC-TEMP-6: Historical query with explicit flag returns superseded facts with validity interval.

## 9. Temporal Correctness Test Cases

TC-1 Newer file update
- Initial fact A as_of 2024-01-01 current=true
- Ingest file with fact B same entity/predicate different value as_of 2024-06-01
- Expected: A current=false, valid_to=2024-06-01, B current=true
- All three modes return B

TC-2 Older file arrives later
- Current fact C as_of 2024-06-01
- Ingest file with fact D same entity/predicate as_of 2024-02-01
- Expected: D inserted with current=false, C unchanged
- Retrieval returns C

TC-3 Out-of-order ingestion
- Ingest 2024-09-01 then 2024-03-01 then 2024-12-01
- Expected final current fact is 2024-12-01, supersession chain length 3

TC-4 Retrieval mode consistency
- Same query executed on Pure RAG, RAG+KG, KG-only
- Expected identical current fact returned

TC-5 Explainability
- Query returns answer with citation: source_file, as_of, supersedes chain

## 10. Non-Functional Requirements

- Consistency: Current flag invariant maintained
- Auditability: Superseded facts never deleted
- Performance: Incremental update < 5s per file for samples5 size
- Traceability: Full provenance chain per fact

## 11. Interfaces

- Ingestion API: ingest_file(file_path)
- Query API: query(question, mode, include_historical=false)
- KG API: get_fact_history(entity_id, predicate)

## 12. Open Items

- Final choice of KG technology and vector store
- Entity canonicalization rules

Ready for Stage 4 – Architect / Design.

---
Status: Draft awaiting human approval
