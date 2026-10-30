---
format: html
---

# 05_Retrieval — Hybrid Retrieval (3 Modes, Temporal-Aware)

## Purpose (from Proposal)

All three retrieval modes must default to **current=true** facts:

1. **Pure RAG** — vector search over current facts
2. **RAG + KG Validator** — hybrid hits, KG overrides stale
3. **KG-only** — graph traversal with `current=true` predicate

Historical versions only on explicit request (`as_of` or `include_history=True`).

---

## Git Projects to Assemble

### 1. Graphiti (Core Retrieval Engine)
- **Repo:** [github.com/getzep/graphiti](https://github.com/getzep/graphiti)
- **Key features:**
  - Hybrid retrieval: vector + keyword + graph traversal
  - Temporal filtering via search query params
  - MultiHop traversal for complex questions
  - Pluggable vector backends
- **Provides all three retrieval modes natively**

### 2. RAGBrain (Checked Generation Layer)
- **Repo:** [github.com/Nagendhra-Madishetti/ragbrain](https://github.com/Nagendhra-Madishetti/ragbrain)
- **Key features:**
  - As-of retrieval (validity-filtered before ranking)
  - Checked generation: claim-by-claim verification
  - Citation-enriched answers
  - System-time replay for audit
- **Use case:** Add on top of Graphiti for verified answers

### 3. HiRAG (Hierarchical Enhancement)
- **Repo:** Code at [arxiv.org/abs/2025.findings-emnlp.321](https://arxiv.org/abs/2025.findings-emnlp.321)
- **Key features:**
  - 3-level context (global → bridge → local)
  - Hierarchical KG with summary entities
  - Bridges knowledge layer disparities
- **Use case:** Enhance Graphiti retrieval with hierarchical context

### 4. Helix (Multi-Hop + Hallucination Detection)
- **Repo:** [github.com/YashNuhash/Helix](https://github.com/YashNuhash/Helix)
- **License:** MIT
- **Key features:**
  - Fuses LightRAG (dual-level retrieval) + Graphiti
  - Multi-hop BFS with scoring
  - Composite Fidelity Index (CFI) verification
- **Use case:** Use CFI to score answer faithfulness

### 5. Engram (Temporal Scoring)
- **Repo:** [github.com/jamjet-labs/engram](https://github.com/jamjet-labs/engram)
- **Key features:**
  - HybridRetriever (vector + keyword + temporal)
  - Reader modes (recall vs synthesis)
  - Active fact versioning (`supersede()` filters old by default)
- **Use case:** Mature hybrid retrieval with temporal scoring

---

## Three Retrieval Modes (Implementation)

### Mode 1: Pure RAG (Vector + temporal filter)

```
INPUT: query
  1. Encode query → embedding
  2. Vector search top-K where metadata.current=true
     (metadata stored at ingestion time by Graphiti/RAGBrain)
  3. Return ranked hits with citations
  4. LLM generates answer from hits
```

**Libraries:** Graphiti.search(query, modes=['vector'])
**Temporal filter:** `current=true` metadata

---

### Mode 2: RAG + KG Validator (Most robust)

```
INPUT: query
  1. Vector search top-K hits (without current filter initially)
  2. For each hit:
     - Lookup corresponding entity in KG
     - Check KG.current flag
     - IF current=false: discard hit, optionally surface superseded-by
  3. KG traversal: expand neighborhood of valid entities
  4. Combine surviving vector hits + KG facts
  5. RRF fusion (Reciprocal Rank Fusion)
  6. RAGBrain "checked generation":
     - Generate answer candidate
     - Verify each claim against retrieved facts
     - Flag unsupported claims
  7. Return answer with citations + confidence
```

**Libraries:**
- Graphiti (vector search + KG)
- Helix (CFI scoring optional)
- RAGBrain (checked generation)

---

### Mode 3: KG-Only (Traversal + temporal filter)

```
INPUT: query
  1. NER on query → seed entities
  2. Personalized PageRank / BFS from seed entities
  3. Filter edges where current=true
  4. Aggregate facts within N-hops
  5. (Optional) HiRAG hierarchical expansion
  6. LLM generates answer with citations
```

**Libraries:** Graphiti (graph query) + HiRAG (hierarchical)

---

## Temporal Query Support

### Default (current=true)
```python
result = graph.query("Who is CEO?", valid_at="now")
```

### Historical
```python
result = graph.query(
    "Who was CEO in 2023?",
    valid_at=datetime(2023, 6, 1)
)
```

### System-time replay (audit)
```python
result = graph.query(
    "What did we know about CEO on 2024-01-01?",
    believed_at=datetime(2024, 1, 1)
)
```

### Include history
```python
result = graph.query(
    "Show all CEO versions",
    include_history=True
)
```

---

## Fusion Methods

| Method | Implementation | Used In |
|--------|---------------|---------|
| **Reciprocal Rank Fusion (RRF)** | Standard — fuse vector + keyword + KG ranks | Mode 2 |
| **Weighted Sum** | (0.4 semantic) + (0.3 keyword) + (0.3 graph) | Mode 1 |
| **Composite Score** (context-graph) | (0.3 recency) + (0.4 confidence) + (0.3 authority) | Mode 3 |
| **Graph Traversal** | BFS/Dijkstra with temporal edge filtering | Mode 3 |

---

## Citation Requirements (per Proposal)

Every answer MUST include:
- **Fact content** (extracted knowledge)
- **Source file** (provenance)
- **Extraction path** (text/ocr/vlm/etc.)
- **Model used** (for extraction)
- **As-of timestamp** (when fact was valid)
- **Confidence score** (optional but recommended)

Example output:
```
Answer: Satya Nadella is CEO of Microsoft.
Citation: Microsoft Annual Report 2024.pdf, p. 12
Extracted via: vlm (Qwen2.5-VL-7B)
As-of: 2024-01-15 (file modified)
Confidence: 0.95
Note: Previous CEO "Steve Ballmer" superseded on 2014-02-04.
```

---

## Retrieval Quality Metrics (Evaluation Band)

To be measured during Evaluation Band:

| Metric | Definition | Target |
|--------|-----------|--------|
| **Temporal Correctness** | % queries returning newest fact | ≥95% |
| **Faithfulness (CFI)** | Verified claim ratio | ≥0.9 |
| **Hit@K** | Top-K contains answer | ≥0.9 |
| **MRR** | Reciprocal rank of first hit | ≥0.8 |
| **Latency** | Query → answer | <3s |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| KG validator filters too aggressively (losing relevant hits) | Tune KG matching (exact vs fuzzy entity match) |
| Stale vector hits even after supersession | Re-index / delete old vectors on supersession |
| Checked generation slows response | Limit verify step; use smaller model for verification |
| CFI false positives | Use NLI-based verification (LLMConflictResolver) |
| Hierarchical expansion noise | Tune LSH threshold (0.7 minimum similarity) |

---

## Open Questions

1. Reranking: cross-encoder vs LLM-as-reranker? Recommendation: ms-marco-MiniLM (fast)
2. Knowledge cache: should frequently asked queries cache? TTL suggestion: 1 hour
3. Failed entity resolution: fallback to vector-only search?
4. Async retrieval or sync for audit trail?
5. Should we expose `as_of` to end users, or auto-detect from query?
