# 01_Architecture — Assembled Pipeline

## End-to-End Pipeline (from Proposal, assembled)

```
┌─────────────────────────────────────────────────────────────────┐
│  INTAKE (AI-KE + Docling + Docs2KG)                             │
│  Watches samples5/  →  accepts 15+ formats → normalizes         │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  MULTI-PATH EXTRACTION                                           │
│  • Text path:  Docs2KG / Semantica (NER + relations)             │
│  • Table path: Docling / MinerU (table structure recognition)    │
│  • Visual path: Docling-Graph / Multi-VIE (VLM captions)         │
│  • Audio/video: AI-KE (FFmpeg → Whisper → text)                  │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  VLM ENRICHMENT (Docling-Graph + Diagram2Graph)                  │
│  • Qwen2.5-VL-7B-SFT / GPT-4o Vision                            │
│  • Charts, diagrams, flowcharts → KG nodes/edges                 │
│  • Provenance tagged (model + extraction path)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  RECONSTRUCTION (Graphiti + RAGBrain)                            │
│  • Entities normalized (Semantica merge_entities=True)            │
│  • Temporal metadata attached (valid_at, created_at)             │
│  • Conflict detected → supersession edges added                   │
│  • Provenance recorded (source, timestamp, model)                │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  HIERARCHICAL INDEXING (HiRAG + Graphiti layers)                │
│  • Layer 0: leaf entities/relations                              │
│  • Layer 1: community summaries (LLM-generated)                 │
│  • Layer 2+: global summaries                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  HYBRID RETRIEVAL (Graphiti + RAGBrain + HiRAG)                 │
│  • Mode A: Pure RAG (vector, current-only)                      │
│  • Mode B: RAG + KG Validator (hybrid + current-flag check)     │
│  • Mode C: KG-only (graph traversal, current=true predicate)    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Wiring

Each arrow above is a **library API call**, not a code authoring task:

| Connection | API Call |
|-----------|----------|
| Intake → Extraction | `AIKEExtractor.extract(path)` → `DoclingParser.parse(path)` |
| Extraction → VLM | `docling_graph.extract(image, prompt)` |
| VLM → Reconstruction | `graphiti.add_episode(content, source, timestamp)` |
| Extraction → Reconstruction | `semantica merger_entities=True` |
| Reconstruction → Indexing | `graphiti.add_episode()` (auto-indexes) |
| Indexing → Retrieval | `graphiti.query(q, mode=...)` / `ragbrain.query(q, as_of=...)` |

---

## Temporal Default in Retrieval (Required by Proposal)

| Mode | Implementation |
|------|---------------|
| Pure RAG | Query vector index with `current=true` metadata filter |
| RAG + KG Validator | Vector hits → KG `current` flag check → override stale hits |
| KG-only | Cypher/ traversal with `WHERE e.current = true` |

---

## Temporal Behaviour Across Components

| Ingestion | Conflict Detection | Retrieval |
|-----------|-------------------|-----------|
| Watch samples5/; extract as-of from file metadata | Compare by entity identity + provenance | Default to current=true |
| Multi-path extraction (text + table + visual) | Compare as-of timestamps | KG validator overrides stale |
| Record provenance (source, path, model) | Promote newer; demote older to superseded | Most-recent-wins cited |
| Retain superseded facts for audit | `superseded_by=<new>`, `validity_end=<new as-of>` | Historical only on explicit request |

---

## Open Design Questions
1. Which vector store backend (Qdrant, Weaviate, Chroma)?
2. Which graph backend (Neo4j, FalkorDB, Memgraph)?
3. Which LLM provider (OpenAI, Anthropic, Ollama local)?
4. Whether to use RAGBrain *on top of* Graphiti, or replace?
5. How to handle stale-fact *retrieval history* audit queries?

➡️ **Awaiting human validation.**
