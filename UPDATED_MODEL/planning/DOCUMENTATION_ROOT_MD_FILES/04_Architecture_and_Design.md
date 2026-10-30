---
format: html
---

# 04_Architecture_and_Design.md - Architecture and Design

## 1. High-Level Architecture Overview

The system implements the technical pipeline:

**Intake → Multi-path Extraction → VLM Enrichment → Reconstruction → Hierarchical Indexing → Hybrid Retrieval**

All components are orchestrated around a central Temporal Knowledge Graph that stores facts with validity intervals and current/superseded flags. Temporal validity is the central cross-cutting concern.

Component layers:
1. Ingestion Layer
2. Extraction & Enrichment Layer
3. Knowledge Layer [KG + Vector Store]
4. Retrieval Layer [Three Modes]
5. Orchestration & API Layer

## 2. Technology Choices

### Knowledge Graph Store
**Choice: Neo4j Community Edition**
Justification: Native graph model, property graph supports temporal attributes, mature Cypher query language, good support for supersedes edges and history traversal. Alternative: Apache AGE, but Neo4j provides proven tooling.

### Vector Store
**Choice: Qdrant**
Justification: Open-source, fast ANN search, payload filtering allows filtering by current=true and as_of at query time, easy re-indexing. Alternative: FAISS, but Qdrant provides managed payload.

### Extraction Libraries
- **Text extraction**: PyPDF2 / pdfplumber for PDFs, python-docx for DOCX, python-pptx for PPTX
- **Table extraction**: Camelot / Tabula-py
- **Multi-path orchestration**: LangChain Document Loaders

### VLM Enrichment
**Choice: Hugging Face Transformers with open-source VLM**
- Candidate: Qwen2-VL-7B or LLaVA-1.6
Justification: Open-source, can run locally, capable of entity/relation extraction from images/tables. Configurable.

### Reconstruction & Normalization
**Choice: spaCy + custom rules**
Justification: NER, coreference resolution, entity canonicalization.

### Orchestration
**Choice: Python 3.11 + FastAPI**
Justification: Simple API, async support for ingestion pipeline.

### File Watcher
**Choice: watchdog**
Justification: Cross-platform file system events for samples5/.

## 3. Component Design

### 3.1 Intake Module
Responsibilities:
- Watch samples5/ for create/modify events
- Invoke `extract.py` to obtain file metadata timestamps
- Emit IngestionEvent { file_path, as_of, file_hash, ingestion_time }

Integration with extract.py:
- Existing extract.py function get_file_timestamps() is wrapped as TimestampExtractor
- Improved version adds fallback to os.path.getmtime with flag timestamp_fallback
- Timestamp becomes canonical as_of for all facts from file

Interface:
`ingest_file(path) -> IngestionEvent`

### 3.2 Multi-path Extraction Module
Responsibilities:
- Dispatch file to text, table, VLM extractors
- Each extractor returns RawFact { text, span, extraction_path, provenance_id }
- Attach as_of from Intake

### 3.3 VLM Enrichment & Reconstruction Module
Responsibilities:
- Enrich raw facts into structured triples
- Canonicalize entity IDs via entity resolver
- Output NormalizedFact { subject_entity_id, predicate, object_value, provenance_id, as_of }

### 3.4 Temporal Knowledge Graph Module
Responsibilities:
- Persist entities, facts, provenance
- Enforce temporal schema
- Execute conflict detection & resolution

Core procedures:
`upsert_fact(fact)` → runs conflict detection algorithm
`promote_fact(new_fact, old_fact)` → updates flags and supersedes edges
`get_current_facts(entity, predicate)` → returns current=true only

### 3.5 Hierarchical Indexing Module
Responsibilities:
- Generate embeddings for normalized facts
- Store in Qdrant with payload: fact_id, current, as_of, source_file
- On supersession: update payload current=false or re-index

### 3.6 Retrieval Layer

**Pure RAG Retriever**
- Query Qdrant with filter `current=true`
- Post-filter ensures payload.current=true
- Re-rank by hybrid score + recency boost

**RAG + KG Validator Retriever**
- Step 1: RAG retrieval as above
- Step 2: For each candidate fact_id, fetch KG current fact for same subject/predicate
- Step 3: If mismatch, replace with KG current fact
- Step 4: Return validated answer with temporal justification

**KG-only Retriever**
- Direct Cypher query with `WHERE f.current = true`
- No vector involvement
- Returns facts with provenance and as_of

All modes expose common interface:
`retrieve(question, mode, include_historical=False) -> Answer { text, citations, temporal_justification }`

## 4. Data Flow

### 4.1 Initial Load
1. Scan samples5/ recursively
2. For each file:
   a. Intake → TimestampExtractor → as_of
   b. Multi-path Extraction → RawFacts
   c. VLM Enrichment → NormalizedFacts
   d. KG upsert with conflict resolution against existing facts
   e. Indexing → Qdrant upsert
3. Build hierarchical index

### 4.2 Incremental Update
1. Watchdog detects file change
2. Intake reads file, gets new as_of via extract.py
3. Extraction produces new facts
4. Conflict Detection:
   - Query KG for current facts with same subject/predicate
   - Compare as_of timestamps
5. Resolution:
   - If new as_of > old as_of → demote old, promote new
   - Update supersedes edges, valid_to, current flags
6. Indexing:
   - Update Qdrant payload for old fact current=false
   - Index new fact with current=true
7. Retrieval layer immediately sees updated current facts

Temporal conflict resolution is atomic per entity-predicate within KG transaction.

## 5. Temporal Validity Enforcement

Central invariant: KG is source of truth for current flag.

- All writes go through Temporal KG Module which enforces schema constraints
- Vector store payload mirrors KG current flag
- Retrieval filters always require current=true unless explicit historical request
- Supersession chain preserved for audit

## 6. Component Interfaces

```
Intake → Extraction → Enrichment → KG Module → Indexer
                                      ↓
                              Retrieval Layer
```

APIs:
- `POST /ingest` - trigger ingestion
- `POST /query` - query with mode parameter
- `GET /fact/{fact_id}/history` - audit trail

## 7. Data Models

Fact node in Neo4j:
```
(:Fact {fact_id, subject, predicate, object, as_of, valid_from, valid_to, current})
-[:DERIVED_FROM]->(:Provenance {source_file, extraction_path})
-[:SUPERSEDES]->(:Fact)
```

Qdrant point payload:
```
{
  fact_id: string,
  text: string,
  current: bool,
  as_of: int,
  source_file: string
}
```

## 8. Resilience and Edge Cases

- Missing timestamp → fallback to ingestion time with flag
- Same timestamp conflict → deterministic tie-break by source_file lexical order
- Partial file update → re-ingest whole file, conflict resolution handles unchanged facts
- VLM hallucination → provenance tracks model_version for audit

## 9. Diagram Summary

Textual component diagram:

[Watchdog] → [Intake + TimestampExtractor]
                     ↓
            [Multi-path Extraction] → [VLM Enrichment] → [Reconstruction]
                     ↓
            [Temporal KG Module] ↔ [Qdrant Indexer]
                     ↓
            [Pure RAG] [RAG+KG Validator] [KG-only] → [API]

Temporal validity flows from TimestampExtractor → Fact.as_of → Conflict Resolution → current flag → Retrieval filters.

Ready for Stage 5 – Planner.

---
Status: Draft awaiting human approval
