#!/usr/bin/env fish
# setup_temporal.fish
# Fish-compatible setup script to materialise P0 Python files from DEV-P0-*.md specs
# Run from /home/karthikean.juttumaha/mini-extract

# 1. Create directories
mkdir -p src/temporal src/ingestion src/indexing src/retrieval src/pipeline tests

# 2. Create __init__.py files
touch src/__init__.py src/temporal/__init__.py src/ingestion/__init__.py src/indexing/__init__.py src/retrieval/__init__.py src/pipeline/__init__.py

# 3. Materialise Python files from specs
# DEV-P0-01 TimestampExtractor
bash -c 'cat > src/temporal/timestamp_extractor.py << "EOF"
#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
from typing import Tuple
import os
from extract import MetadataExtractor

class TimestampExtractor:
    def __init__(self):
        self.metadata_extractor = MetadataExtractor()
    def get_as_of(self, file_path):
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(file_path)
        fallback_used = False
        try:
            metadata = self.metadata_extractor.extract(path)
            modified_iso = metadata.get("filesystem",{}).get("modified_time")
            if modified_iso:
                as_of = datetime.fromisoformat(modified_iso.replace("Z","+00:00"))
                return as_of, False
        except Exception:
            fallback_used = True
        mtime = os.path.getmtime(path)
        return datetime.fromtimestamp(mtime, tz=timezone.utc), fallback_used
EOF'

# DEV-P0-02 Knowledge Graph Schema
bash -c 'cat > src/temporal/kg_schema.py << "EOF"
#!/usr/bin/env python3
from neo4j import GraphDatabase

class KGSchemasetup:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user,password))
    def setup_schema(self):
        stmts = [
            "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE",
            "CREATE CONSTRAINT fact_id_unique IF NOT EXISTS FOR (f:Fact) REQUIRE f.fact_id IS UNIQUE",
            "CREATE CONSTRAINT provenance_id_unique IF NOT EXISTS FOR (p:Provenance) REQUIRE p.provenance_id IS UNIQUE"
        ]
        with self.driver.session() as s:
            for st in stmts: s.run(st)
EOF'

bash -c 'cat > src/temporal/temporal_kg.py << "EOF"
#!/usr/bin/env python3
from neo4j import GraphDatabase
from datetime import datetime

class TemporalKG:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user,password))
    def close(self):
        self.driver.close()
    def get_current_facts(self, subject_entity_id, predicate):
        with self.driver.session() as s:
            res = s.run("MATCH (f:Fact) WHERE f.subject_entity_id=$s AND f.predicate=$p AND f.current=true RETURN f", s=subject_entity_id, p=predicate)
            return [dict(r["f"]) for r in res]
    def upsert_fact(self, fact_id, subject_entity_id, predicate, object_value, as_of, provenance_id):
        with self.driver.session() as s:
            s.run("""
                MERGE (f:Fact {fact_id:$fid})
                SET f.subject_entity_id=$s, f.predicate=$p, f.object_value=$o, f.as_of=$a, f.current=true
            """, fid=fact_id, s=subject_entity_id, p=predicate, o=object_value, a=as_of.isoformat())
EOF'

# DEV-P0-03 Conflict Resolver
bash -c 'cat > src/temporal/conflict_resolver.py << "EOF"
#!/usr/bin/env python3
from datetime import datetime
from temporal.temporal_kg import TemporalKG

class ConflictResolver:
    def __init__(self, kg):
        self.kg = kg
    def upsert_fact_with_resolution(self, fact_id, subject_entity_id, predicate, object_value, as_of, provenance_id, source_file_path):
        existing = self.kg.get_current_facts(subject_entity_id, predicate)
        if not existing:
            self.kg.upsert_fact(fact_id, subject_entity_id, predicate, object_value, as_of, provenance_id)
            return {"action":"inserted"}
        old = existing[0]
        old_as_of = datetime.fromisoformat(old.get("as_of","").replace("Z","+00:00"))
        if as_of > old_as_of:
            with self.kg.driver.session() as s:
                s.run("MATCH (f:Fact {fact_id:$id}) SET f.current=false", id=old["fact_id"])
            self.kg.upsert_fact(fact_id, subject_entity_id, predicate, object_value, as_of, provenance_id)
            return {"action":"promoted"}
        return {"action":"demoted"}
EOF'

# DEV-P0-04 Intake
bash -c 'cat > src/ingestion/intake.py << "EOF"
#!/usr/bin/env python3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
from temporal.timestamp_extractor import TimestampExtractor

@dataclass
class IngestionEvent:
    file_path: str
    as_of: datetime
    timestamp_fallback: bool
    ingestion_time: datetime
    file_hash: str
    event_type: str

class IntakeProcessor:
    def __init__(self, callback):
        self.extractor = TimestampExtractor()
        self.callback = callback
    def process_file(self, file_path, event_type):
        path = Path(file_path)
        as_of, fallback = self.extractor.get_as_of(path)
        h = hashlib.sha256()
        with open(path,"rb") as f:
            h.update(f.read())
        event = IngestionEvent(str(path.resolve()), as_of, fallback, datetime.now(timezone.utc), h.hexdigest(), event_type)
        self.callback(event)
EOF'

bash -c 'cat > src/ingestion/file_watcher.py << "EOF"
#!/usr/bin/env python3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ingestion.intake import IntakeProcessor

class SamplesEventHandler(FileSystemEventHandler):
    def __init__(self, processor): self.processor = processor
    def on_created(self, e):
        if not e.is_directory: self.processor.process_file(e.src_path,"created")
    def on_modified(self, e):
        if not e.is_directory: self.processor.process_file(e.src_path,"modified")

class FileWatcher:
    def __init__(self, watch_dir, callback):
        self.observer = Observer()
        self.handler = SamplesEventHandler(IntakeProcessor(callback))
        self.observer.schedule(self.handler, watch_dir, recursive=True)
    def start(self): self.observer.start()
    def stop(self): self.observer.stop(); self.observer.join()
EOF'

# DEV-P0-05 Vector Indexer
bash -c 'cat > src/indexing/vector_indexer.py << "EOF"
#!/usr/bin/env python3
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

class VectorIndexer:
    def __init__(self, qdrant_url="http://localhost:6333"):
        self.client = QdrantClient(url=qdrant_url)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
    def index_fact(self, fact_id, fact_text, metadata):
        vec = self.embedder.encode(fact_text).tolist()
        self.client.upsert(collection_name="temporal_facts", points=[{"id":fact_id,"vector":vec,"payload":metadata}])
    def search_current(self, query_text, top_k=10):
        qv = self.embedder.encode(query_text).tolist()
        res = self.client.search(collection_name="temporal_facts", query_vector=qv, limit=top_k, query_filter={"must":[{"key":"current","match":{"value":True}}]})
        return res
EOF'

# DEV-P0-06 Pure RAG
bash -c 'cat > src/retrieval/pure_rag.py << "EOF"
#!/usr/bin/env python3
from datetime import datetime, timezone
from indexing.vector_indexer import VectorIndexer

class PureRAGRetriever:
    def __init__(self, indexer): self.indexer = indexer
    def retrieve(self, question, top_k=5):
        results = self.indexer.search_current(question, top_k=top_k*2)
        now = datetime.now(timezone.utc).timestamp()
        for r in results:
            as_of = r.payload.get("as_of", now)
            age = max(0, (now - as_of)/86400)
            r.score = r.score * (0.7 + 0.3/(1+age/365))
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
EOF'

# DEV-P0-07 KG Only
bash -c 'cat > src/retrieval/kg_only.py << "EOF"
#!/usr/bin/env python3
from temporal.temporal_kg import TemporalKG

class KGOnlyRetriever:
    def __init__(self, kg): self.kg = kg
    def retrieve_by_entity_predicate(self, subject_entity_id, predicate):
        facts = self.kg.get_current_facts(subject_entity_id, predicate)
        return [{"fact_id":f.get("fact_id"),"object_value":f.get("object_value"),"as_of":f.get("as_of")} for f in facts]
EOF'

# DEV-P0-08 RAG KG Validator
bash -c 'cat > src/retrieval/rag_kg_validator.py << "EOF"
#!/usr/bin/env python3
from retrieval.pure_rag import PureRAGRetriever
from retrieval.kg_only import KGOnlyRetriever

class RAGKGValidatorRetriever:
    def __init__(self, pure_rag, kg_retriever):
        self.pure_rag = pure_rag
        self.kg = kg_retriever
    def retrieve(self, question, top_k=5):
        rag = self.pure_rag.retrieve(question, top_k)
        out = []
        for r in rag:
            subj = r.payload.get("subject_entity_id")
            pred = r.payload.get("predicate")
            if subj and pred:
                kg_facts = self.kg.retrieve_by_entity_predicate(subj, pred)
                if kg_facts:
                    out.append({"source":"KG","fact":kg_facts[0]})
                else:
                    out.append({"source":"RAG","fact":r})
            else:
                out.append({"source":"RAG","fact":r})
        return out
EOF'

# DEV-P0-09 Incremental Pipeline
bash -c 'cat > src/pipeline/incremental_pipeline.py << "EOF"
#!/usr/bin/env python3
from temporal.temporal_kg import TemporalKG
from temporal.conflict_resolver import ConflictResolver
from indexing.vector_indexer import VectorIndexer

class IncrementalPipeline:
    def __init__(self, kg_uri, kg_user, kg_pass, qdrant_url):
        self.kg = TemporalKG(kg_uri, kg_user, kg_pass)
        self.indexer = VectorIndexer(qdrant_url)
        self.resolver = ConflictResolver(self.kg)
    def close(self): self.kg.close()
EOF'

echo "Setup complete."
echo "To run tests:"
echo "  set -x PYTHONPATH /home/karthikean.juttumaha/mini-extract"
echo "  pytest tests/ -v"
echo ""
echo "Make sure Neo4j is running on bolt://localhost:7687 and Qdrant on http://localhost:6333"
