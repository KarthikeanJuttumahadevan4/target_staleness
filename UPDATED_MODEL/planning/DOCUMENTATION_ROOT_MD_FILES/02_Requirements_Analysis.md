---
format: html
---

# 02_Requirements_Analysis.md - Requirements Analysis

## Purpose
Deep requirements analysis to confirm feasibility and completeness of temporal-valid Knowledge Graph RAG system. This analysis explicitly covers `extract.py` integration, temporal modelling, conflict detection/resolution, retrieval mode behaviour, and evaluation criteria.

## 1. Context and Assumptions

**Existing Assets**
- `extract.py` exists and extracts edit/modification timestamps from file metadata. It must be located, reused, and optionally improved for reliability.
- `samples5/` directory will be used for ingestion and incremental updates.
- Knowledge Graph and vector store are to be implemented/selected.

**Assumptions**
- Files have reliable modification timestamps. If missing, fallback to ingestion time with explicit flag.
- Entity identity can be established via normalized identifiers, e.g., name + type + context.
- VLM Enrichment and Multi-path Extraction produce structured output suitable for KG ingestion.
- Human validation occurs after each major artifact.

## 2. Functional Requirements

### 2.1 Intake
FR-I1: System monitors `samples5/` for new files and modifications.
FR-I2: On change, system triggers incremental ingestion pipeline for affected file only.
FR-I3: Intake records ingestion timestamp and file path as provenance.

### 2.2 Multi-path Extraction
FR-E1: Extract structured facts via multiple paths: text extraction, table extraction, VLM extraction.
FR-E2: Each extracted fact is associated with source file, extraction path, and model version.
FR-E3: `extract.py` is invoked to obtain file edit/modification timestamp. Timestamp is stored as `as_of` for all facts from that file.

### 2.3 VLM Enrichment & Reconstruction
FR-V1: Enrich extracted raw facts into normalized entities and relations.
FR-V2: Reconstruction step resolves coreferences and normalizes values.
FR-V3: Output schema is compatible with KG ingestion.

### 2.4 Temporal Modelling in Knowledge Graph

Mandatory temporal attributes per fact / triple:
- `fact_id`: unique identifier
- `entity_id` / `relation_id`
- `value` / `predicate` / `object`
- `provenance`: source_file, extraction_path, model_version
- `as_of`: timestamp from file metadata via `extract.py`
- `valid_from`: timestamp when fact became current
- `valid_to`: nullable, set when superseded
- `current`: boolean flag, true if fact is authoritative now
- `supersedes`: list of fact_ids this fact replaces
- `superseded_by`: nullable fact_id

Temporal modelling requirements:
FR-T1: Every extracted information unit must be linked to provenance and as-of timestamp.
FR-T2: Validity interval is maintained: [valid_from, valid_to) with valid_to = null for current.
FR-T3: Supersedes edges exist between conflicting versions.
FR-T4: Current flag is always consistent with validity interval.

### 2.5 Conflict Detection and Resolution

Conflict definition:
Two facts conflict if they share same entity identity and predicate but have different object values.

FR-C1: On ingestion, system queries KG for existing facts with same entity and predicate.
FR-C2: If conflict found, compare `as_of` timestamps. Higher `as_of` wins.
FR-C3: Promotion rule: new fact set current=true, valid_from=as_of, supersedes=[old_fact_id]. Old fact set current=false, valid_to=as_of, superseded_by=new_fact_id.
FR-C4: If timestamps equal, tie-break by provenance priority or ingestion order, and log ambiguity.
FR-C5: Conflict detection must be deterministic and auditable.

Policy:
- Most-recent-wins is default.
- Older versions retained for audit, never deleted.
- Flagging must be explicit and queryable.

### 2.6 Hierarchical Indexing
FR-H1: Vector embeddings are generated from reconstructed facts.
FR-H2: Vector index stores reference to fact_id and current flag at indexing time.
FR-H3: On supersession, vector index is updated to demote superseded facts or filter them at query time.

### 2.7 Hybrid Retrieval with Three Modes

Common requirement:
FR-R0: All three modes default to current=true facts only unless user explicitly requests historical view.

Mode 1 – Pure RAG
FR-R1: Retrieve top-k chunks from vector store.
FR-R1a: Filter or re-rank results to prefer current=true facts.
FR-R1b: If a superseded fact is retrieved, it must be discarded or demoted below current version.

Mode 2 – RAG + KG Validator
FR-R2: Retrieve candidate answers via RAG.
FR-R2a: Validator checks KG for current facts matching entities/predicates in candidate answer.
FR-R2b: If KG current fact contradicts RAG candidate, KG fact overrides.
FR-R2c: Final answer must cite KG current fact with timestamp and source.

Mode 3 – KG-only
FR-R3: Query KG directly with current=true predicate.
FR-R3a: Results must be filtered by current flag before returning.
FR-R3b: Answer includes provenance and as-of timestamp justification.

### 2.8 Explainability
FR-X1: Every answer must be able to explain why it is current: cite source file, as-of timestamp, and supersession chain if applicable.
FR-X2: Provide “why this is the current answer” field in response.

## 3. Non-Functional Requirements

NFR-1 Temporal Correctness: 100% of answers default to most recent flagged version across all modes.
NFR-2 Auditability: Full history of supersession retained, queryable.
NFR-3 Consistency: Current flag and validity intervals remain consistent after incremental updates.
NFR-4 Performance: Incremental ingestion completes within acceptable time for single file in samples5.
NFR-5 Traceability: All facts traceable to source file and extraction path.

## 4. Evaluation Criteria

### 4.1 Temporal Correctness Tests
TC-1 New file arrives with updated fact → old fact flagged superseded, all three modes return new fact.
TC-2 Multiple conflicting updates arrive out of order → system resolves by as-of timestamp, not ingestion order.
TC-3 Query for historical version explicitly → system returns superseded fact with validity interval.
TC-4 Same timestamp conflict → system logs ambiguity and applies deterministic tie-break.

### 4.2 Retrieval Mode Tests
RM-1 Pure RAG returns only current facts.
RM-2 RAG+KG Validator overrides stale RAG hit with KG current fact.
RM-3 KG-only never returns superseded facts by default.

### 4.3 Evaluation Band Metrics
In addition to temporal tests, system must meet existing Evaluation Band metrics for relevance, faithfulness, and coverage.

## 5. Open Questions and Risks

Q1: What is exact schema of existing `extract.py`? Does it support all file types in samples5?
Q2: How to define entity identity for conflict detection? Need canonicalization rules.
Q3: Vector store update strategy: delete/reindex superseded facts vs filter at query time?
Q4: Handling of partial updates where file changes only a subset of facts.

Risks:
- R1: Unreliable file timestamps → fallback strategy needed.
- R2: VLM Enrichment hallucinations creating spurious conflicts.
- R3: Performance degradation with long supersession chains.

## 6. Constraints

- Must reuse `extract.py` timestamp extraction.
- Most-recent-wins policy is non-negotiable.
- Human validation required after each artifact.
- Prefer battle-tested open-source components.

## 7. Conclusion

Requirements analysis confirms temporal validity can be achieved by:
- Mandatory temporal attributes and current flag in KG
- Deterministic conflict detection and promotion/demotion rules driven by `extract.py` timestamps
- Retrieval layer enforcement of current=true across all three modes

Ready for Stage 3 – Specifications.

---
Status: Draft awaiting human approval
