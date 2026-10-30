#!/usr/bin/env python3
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

class VectorIndexer:
    def __init__(self, qdrant_url="http://localhost:6333"):
        self.client = QdrantClient(url=qdrant_url)
        self.embedder = SentenceTransformer(all-MiniLM-L6-v2)
    def index_fact(self, fact_id, fact_text, metadata):
        vec = self.embedder.encode(fact_text).tolist()
        self.client.upsert(collection_name="temporal_facts", points=[{"id":fact_id,"vector":vec,"payload":metadata}])
    def search_current(self, query_text, top_k=10):
        qv = self.embedder.encode(query_text).tolist()
        res = self.client.search(collection_name="temporal_facts", query_vector=qv, limit=top_k, query_filter={"must":[{"key":"current","match":{"value":True}}]})
        return res
