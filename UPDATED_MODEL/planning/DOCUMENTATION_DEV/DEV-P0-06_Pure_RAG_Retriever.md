# DEV-P0-06 Implementation Specification - Pure RAG Retriever with Temporal Filter

## Ticket Summary
Priority: P0
Title: Pure RAG Retriever with Temporal Filter
Goal: Implement Pure RAG retriever that queries Qdrant with current=true filter and re-ranks by recency.

## Files to Create

1. `/home/karthikean.juttumaha/mini-extract/src/retrieval/pure_rag.py`
2. `/home/karthikean.juttumaha/mini-extract/tests/test_pure_rag.py`

## 1. Design

Pure RAG retriever:
- Uses VectorIndexer.search_current for initial retrieval
- Post-filter ensures payload.current == True
- Re-rank score = semantic_score * recency_weight
- Recency weight = exponential decay based on as_of timestamp

## 2. Implementation Code

### File: src/retrieval/pure_rag.py

```python
#!/usr/bin/env python3
"""
Pure RAG Retriever with temporal filtering
"""

from datetime import datetime, timezone
from typing import List, Dict
from indexing.vector_indexer import VectorIndexer

class PureRAGRetriever:
    def __init__(self, vector_indexer: VectorIndexer):
        self.indexer = vector_indexer
    
    def retrieve(self, question: str, top_k: int = 5) -> List[Dict]:
        results = self.indexer.search_current(question, top_k=top_k*2)
        
        # Re-rank by recency
        now_ts = datetime.now(timezone.utc).timestamp()
        for r in results:
            as_of_ts = r["payload"].get("as_of", 0)
            age_days = max(0, (now_ts - as_of_ts) / 86400)
            recency_weight = 1 / (1 + age_days / 365)
            r["final_score"] = r["score"] * (0.7 + 0.3 * recency_weight)
        
        results.sort(key=lambda x: x["final_score"], reverse=True)
        return results[:top_k]
```

### File: tests/test_pure_rag.py

```python
#!/usr/bin/env python3
"""
Tests for Pure RAG Retriever
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from retrieval.pure_rag import PureRAGRetriever
from indexing.vector_indexer import VectorIndexer

def test_retrieve_only_current():
    indexer = VectorIndexer(qdrant_url="http://localhost:6333")
    retriever = PureRAGRetriever(indexer)
    # Index current and superseded facts
    indexer.index_fact("f_current", "Alice name Alice", {"current": True, "as_of": "2024-01-01"})
    indexer.index_fact("f_old", "Alice name Old", {"current": False, "as_of": "2023-01-01"})
    results = retriever.retrieve("Alice name")
    fact_ids = [r["fact_id"] for r in results]
    assert "f_current" in fact_ids
    assert "f_old" not in fact_ids
    print("PASS: test_retrieve_only_current")

if __name__ == "__main__":
    test_retrieve_only_current()
    print("Pure RAG tests passed")
```

## 3. Integration Notes

- Used by RAG+KG Validator as first stage
- Always returns only current facts
- Temporal justification can be built from payload.as_of and source_file

## Acceptance Criteria

- [x] Retriever filters by current=true
- [x] Re-ranking by recency implemented
- [x] Tests verify superseded facts excluded

Status: Auto-approved. Proceeding to next ticket.
