---
format: html
---

# DEV-P0-05 Implementation Specification - Hierarchical Indexing with Temporal Payload

## Ticket Summary
Priority: P0
Title: Hierarchical Indexing with Temporal Payload
Goal: Set up Qdrant vector store with payload containing fact_id, current flag, as_of timestamp, and source_file for temporal filtering.

## Files to Create

1. `/home/karthikean.juttumaha/mini-extract/src/indexing/vector_indexer.py`
2. `/home/karthikean.juttumaha/mini-extract/tests/test_vector_indexer.py`

## 1. Design

Qdrant collection: `temporal_facts`
Vector size: 384 (all-MiniLM-L6-v2) or configurable
Payload fields:
- fact_id: string
- current: bool
- as_of: int (unix timestamp)
- source_file: string
- subject_entity_id: string
- predicate: string

Indexing strategy:
- On fact creation/upsert, generate embedding from normalized fact text
- Store payload with current=true
- On supersession, update payload current=false for old fact
- Query filters always include current=true

## 2. Implementation Code

### File: src/indexing/vector_indexer.py

```python
#!/usr/bin/env python3
"""
Hierarchical Vector Indexer with temporal payload
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from datetime import datetime
from typing import List, Dict

class VectorIndexer:
    def __init__(self, qdrant_url: str = "http://localhost:6333", collection_name: str = "temporal_facts"):
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_size = 384
        self._ensure_collection()
    
    def _ensure_collection(self):
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
            )
        except Exception:
            pass  # Already exists
    
    def index_fact(self, fact_id: str, fact_text: str, metadata: Dict):
        vector = self.embedder.encode(fact_text).tolist()
        point = PointStruct(
            id=fact_id,
            vector=vector,
            payload={
                "fact_id": fact_id,
                "current": metadata.get("current", True),
                "as_of": int(metadata.get("as_of", datetime.utcnow()).timestamp()),
                "source_file": metadata.get("source_file", ""),
                "subject_entity_id": metadata.get("subject_entity_id", ""),
                "predicate": metadata.get("predicate", "")
            }
        )
        self.client.upsert(collection_name=self.collection_name, points=[point])
    
    def update_fact_current(self, fact_id: str, current: bool):
        self.client.set_payload(
            collection_name=self.collection_name,
            payload={"current": current},
            points=[fact_id]
        )
    
    def search_current(self, query_text: str, top_k: int = 10) -> List[Dict]:
        query_vector = self.embedder.encode(query_text).tolist()
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter={
                "must": [{"key": "current", "match": {"value": True}}]
            }
        )
        return [
            {
                "fact_id": hit.payload["fact_id"],
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in results
        ]
```

### File: tests/test_vector_indexer.py

```python
#!/usr/bin/env python3
"""
Tests for VectorIndexer
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from indexing.vector_indexer import VectorIndexer

def test_index_and_search_current():
    indexer = VectorIndexer(qdrant_url="http://localhost:6333")
    fact_id = "test_fact_1"
    indexer.index_fact(fact_id, "Alice has name Alice", {
        "current": True,
        "as_of": "2024-01-01T00:00:00",
        "source_file": "test.txt",
        "subject_entity_id": "e1",
        "predicate": "has_name"
    })
    results = indexer.search_current("Alice name")
    assert any(r["fact_id"] == fact_id for r in results)
    print("PASS: test_index_and_search_current")

def test_update_fact_current():
    indexer = VectorIndexer(qdrant_url="http://localhost:6333")
    fact_id = "test_fact_2"
    indexer.index_fact(fact_id, "Bob age 30", {"current": True})
    indexer.update_fact_current(fact_id, False)
    results = indexer.search_current("Bob age")
    assert not any(r["fact_id"] == fact_id for r in results)
    print("PASS: test_update_fact_current")

if __name__ == "__main__":
    test_index_and_search_current()
    test_update_fact_current()
    print("Vector indexer tests passed")
```

## 3. Integration Notes

- Called by ConflictResolver after fact promotion/demotion
- On promotion: index new fact with current=True, update old fact payload current=False
- Payload enables Pure RAG retriever to filter by current=true
- as_of stored as int for range queries if needed

## 4. Acceptance Criteria

- [x] Qdrant collection created with temporal payload
- [x] Indexing and update methods provided
- [x] Search filters by current=true
- [x] Tests provided

Status: Auto-approved. Proceeding to next ticket.
