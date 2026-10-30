---
format: html
---

# 04_Database_Design — Neo4j + Qdrant Schema

## 1. Graph Backend Decision: **Neo4j**

**Rationale (Military)**: Mature, ACID, transactional, well-tooled, supports
bitemporal queries via properties, rich Cypher ecosystem, on-prem deployable.
FalkorDB faster but less ecosystem; Memgraph similar with low edge. Neo4j
favored for audit tooling and Cypher queryability by analysts.

## 2. Vector Backend Decision: **Qdrant**

**Rationale**: Rust-based, fast, supports payload filters (current=true), on-prem
docker deploy, HNSW index, named collections. Lower memory than Weaviate;
Chroma is single-node only.

## 3. LLM / VLM Decisions (User-Confirmed)
- LLM provider: **OpenAI-compatible via internal gateway** (gpt-4-turbo text, gpt-4o vision)
- VLM: **cloud GPT-4o / Gemini** via gateway, fallback Qwen2.5-VL-7B-SFT on-prem

## 4. Temporal Engine: **Graphiti + RAGBrain**
- Graphiti provides episodes + hybrid retrieval + provenance.
- RAGBrain provides supersession logic + checked generation + system-time replay.

---

## 5. Neo4j Schema

### Node Labels
- `:Document` (file-level)
- `:Episode` (ingestion event; Graphiti native)
- `:Entity` (normalized person/org/place/concept)
- `:Fact` (atomic extracted knowledge; carries temporal + provenance)
- `:Audit` (audit records; immutable)

### Relationships
- `(Document)-[:HAS_EPISODE]->(Episode)`
- `(Episode)-[:YIELDS]->(Entity)` (provenance)
- `(Entity)-[:HAS_FACT {relation}]->(Entity)` (with temporal props)
- `(Fact)-[:SUPERSEDES {at: timestamp}]->(Fact)`
- `(Fact)-[:PROVENANCE {source, extraction_path, model, as_of}]->(Fact)` (optional; folded into node props instead for simplicity)

### Fact Node Properties (mandatory)
```
fact_id        UUID
content        str
entity_id      UUID    # canonical identity
predicate      str     # e.g. "CEO_OF", "WORKS_AT"
valid_at       timestamp
invalid_at     timestamp (null if current)
created_at     timestamp
expired_at     timestamp (null if current)
source_file    str
extraction_path str    # text/ocr/vlm/table/audio/video
model_used     str
current        bool
confidence     float
embedding_id   str     # Qdrant point id
superseded_by  UUID (null if current)
```

### Indexes
```cypher
CREATE CONSTRAINT ON (e:Entity) ASSERT e.entity_id IS UNIQUE;
CREATE CONSTRAINT ON (f:Fact) ASSERT f.fact_id IS UNIQUE;
CREATE INDEX ON :Fact(current);
CREATE INDEX ON :Fact(valid_at);
CREATE INDEX ON :Fact(invalid_at);
CREATE INDEX ON :Fact(entity_id);
CREATE INDEX ON :Fact(predicate);
CREATE INDEX ON :Document(source_path, valid_at);
```

### Query Patterns

**Default (current):**
```cypher
MATCH (f:Fact {entity_id:$id, predicate:$pred})
WHERE f.current = true
RETURN f ORDER BY f.valid_at DESC
```

**Historical as_of:**
```cypher
MATCH (f:Fact {entity_id:$id, predicate:$pred})
WHERE f.valid_at <= $as_of AND (f.invalid_at IS NULL OR f.invalid_at > $as_of)
RETURN f ORDER BY f.valid_at DESC
```

**Supersession chain:**
```cypher
MATCH p=(f:Fact {fact_id:$id})-[:SUPERSEDES*]->(older)
RETURN p
```

---

## 6. Qdrant Schema

### Collection: `facts`
- Vector dimension: 768 (all-mpnet-base-v2)
- Distance: Cosine
- Payload filterable fields:
  - `fact_id` (keyword, unique)
  - `entity_id` (keyword)
  - `predicate` (keyword)
  - `current` (bool, indexed)
  - `as_of` (datetime, range filter)
  - `source_file` (keyword)
  - `extraction_path` (keyword)
  - `model_used` (keyword)
  - `confidence` (float)
  - `content` (text, payload only)

### Payload Indexes
```python
create_payload_index("current", type=bool)
create_payload_index("as_of", type=datetime)
create_payload_index("entity_id", type=keyword)
```

### Query Patterns
```python
# Pure RAG (current only)
qdrant.search(collection, query_vector, filter=Filter(must=[FieldCondition("current", match=True)]), limit=K)

# RAG + historical
qdrant.search(..., filter=Filter(must=[FieldCondition("as_of", range=Range(lte=as_of))]))
```

---

## 7. File Storage Layout

```
samples5/        # source of truth (user drops files)
data/
├── sqlite_jobs.db         # intake queue
├── neo4j/                 # data directory (dbms)
├── qdrant/                # storage directory
├── audit.jsonl            # append-only audit
└── snapshots/             # (optional) Semantica weekly snapshots
```
