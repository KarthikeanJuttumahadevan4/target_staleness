#!/usr/bin/env python3
from src.indexing.vector_indexer import VectorIndexer
from src.temporal.temporal_kg import TemporalKG
class HierarchicalIndexer:
    def __init__(self, kg, indexer):
        self.kg = kg
        self.indexer = indexer
    def index_fact(self, fact_id, fact_text, metadata):
        self.indexer.index_fact(fact_id, fact_text, metadata)
