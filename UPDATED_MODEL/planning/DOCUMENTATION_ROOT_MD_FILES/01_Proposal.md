---
format: html
---

# 01_Proposal.md - Project Proposal

## Project Name
Temporal-Valid Knowledge Graph RAG System with Multi-Path Extraction

## 1. Restatement of Full Goal

Build a production system whose runtime behaviour matches the technical pipeline:

**Intake → Multi-path Extraction → VLM Enrichment → Reconstruction → Hierarchical Indexing → Hybrid Retrieval**

Hybrid Retrieval operates in three modes:
1. Pure RAG
2. RAG + KG Validator
3. KG-only

The system must be engineered through the OpenSpec-inspired agent pipeline:

**Proposal → Analyst → Specifications → Architect → Design → Planner → Tasks → Tech Lead → Developer | Tester | Reviewer**

Human validation is mandatory after each major intermediate artifact. The final deliverable is a working repository that can ingest and incrementally update a `samples5/` directory and answer questions using any of the three retrieval modes.

## 2. Highest-Priority Requirement: Temporal Validity

Temporal validity is #1 priority, above all other features.

The system already possesses `extract.py` that extracts edit/modification timestamps from file metadata and stores them in the Knowledge Graph. This capability will be located, reused and improved if necessary.

Every piece of extracted information must be linked to:
- Provenance: source file, extraction path, model used
- Temporal validity: as-of timestamp from file metadata, validity interval, and current/superseded flag

When new files are added that contain conflicting or updated information, the system must:
1. Detect conflict via the Knowledge Graph using entity/relation identity and provenance
2. Flag the most recent information as current and authoritative
3. Mark older versions as outdated / superseded while retaining them for audit
4. Default to the most recent, flagged version in all three retrieval modes when answering

The agent must always be able to explain “why this is the current answer” by citing timestamp and source that made it the latest.

Most-recent-wins + explicit flagging of outdated data is non-negotiable and must be designed, implemented, tested and demonstrated first-class.

## 3. Temporal Behaviour Across Components

**Ingestion / Incremental Update**
- Intake watches for new or modified files in `samples5/`
- Multi-path Extraction extracts structured facts
- `extract.py` timestamp extraction provides file modification/edit date
- VLM Enrichment and Reconstruction produce normalized entities/relations
- Hierarchical Indexing writes to vector store and Knowledge Graph with temporal attributes

**Conflict Detection and Resolution**
- On each ingestion, compare extracted facts against existing KG nodes/edges by entity identity
- If semantic conflict exists, compare as-of timestamps
- Promote newer fact to current=true, supersedes older
- Demote older fact to current=false, superseded_by=<new>, validity_end=<new as-of>
- Retain full history for audit

**Retrieval Modes – Temporal Default**
All three retrieval modes must filter or re-rank to prefer current=true facts:
- Pure RAG: vector index stores only current facts or re-ranks by temporal flag
- RAG + KG Validator: validator checks KG current flag and overrides stale RAG hits
- KG-only: queries KG with current=true predicate by default

Historical versions are accessible only on explicit user request for history.

## 4. Success Criteria

- System ingests initial `samples5/` and builds KG + vector index with timestamps
- Adding a newer file with conflicting information automatically flags old facts as superseded
- All three retrieval modes return the newest information by default
- Answers include provenance and timestamp justification
- Evaluation Band metrics are met, with additional temporal correctness tests

## 5. Scope Boundaries

In-scope:
- Reuse/improve `extract.py` timestamp extraction
- Temporal modelling in KG
- Conflict detection, promotion/demotion logic
- Temporal-aware retrieval for three modes
- Incremental update pipeline

Out-of-scope for this proposal stage:
- Specific model choices, UI, deployment

## 6. Next Stage

Awaiting human validation of this proposal before proceeding to Stage 2 – Analyst and `02_Requirements_Analysis.md`.

---
Status: Draft awaiting human approval
