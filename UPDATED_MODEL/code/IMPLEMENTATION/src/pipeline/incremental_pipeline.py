#!/usr/bin/env python3
from src.temporal.temporal_kg import TemporalKG
from src.temporal.conflict_resolver import ConflictResolver
from src.indexing.vector_indexer import VectorIndexer

class IncrementalPipeline:
    def __init__(self, kg_uri, kg_user, kg_pass, qdrant_url):
        self.kg = TemporalKG(kg_uri, kg_user, kg_pass)
        self.indexer = VectorIndexer(qdrant_url)
        self.resolver = ConflictResolver(self.kg)
    def close(self): self.kg.close()
