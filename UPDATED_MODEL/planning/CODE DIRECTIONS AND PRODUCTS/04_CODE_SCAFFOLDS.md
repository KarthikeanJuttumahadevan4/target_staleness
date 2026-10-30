# 04_CODE_SCAFFOLDS — Copy-Paste Skeletons per File

> Replace `pass` / `raise NotImplementedError` bodies with real implementation.
> Tests referenced in `07_ACCEPTANCE_CHECKS.md` validate each.

## `src/config.py`
```python
from pydantic import BaseSettings, Field
from functools import lru_cache

class Settings(BaseSettings):
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="http://llm-gateway.internal/v1", alias="OPENAI_BASE_URL")
    model: str = Field(default="gpt-4-turbo", alias="MODEL")
    vlm_model: str = Field(default="gpt-4o", alias="VLM_MODEL")
    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="", alias="NEO4J_PASSWORD")
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    watch_dir: str = Field(default="./samples5", alias="WATCH_DIR")
    audit_log_path: str = Field(default="./data/audit.jsonl", alias="AUDIT_LOG_PATH")

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache
def get_settings():
    return Settings()
```

## `src/intake/router.py`
```python
import magic

ARCHIVE_EXT = {".zip", ".tar", ".gz", ".7z", ".tar.gz"}
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}
VIDEO_EXT = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
PDF_EXT = {".pdf"}
OFFICE_EXT = {".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt"}
TEXT_EXT = {".txt", ".md", ".csv", ".json", ".xml", ".rtf"}

def route(path: str) -> str:
    low = path.lower()
    from pathlib import Path
    suf = Path(low).suffix
    if suf in ARCHIVE_EXT: return "archive"
    if suf in AUDIO_EXT: return "audio"
    if suf in VIDEO_EXT: return "video"
    if suf in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}: return "vlm"
    if suf in PDF_EXT:
        mime = magic.from_file(path, mime=True)
        return "ocr" if "application/pdf" in mime else "text"
    if suf in OFFICE_EXT: return "text"
    if suf in TEXT_EXT: return "text"
    return "unsupported"
```

## `src/extraction/vlm.py`
```python
"""Conditional VLM enrichment. Lazy-import heavy deps."""
def enrich(images: list, prompt_type: str = "caption") -> list[dict]:
    # 1. Try on-prem Qwen2.5-VL-7B via vLLM (optional)
    # 2. Fallback to OpenAI gateway gpt-4o vision
    # returns list of {content, bbox, confidence, model_used}
    raise NotImplementedError  # CODER: implement
```

## `src/temporal/temporal_kg.py`
```python
"""Neo4j/Graphiti wrapper. See ARCHITECTURE/04_Database_Design.md."""
from neo4j import GraphDatabase
from src.config import get_settings

class TemporalKG:
    def __init__(self, uri=None, user=None, password=None):
        s = get_settings()
        self.driver = GraphDatabase.driver(
            uri or s.neo4j_uri,
            auth=(user or s.neo4j_user, password or s.neo4j_password),
        )

    def close(self):
        self.driver.close()

    def get_current_facts(self, entity_id, predicate):
        with self.driver.session() as sess:
            res = sess.run(
                "MATCH (f:Fact) WHERE f.entity_id=$e AND f.predicate=$p AND f.current=true "
                "RETURN f ORDER BY f.valid_at DESC", e=entity_id, p=predicate)
            return [dict(r["f"]) for r in res]

    def upsert_fact(self, fact_id, entity_id, predicate, object_value, as_of, source_file,
                    extraction_path, model_used, current=True, confidence=1.0):
        with self.driver.session() as sess:
            sess.run("""
                MERGE (f:Fact {fact_id:$fid})
                SET f.entity_id=$e, f.predicate=$p, f.object_value=$o,
                    f.valid_at=$a, f.source_file=$sf, f.extraction_path=$ep,
                    f.model_used=$m, f.current=$c, f.confidence=$conf,
                    f.created_at=datetime()
                """,
                fid=fact_id, e=entity_id, p=predicate, o=object_value, a=as_of.isoformat(),
                sf=source_file, ep=extraction_path, m=model_used, c=current, conf=confidence)

    def supersede(self, old_fact_id, new_fact_id, at_iso):
        with self.driver.session() as sess:
            sess.run("""
                MATCH (o:Fact {fact_id:$o}) MATCH (n:Fact {fact_id:$n})
                SET o.current=false, o.invalid_at=datetime($at), o.expired_at=datetime(),
                    o.superseded_by=$n
                MERGE (n)-[:SUPERSEDES]->(o)
            """, o=old_fact_id, n=new_fact_id, at=at_iso)
```

## `src/reconstruction/conflict_resolver.py`
```python
from datetime import datetime
from src.models import ReconciliationResult

def reconcile(new_fact, existing_facts: list) -> ReconciliationResult:
    """Most-recent-wins. Synchronous."""
    # Compare by entity_id + predicate. If newer valid_at => supersede.
    for old in existing_facts:
        if old["entity_id"] == new_fact["entity_id"] and old["predicate"] == new_fact["predicate"]:
            new_dt = datetime.fromisoformat(new_fact["valid_at"].replace("Z","+00:00"))
            old_dt = datetime.fromisoformat(old["valid_at"].replace("Z","+00:00"))
            if new_dt > old_dt:
                return ReconciliationResult(action="supersede",
                    superseded_fact_id=old["fact_id"],
                    reason=f"newer valid_at {new_dt} > {old_dt}")
    return ReconciliationResult(action="keep", reason="no conflict or not newer")
```

## `src/audit/logger.py`
```python
import json, hashlib, datetime
from pathlib import Path

class AuditLogger:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._prev_hash = self._last_hash()

    def _last_hash(self):
        if not self.path.exists(): return "GENESIS"
        last = self.path.read_text().strip().splitlines()[-1]
        return json.loads(last)["hash"]

    def log(self, event: dict):
        entry = {**event, "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 "prev_hash": self._prev_hash}
        h = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
        entry["hash"] = h
        with self.path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
        self._prev_hash = h
        return h
```

## `src/api/server.py`
```python
from fastapi import FastAPI, Depends
from src.generation.answer_gen import answer
from src.retrieval.hybrid import query

app = FastAPI(title="mini-extract-temporal-kg")

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/ready")
def ready(): return {"ready": True}

@app.post("/query")
def query_endpoint(req: "QueryRequest"):
    # CODER: validate, call hybrid.query, generate answer, audit
    raise NotImplementedError
```

## `main.py`
```python
import argparse, threading, uvicorn
from src.api.server import app
from src.intake.watcher import start_watcher

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--watch-dir", default="./samples5")
    args = p.parse_args()
    threading.Thread(target=start_watcher, args=(args.watch_dir,), daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=args.port)

if __name__ == "__main__":
    main()
```

## `src/intake/watcher.py`
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

class Handler(FileSystemEventHandler):
    def __init__(self, queue): self.q = queue
    def on_created(self, e):
        if not e.is_directory and self._ok(e.src_path):
            self.q.enqueue(e.src_path)
    def on_modified(self, e):
        if not e.is_directory and self._ok(e.src_path):
            self.q.enqueue(e.src_path)
    @staticmethod
    def _ok(p):
        p = Path(p).resolve()
        root = Path("./samples5").resolve()
        return str(p).startswith(str(root)) and p.stat().st_size <= 500*1024*1024

def start_watcher(watch_dir="./samples5"):
    obs = Observer()
    obs.schedule(Handler(JobQueue()), watch_dir, recursive=True)
    obs.start()
    obs.join()
```

## `src/temporal/kg_schema.py`
```python
SCHEMA_STATEMENTS = [
    "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE",
    "CREATE CONSTRAINT fact_id_unique IF NOT EXISTS FOR (f:Fact) REQUIRE f.fact_id IS UNIQUE",
    "CREATE INDEX fact_current IF NOT EXISTS FOR (f:Fact) ON (f.current)",
    "CREATE INDEX fact_valid_at IF NOT EXISTS FOR (f:Fact) ON (f.valid_at)",
    "CREATE INDEX fact_invalid_at IF NOT EXISTS FOR (f:Fact) ON (f.invalid_at)",
    "CREATE INDEX fact_entity IF NOT EXISTS FOR (f:Fact) ON (f.entity_id)",
    "CREATE INDEX fact_predicate IF NOT EXISTS FOR (f:Fact) ON (f.predicate)",
]

def init_schema(driver):
    with driver.session() as s:
        for stmt in SCHEMA_STATEMENTS:
            s.run(stmt)
```
