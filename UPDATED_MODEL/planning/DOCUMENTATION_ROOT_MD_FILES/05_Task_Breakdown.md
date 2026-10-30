---
format: html
---

# 05_Task_Breakdown.md - Task Breakdown

## Purpose
Break Architecture and Design into ordered implementation tasks prioritized by temporal validity. Tasks are grouped by role and include dependencies, acceptance criteria, and effort estimates.

## Prioritization Principle
All temporal-validity components are P0. Non-temporal features are P1.

## Phase 1: Foundation & Temporal Core

### T1.1 - Locate and Wrap extract.py
Role: Developer
Priority: P0
Description: Locate existing extract.py, understand timestamp extraction logic, create TimestampExtractor wrapper with fallback.
Dependencies: None
Acceptance Criteria:
- Wrapper returns as_of datetime for all supported file types
- Fallback flag set when timestamp unavailable
- Unit tests pass for sample files
Effort: S

### T1.2 - Set up Knowledge Graph Schema
Role: Developer
Priority: P0
Description: Initialize Neo4j, create Entity, Fact, Provenance nodes and relationships, enforce temporal attributes.
Dependencies: None
Acceptance Criteria:
- Schema constraints validated
- Sample nodes insertable with as_of, valid_from, valid_to, current, supersedes
Effort: M

### T1.3 - Implement Temporal Conflict Resolution Engine
Role: Developer
Priority: P0
Description: Implement upsert_fact with conflict detection, most-recent-wins promotion/demotion, supersedes edge creation.
Dependencies: T1.2
Acceptance Criteria:
- Newer as_of promotes and demotes older fact
- Supersedes edges created
- Current flag invariant maintained
Effort: L

## Phase 2: Extraction Pipeline

### T2.1 - Intake & File Watcher
Role: Developer
Priority: P0
Description: Implement watchdog for samples5/, emit IngestionEvent with timestamp from extract.py.
Dependencies: T1.1
Acceptance Criteria:
- New file detection triggers pipeline
- Event contains as_of and provenance
Effort: S

### T2.2 - Multi-path Extraction
Role: Developer
Priority: P1
Description: Implement text, table, VLM extractors returning RawFacts.
Dependencies: T2.1
Acceptance Criteria:
- Extractors produce facts with extraction_path tag
Effort: M

### T2.3 - VLM Enrichment & Reconstruction
Role: Developer
Priority: P1
Description: Integrate VLM for enrichment and spaCy for normalization.
Dependencies: T2.2
Acceptance Criteria:
- Normalized triples produced with canonical entity IDs
Effort: M

## Phase 3: Indexing & Retrieval

### T3.1 - Hierarchical Indexing with Temporal Payload
Role: Developer
Priority: P0
Description: Set up Qdrant, generate embeddings, store payload with current and as_of.
Dependencies: T1.3
Acceptance Criteria:
- Index supports filter by current=true
- Supersession updates payload
Effort: M

### T3.2 - Pure RAG Retriever with Temporal Filter
Role: Developer
Priority: P0
Description: Implement Pure RAG that filters Qdrant results to current=true and re-ranks by recency.
Dependencies: T3.1
Acceptance Criteria:
- Returns only current facts
- Superseded facts never returned
Effort: M

### T3.3 - KG-only Retriever
Role: Developer
Priority: P0
Description: Implement Cypher queries with WHERE current=true.
Dependencies: T1.3
Acceptance Criteria:
- Returns current facts only
- Includes temporal justification
Effort: S

### T3.4 - RAG + KG Validator Retriever
Role: Developer
Priority: P0
Description: Implement validator that overrides RAG candidates with KG current facts.
Dependencies: T3.2, T3.3
Acceptance Criteria:
- Stale RAG hits overridden by KG current fact
- Answer cites timestamp and source
Effort: M

## Phase 4: Incremental Update Flow

### T4.1 - End-to-End Incremental Update
Role: Developer
Priority: P0
Description: Wire Intake → Extraction → Conflict Resolution → Index Update.
Dependencies: T2.1, T1.3, T3.1
Acceptance Criteria:
- New file with conflicting fact updates KG and index
- Old fact flagged superseded
- All three retrieval modes reflect change immediately
Effort: L

## Phase 5: Testing

### T5.1 - Temporal Validity Unit Tests
Role: Tester
Priority: P0
Description: Test conflict resolution engine with newer/older/same timestamps.
Dependencies: T1.3
Acceptance Criteria:
- TC-1 to TC-4 pass
Effort: M

### T5.2 - Retrieval Mode Temporal Tests
Role: Tester
Priority: P0
Description: Test Pure RAG, RAG+KG, KG-only return only current facts.
Dependencies: T3.2, T3.3, T3.4
Acceptance Criteria:
- All three modes return identical current fact after update
Effort: M

### T5.3 - Incremental Update Integration Tests
Role: Tester
Priority: P0
Description: Add file to samples5/ and verify supersession chain.
Dependencies: T4.1
Acceptance Criteria:
- Supersedes edges correct
- Answers include provenance and as_of
Effort: M

### T5.4 - Evaluation Band Tests
Role: Tester
Priority: P1
Description: Run existing Evaluation Band metrics.
Dependencies: T4.1
Acceptance Criteria:
- Metrics meet baseline
Effort: S

## Phase 6: Review

### T6.1 - Temporal Correctness Review
Role: Reviewer
Priority: P0
Description: Review conflict resolution logic, current flag enforcement, and retrieval filters.
Dependencies: T1.3, T3.2, T3.3, T3.4
Acceptance Criteria:
- No path returns superseded facts by default
- Explainability requirement met
Effort: M

### T6.2 - Architecture Compliance Review
Role: Reviewer
Priority: P1
Description: Verify pipeline matches approved design.
Dependencies: T4.1
Acceptance Criteria:
- All components integrated per design
Effort: S

## Dependencies Summary

T1.1 → T2.1
T1.2 → T1.3 → T3.1, T3.3, T5.1
T1.3 → T4.1
T3.1 → T3.2 → T3.4
T3.3 → T3.4
T4.1 → T5.3

## Effort Key
S = Small < 1 day
M = Medium 1-3 days
L = Large 3-5 days

## Handover to Tech Lead

Tech Lead is requested to:
1. Create detailed tickets for Developer, Tester, Reviewer based on tasks above
2. Ensure P0 temporal-validity tasks are scheduled first and gated
3. Enforce acceptance criteria before progressing to next phase
4. Coordinate Developer-Tester-Reviewer loop for temporal correctness

Task breakdown complete and ready for Tech Lead planning.

---
Status: Draft awaiting human approval
