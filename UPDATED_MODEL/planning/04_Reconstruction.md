# 04_Reconstruction — Temporal KG Construction & Conflict Resolution

## Purpose

Convert extracted entities/facts into a **temporal knowledge graph** with:

- As-of timestamps (from file metadata via reuse of `extract.py`)
- Provenance (source, extraction path, model)
- Conflict detection (entity identity + provenance)
- Supersession (most-recent-wins, retain history)
- Audit trails

---

## Git Projects to Assemble

### 1. Graphiti (Primary KG Engine)
- **Repo:** [github.com/getzep/graphiti](https://github.com/getzep/graphiti)
- **Developed by:** Zep Inc.
- **License:** Apache 2.0
- **Stars:** 32K
- **Key features:**
  - Temporal fact management (validity windows)
  - Episodes & provenance (full lineage)
  - Incremental construction (no batch rebuild)
  - Hybrid retrieval (vector + KG + BM25)
  - Hyperparameter-tuned entity/relation extraction
  - Multiple backends: Neo4j, FalkorDB, Memgraph
  - Bi-temporal support (also provides transaction time)
- **Why chosen:** Most mature; production-tested; supports all three retrieval modes

### 2. RAGBrain (Conflict Resolution & Audit Layer)
- **Repo:** [github.com/Nagendhra-Madishetti/ragbrain](https://github.com/Nagendhra-Madishetti/ragbrain)
- **Developed by:** Nagendhra Madishetti
- **License:** Apache 2.0
- **Key features:**
  - Bi-temporal model (4 timestamps per fact)
  - `superseded_by` back-links at write time
  - System-time replay (audit)
  - Checked generation (claim-by-claim verification)
  - Pluggable everything (embedder, reranker, backend)
  - Multi-replica ready (shared session state)
- **Why chosen:** Explicit conflict resolution; citation-ready answers

### 3. Semantica (Entity Resolution Utility)
- **Repo:** [github.com/semantica-agi/semantica](https://github.com/semantica-agi/semantica)
- **License:** MIT
- **Key features:** `GraphBuilder(merge_entities=True)`; fuzzy/exact/ML-based resolution
- **Use case:** Deduplicate entities before KG insertion (e.g., "Apple", "Apple Inc.", "AAPL")

### 4. zeit (Lightweight Temporal Layer)
- **Repo:** [github.com/kborovik/zeit](https://github.com/kborovik/zeit)
- **License:** Proprietary (zeit-graph on PyPI)
- **Key features:** Bi-temporal clocks, expires old fact, history retained
- **Use case:** Fallback if Graphiti alone insufficient

### 5. context-graph (Conflict Taxonomy)
- **Repo:** [github.com/williebsweet/context-graph](https://github.com/williebsweet/context-graph)
- **License:** (check)
- **Key features:** 4 conflict types; 4 resolution strategies; recency wins
- **Use case:** Reference implementation for conflict detection taxonomy

---

## Assembled Reconstruction Pipeline

```
Entity/Relation Extracts (from Intake)
       │
       ├── [1] Entity Resolution (Semantica)
       │       merge_entities=True → dedup "Apple"/"AAPL"/"Apple Inc."
       │
       ├── [2] Temporal Metadata Attachment (reuse extract.py)
       │       file mtime → valid_at (as-of timestamp)
       │       source file, extraction path, model → provenance
       │
       ├── [3] Graphiti Episode Creation
       │       graphiti.add_episode(
       │         content=fact,
       │         source=...,
       │         timestamp=as_of,
       │         valid_at=as_of,
       │         metadata={provenance}
       │       )
       │
       ├── [4] Conflict Detection (Graphiti + RAGBrain)
       │       • Identify matching entity identity
       │       • Compare as-of timestamps
       │       • If newer: mark older superseded
       │       • Create superseded_by edge
       │
       └── [5] Audit + Versioning
               • Retain old facts (current=false)
               • Record mutation history
               • Create snapshot (optional, via Semantica TemporalVersionManager)
```

---

## Temporal Metadata (Required per Proposal)

Every fact MUST carry:

| Field | Source |
|-------|--------|
| `valid_at` | File mtime (from `extract.py`) |
| `invalid_at` | Set when superseded |
| `created_at` | System time of ingest |
| `expired_at` | Set when superseded (system time) |
| `source_file` | Path to document |
| `extraction_path` | text / ocr / vlm / table / ... |
| `model_used` | Name + version |
| `current` | Boolean flag |
| `superseded_by` | UUID of newer fact |

---

## Conflict Detection Logic (Most-Recent-Wins)

```
On ingest new fact F_new:
  FOR each existing fact F_old WHERE:
    entity_id(F_new) == entity_id(F_old) AND
    predicate(F_new) == predicate(F_old):
      IF valid_at(F_new) > valid_at(F_old):
          # Conflict: promote new, demote old
          F_new.current = true
          F_old.current = false
          F_old.invalid_at = valid_at(F_new) - epsilon
          F_old.expired_at = now()
          F_old.superseded_by = F_new.id
          CREATE EDGE F_new SUPERSEDES F_old
      ELSE:
          # Older new; mark current but don't promote
          F_new.current = false
          F_new.superseded_by = F_old.id (informative)

Default retrieval filter: current = true
```

---

## Reuse of `extract.py`

Per the proposal, the existing `extract.py` provides file modification/edit
timestamps. To reuse:

1. **Locate** `extract.py` (currently exists in repo root)
2. **Wrap** it to produce `valid_at` timestamps for Graphiti episodes:
   ```python
   from extract import get_file_modified_time
   valid_at = get_file_modified_time(source_path)
   graphiti.add_episode(content, source_path, valid_at=valid_at)
   ```
3. **Improve** it if it only captures creation time (need modification time);
   expose both.

### Open Decision
- Should `extract.py` be **improved** (e.g., to handle audio/video creation dates)?
- Or only reused as-is (and supplemented by other timestamp sources)?

---

## Audit Trail & Versioning

- **Retain full history** (do not delete old facts).
- Use **Semantica's TemporalVersionManager** (SQLite backend) for periodic
  graph snapshots (optional but recommended).
- Provide `query_history(entity_id)` returning all facts (current + superseded)
  with timestamps and sources.
- Use **RAGBrain's system-time replay** to answer "what did the system know
  on date D?"

---

## Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Entity ID mismatch across sources | Use hash-based canonical IDs (Semantica fuzzy merge) |
| Concurrent ingestion race conditions | Use transactional graph DB (Neo4j/FalkorDB ACID) |
| Supersession logic errors | Use Graphiti's built-in invalidation + tests |
| Audit performance degradation | Periodic snapshot + archival (Semantica prune_versions) |
| Missing timestamps | Fallback to `now()` system time; flag as low confidence |

---

## Open Questions

1. Which graph DB backend (Neo4j vs FalkorDB vs Memgraph)? 
   - **Recommendation:** FalkorDB (fast, in-memory, temporal graph natively).
2. Should KG snapshots be automatic (per ingest) or manual?
3. How to handle **partial conflicts** (only some relations change)?
4. Should invalidation be **synchronous** or via background queue?
