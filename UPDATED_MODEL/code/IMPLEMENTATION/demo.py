from src.temporal.timestamp_extractor import TimestampExtractor
from src.temporal.temporal_kg import TemporalKG
from src.temporal.conflict_resolver import ConflictResolver
from src.indexing.vector_indexer import VectorIndexer

# Init
kg = TemporalKG("bolt://localhost:7687", "neo4j", "password")
indexer = VectorIndexer("http://localhost:6333")
resolver = ConflictResolver(kg)

# Example ingest
extractor = TimestampExtractor()
as_of, _ = extractor.get_as_of("samples5/sample1.txt")
print(f"as_of = {as_of}")

# After you copy the code from the specs into src/, run:
# resolver.upsert_fact_with_resolution(...)
# indexer.index_fact(...)

kg.close()
