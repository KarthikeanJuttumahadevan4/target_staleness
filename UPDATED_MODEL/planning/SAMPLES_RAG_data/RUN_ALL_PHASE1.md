---
format: html
---

# RUN_ALL_PHASE1.md – Execute All Phase 1 Creation Commands

This is a **single unified script** that creates all Phase 1 files in one go. 
Copy and paste the entire contents into your fish terminal from `/home/karthikean.juttumaha/mini-extract/`.

---

```fish
#!/usr/bin/env fish

set -x PYTHONPATH /home/karthikean.juttumaha/mini-extract/RAG_data

# =============================================================================
echo ">>>>>>>>> PHASE 1: CREATE ALL FILES <<<<<<<<<"
# =============================================================================

# Step 1: config.yaml
echo "Creating config.yaml..."
bash -c 'cat > /home/karthikean.juttumaha/mini-extract/RAG_data/config.yaml << "YAMLEOF"
ingestion:
  base_path: "samples5"
  watch_mode: false
  allowed_extensions:
    - ".txt"
    - ".pdf"
    - ".docx"
    - ".xlsx"
    - ".pptx"
  batch_size: 100

chunking:
  chunk_size: 512
  overlap: 102
  min_chunk_size: 50

embedding:
  model_name: "all-MiniLM-L6-v2"
  fallback_model: "BAAI/bge-small-en-v1.5"
  batch_size: 32
  normalize: true

vector_store:
  host: "localhost"
  port: 6333
  collection_name: "rag_deductions"
  vector_size: 384
  distance: "Cosine"

deduction:
  confidence_threshold: 0.7
  predicate_map:
    price: "has_price"
    cost: "has_price"
    amount: "has_price"
    headcount: "has_headcount"
    employees: "has_headcount"
    budget: "has_budget"
    date: "has_date"
    as of: "has_date"
    effective: "has_date"

comparison:
  similarity_threshold: 0.85
  confidence_threshold: 0.9

resolution:
  rules:
    - "R1"
    - "R2"
    - "R3"
    - "R4"
    - "R5"
    - "R6"
    - "R7"

directories:
  output: "RAG_data/output"
  logs: "RAG_data/logs"
  deductions_file: "RAG_data/deductions.jsonl"
  resolution_log: "RAG_data/resolution_log.jsonl"

performance:
  max_file_size_mb: 100
  max_concurrent_files: 10
  query_timeout_ms: 500
YAMLEOF'

# Step 2: config.py
echo "Creating config.py..."
bash -c 'cat > /home/karthikean.juttumaha/mini-extract/RAG_data/src/config.py << "PYEOF"
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import yaml

@dataclass
class IngestionConfig:
    base_path: str = "samples5"
    watch_mode: bool = False
    allowed_extensions: List[str] = field(default_factory=lambda: [".txt", ".pdf", ".docx", ".xlsx", ".pptx"])
    batch_size: int = 100

@dataclass
class ChunkingConfig:
    chunk_size: int = 512
    overlap: int = 102
    min_chunk_size: int = 50

@dataclass
class EmbeddingConfig:
    model_name: str = "all-MiniLM-L6-v2"
    fallback_model: str = "BAAI/bge-small-en-v1.5"
    batch_size: int = 32
    normalize: bool = True

@dataclass
class VectorStoreConfig:
    host: str = "localhost"
    port: int = 6333
    collection_name: str = "rag_deductions"
    vector_size: int = 384
    distance: str = "Cosine"

@dataclass
class DeductionConfig:
    confidence_threshold: float = 0.7
    predicate_map: Dict[str, str] = field(default_factory=lambda: {
        "price": "has_price", "cost": "has_price", "amount": "has_price",
        "headcount": "has_headcount", "employees": "has_headcount",
        "budget": "has_budget", "date": "has_date",
        "as of": "has_date", "effective": "has_date",
    })

@dataclass
class ComparisonConfig:
    similarity_threshold: float = 0.85
    confidence_threshold: float = 0.9

@dataclass
class ResolutionConfig:
    rules: List[str] = field(default_factory=lambda: ["R1","R2","R3","R4","R5","R6","R7"])

@dataclass
class DirectoryConfig:
    output: str = "RAG_data/output"
    logs: str = "RAG_data/logs"
    deductions_file: str = "RAG_data/deductions.jsonl"
    resolution_log: str = "RAG_data/resolution_log.jsonl"

@dataclass
class PerformanceConfig:
    max_file_size_mb: int = 100
    max_concurrent_files: int = 10
    query_timeout_ms: int = 500

@dataclass
class Config:
    ingestion: IngestionConfig = field(default_factory=IngestionConfig)
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    deduction: DeductionConfig = field(default_factory=DeductionConfig)
    comparison: ComparisonConfig = field(default_factory=ComparisonConfig)
    resolution: ResolutionConfig = field(default_factory=ResolutionConfig)
    directories: DirectoryConfig = field(default_factory=DirectoryConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)

class ConfigError(Exception):
    pass

def _parse_env_value(value: str, default: Any) -> Any:
    if isinstance(default, bool): return value.lower() in ("true","1","yes","on")
    elif isinstance(default, int): return int(value)
    elif isinstance(default, float): return float(value)
    elif isinstance(default, list):
        if value.startswith("["):
            import json; return json.loads(value)
        return [v.strip() for v in value.split(",") if v.strip()]
    return value

def _get_env_overrides() -> Dict[str, str]:
    overrides = {}
    for key, value in os.environ.items():
        if not key.startswith("RAG_"): continue
        config_key = key[4:].lower().replace("__",".").replace("_",".")
        overrides[config_key] = value
    return overrides

def _apply_overrides(config_dict: Dict[str, Any], overrides: Dict[str, str]) -> Dict[str, Any]:
    result = {}
    for k, v in config_dict.items():
        result[k] = v.copy() if isinstance(v, dict) else v
    for key, value in overrides.items():
        parts = key.split(".")
        current = result
        for part in parts[:-1]:
            if part not in current: current[part] = {}
            current = current[part]
            if not isinstance(current, dict): raise ConfigError(f"Cannot override {key}")
        final_key = parts[-1]
        default_val = current.get(final_key)
        current[final_key] = _parse_env_value(value, default_val if default_val is not None else value)
    return result

def _validate_config(config_dict: Dict[str, Any]) -> None:
    errors = []
    c = config_dict
    ing, ch, em, vs, de, cp, res, di, pe = c.get("ingestion",{}),c.get("chunking",{}),c.get("embedding",{}),c.get("vector_store",{}),c.get("deduction",{}),c.get("comparison",{}),c.get("resolution",{}),c.get("directories",{}),c.get("performance",{})
    if ing.get("batch_size",0) <= 0: errors.append("ingestion.batch_size > 0")
    cs,ov,mc = ch.get("chunk_size",0),ch.get("overlap",0),ch.get("min_chunk_size",0)
    if cs <= 0: errors.append("chunking.chunk_size > 0")
    if ov < 0 or ov >= cs: errors.append("0 <= chunking.overlap < chunk_size")
    if mc <= 0: errors.append("chunking.min_chunk_size > 0")
    if em.get("batch_size",0) <= 0: errors.append("embedding.batch_size > 0")
    p = vs.get("port",0)
    if p <= 0 or p > 65535: errors.append("vector_store.port 1-65535")
    if vs.get("vector_size",0) <= 0: errors.append("vector_store.vector_size > 0")
    if vs.get("distance","").upper() not in ("COSINE","DOT","EUCLIDEAN"): errors.append("vector_store.distance COSINE|DOT|EUCLIDEAN")
    if not (0.0 <= de.get("confidence_threshold",0) <= 1.0): errors.append("deduction.confidence_threshold 0-1")
    if not (0.0 <= cp.get("similarity_threshold",0) <= 1.0): errors.append("comparison.similarity_threshold 0-1")
    if not (0.0 <= cp.get("confidence_threshold",0) <= 1.0): errors.append("comparison.confidence_threshold 0-1")
    if pe.get("max_file_size_mb",0) <= 0: errors.append("performance.max_file_size_mb > 0")
    if pe.get("max_concurrent_files",0) <= 0: errors.append("performance.max_concurrent_files > 0")
    if pe.get("query_timeout_ms",0) <= 0: errors.append("performance.query_timeout_ms > 0")
    if errors: raise ConfigError("; ".join(errors))

_config_cache: Optional[Config] = None
def get_config(config_path: Optional[str] = None) -> Config:
    global _config_cache
    if _config_cache is not None: return _config_cache
    if config_path is None: config_path = os.path.join(os.getcwd(), "RAG_data", "config.yaml")
    if not os.path.exists(config_path): raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, "r") as f: config_dict = yaml.safe_load(f) or {}
    config_dict = _apply_overrides(config_dict, _get_env_overrides())
    _validate_config(config_dict)
    _config_cache = Config.from_dict(config_dict)
    return _config_cache
def reload_config() -> Config:
    global _config_cache; _config_cache = None; return get_config()
def reset_config() -> None:
    global _config_cache; _config_cache = None
PYEOF'

# Step 3: requirements.txt
echo "Creating requirements.txt..."
bash -c 'cat > /home/karthikean.juttumaha/mini-extract/RAG_data/requirements.txt << "TEXTEOF"
PyYAML>=6.0
qdrant-client>=1.8.0
sentence-transformers>=2.2.2
pdfplumber>=0.10.0
python-docx>=1.1.0
openpyxl>=3.1.0
python-pptx>=0.6.21
pytesseract>=0.3.10
pdf2image>=1.16.0
Pillow>=9.0.0
watchdog>=4.0.0
TEXTEOF'

# Step 4: text_chunkers.py
echo "Creating text_chunkers.py..."
bash -c 'cat > /home/karthikean.juttumaha/mini-extract/RAG_data/src/chunking/text_chunkers.py << "PYEOF"
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

@dataclass
class Chunk:
    chunk_id: str
    content: str
    file_path: str
    file_hash: str
    as_of: datetime
    chunk_index: int
    total_chunks: int
    start_offset: int
    end_offset: int
    metadata: Dict[str, Any]

class TextChunker:
    def __init__(self, chunk_size: int = 512, overlap: int = 102, min_chunk_size: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size

    def _tokenize(self, text: str) -> List[str]:
        return text.split()

    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        tokens = self._tokenize(text)
        if not tokens: return []
        effective_chunk_size = max(1, self.chunk_size - self.overlap)
        chunks = []
        index = 0
        chunk_idx = 0
        total = len(tokens)
        while index < total:
            end = min(index + self.chunk_size, total)
            chunk_tokens = tokens[index:end]
            if len(chunk_tokens) < self.min_chunk_size and chunk_idx > 0:
                index = end
                continue
            content = " ".join(chunk_tokens)
            chunks.append(Chunk(
                chunk_id=f"{metadata.get('file_path','unknown')}_{index}",
                content=content, file_path=metadata.get("file_path",""),
                file_hash=metadata.get("file_hash",""), as_of=metadata.get("as_of",datetime.now()),
                chunk_index=chunk_idx, total_chunks=0, start_offset=index, end_offset=end,
                metadata=metadata
            ))
            index += effective_chunk_size
            chunk_idx += 1
        for c in chunks: c.total_chunks = len(chunks)
        return chunks
PYEOF'

# Step 5: table_chunkers.py
echo "Creating table_chunkers.py..."
bash -c 'cat > /home/karthikean.juttumaha/mini-extract/RAG_data/src/chunking/table_chunkers.py << "PYEOF"
from datetime import datetime
from typing import Any, Dict, List
from src.chunking.text_chunkers import Chunk

class TableChunker:
    def chunk_table(self, data: List[List[str]], headers: List[str], metadata: Dict[str, Any]) -> List[Chunk]:
        chunks = []
        for row_index, row in enumerate(data):
            content = " | ".join(row)
            md = metadata.copy()
            md["table_headers"] = headers
            md["row_number"] = row_index
            md["extraction_path"] = "excel_table"
            chunks.append(Chunk(
                chunk_id=f"{md.get('file_path','unknown')}_row_{row_index}",
                content=content, file_path=md["file_path"], file_hash=md["file_hash"],
                as_of=md["as_of"] if isinstance(md["as_of"], datetime) else datetime.now(),
                chunk_index=row_index, total_chunks=0, start_offset=row_index, end_offset=row_index+1,
                metadata=md
            ))
        for c in chunks: c.total_chunks = len(chunks)
        return chunks
PYEOF'

# Step 6: embedder.py
echo "Creating embedder.py..."
bash -c 'cat > /home/karthikean.juttumaha/mini-extract/RAG_data/src/embedding/embedder.py << "PYEOF"
from typing import List

class Embedder:
    def __init__(self, model_name: str = None, batch_size: int = 32):
        from src.config import get_config
        config = get_config()
        self.model_name = model_name or config.embedding.model_name
        self.fallback_model = config.embedding.fallback_model
        self.batch_size = batch_size or config.embedding.batch_size
        self.normalize = config.embedding.normalize
        self._model = None

    def load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        except (ImportError, OSError):
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.fallback_model)
            except Exception as e:
                raise ImportError(f"Cannot load embedding model: {e}")

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts: return []
        if self._model is None: self.load_model()
        return self._model.encode(texts, batch_size=self.batch_size, normalize_embeddings=self.normalize).tolist()

    def embed_single(self, text: str) -> List[float]:
        return self.embed([text])[0]
PYEOF'

# Step 7: qdrant_client.py
echo "Creating qdrant_client.py..."
bash -c 'cat > /home/karthikean.juttumaha/mini-extract/RAG_data/src/storage/qdrant_client.py << "PYEOF"
from typing import Any, Dict, List, Optional

class VectorSearcher:
    def __init__(self, host: str = None, port: int = None, collection_name: str = None):
        from src.config import get_config
        config = get_config()
        self.host = host or config.vector_store.host
        self.port = port or config.vector_store.port
        self.collection_name = collection_name or config.vector_store.collection_name
        self._client = None

    def _get_client(self):
        if self._client is None:
            from qdrant_client import QdrantClient
            self._client = QdrantClient(host=self.host, port=self.port, prefer_grpc=False)
        return self._client

    def initialize_collection(self, vector_size: int = None, distance: str = None):
        from src.config import get_config
        config = get_config()
        vs = vector_size or config.vector_store.vector_size
        dist = distance or config.vector_store.distance
        self._get_client().recreate_collection(
            collection_name=self.collection_name,
            vectors_config={"size": vs, "distance": dist}
        )

    def index(self, vectors: List[List[float]], payloads: List[Dict[str, Any]], ids: Optional[List[str]] = None):
        client = self._get_client()
        points = [{"id": ids[i] if ids else None, "vector": v, "payload": p} for i, (v, p) in enumerate(zip(vectors, payloads))]
        client.upload_points(collection_name=self.collection_name, points=points, batch_size=100)

    def search(self, query_vector: List[float], limit: int = 10, filters: Optional[Dict] = None):
        client = self._get_client()
        results = client.search(
            collection_name=self.collection_name, query_vector=query_vector,
            limit=limit, with_payload=True, with_vectors=True
        )
        return [{"id": r.id, "score": r.score, "payload": r.payload, "vector": r.vector} for r in results]

    def delete_by_file(self, file_path: str):
        client = self._get_client()
        client.delete(
            collection_name=self.collection_name,
            points_selector={"must": [{"key": "file_path", "match": {"value": file_path}}]}
        )
PYEOF'

# Step 8: jsonl_store.py
echo "Creating jsonl_store.py..."
bash -c 'cat > /home/karthikean.juttumaha/mini-extract/RAG_data/src/storage/jsonl_store.py << "PYEOF"
import json
from pathlib import Path
from typing import Any, Dict, List

def read_deductions(file_path: str = None) -> List[Dict[str, Any]]:
    from src.config import get_config
    config = get_config()
    path = file_path or config.directories.deductions_file
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    deductions = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line: deductions.append(json.loads(line))
    return deductions

def write_deduction(deduction: Dict[str, Any], file_path: str = None) -> None:
    from src.config import get_config
    config = get_config()
    path = file_path or config.directories.deductions_file
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(deduction, default=str) + "\n")

def write_deductions(deductions: List[Dict[str, Any]], file_path: str = None) -> None:
    for d in deductions: write_deduction(d, file_path)
PYEOF'

# Step 9: fact_deducer.py
echo "Creating fact_deducer.py..."
bash -c 'cat > /home/karthikean.juttumaha/mini-extract/RAG_data/src/deduction/fact_deducer.py << "PYEOF"
import re
from datetime import datetime
from typing import Any, Dict, List
from dateutil.parser import parse as parse_date

from src.config import get_config
from src.chunking.text_chunkers import Chunk

class FactDeducer:
    def __init__(self, confidence_threshold: float = None, predicate_map: Dict[str, str] = None):
        config = get_config()
        self.confidence_threshold = confidence_threshold or config.deduction.confidence_threshold
        self.predicate_map = predicate_map or config.deduction.predicate_map
        self.patterns = [
            (r"(?:price|cost|amount)[\\s:]*[\\$]?(\\d+[.,]?\\d*)", "has_price", "numeric"),
            (r"headcount[\\s:]*(\\d+)", "has_headcount", "numeric"),
            (r"budget[\\s:]*[\\$]?(\\d+[.,]?\\d*)", "has_budget", "numeric"),
            (r"(?:date|as of|effective)[\\s:]+(\\d{4}-\\d{2}-\\d{2})", "has_date", "date"),
        ]

    def _normalize_value(self, value: str, obj_type: str) -> str:
        value = value.strip()
        if obj_type == "numeric":
            value = re.sub(r"[^\\d.]", "", value)
        elif obj_type == "date":
            try: value = parse_date(value).isoformat()
            except Exception: pass
        return value

    def _extract_subject(self, text: str, predicate: str) -> str:
        for p_key, p_val in self.predicate_map.items():
            if p_val == predicate:
                pattern = rf"(\\w+)\\s+{re.escape(p_key)}"
                match = re.search(pattern, text, re.IGNORECASE)
                if match: return match.group(1)
        return "unknown"

    def deduct(self, chunk: Chunk) -> List[Dict[str, Any]]:
        deductions = []
        text = chunk.content
        for pattern, predicate, obj_type in self.patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                match = match.strip()
                if not match: continue
                subject = self._extract_subject(text, predicate)
                value = self._normalize_value(match, obj_type)
                as_of_iso = chunk.as_of.isoformat() if isinstance(chunk.as_of, datetime) else str(chunk.as_of)
                deduction = {
                    "deduction_id": f"{chunk.chunk_id}_{predicate}_{hash(value) & 0xFFFF}",
                    "source_file_path": chunk.file_path, "chunk_id": chunk.chunk_id,
                    "as_of": as_of_iso, "subject_entity": subject,
                    "subject_entity_type": predicate.replace("has_", ""),
                    "predicate": predicate, "object_value": value, "object_type": obj_type,
                    "extraction_method": "regex", "confidence": 0.95,
                    "provenance": {"extraction_path": chunk.metadata.get("extraction_path","text"),
                        "model_used": "regex_patterns", "raw_text": text[:500]},
                    "metadata": chunk.metadata
                }
                if predicate in self.predicate_map.values():
                    deductions.append(deduction)
        return deductions

    def deduct_batch(self, chunks: List[Chunk]) -> List[Dict[str, Any]]:
        all_deductions = []
        for chunk in chunks: all_deductions.extend(self.deduct(chunk))
        return all_deductions
PYEOF'

# Step 10: file_ingestor.py
echo "Creating file_ingestor.py..."
bash -c 'cat > /home/karthikean.juttumaha/mini-extract/RAG_data/src/ingestion/file_ingestor.py << "PYEOF"
import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.config import get_config
from src.chunking.text_chunkers import Chunk, TextChunker

@dataclass
class IngestionResult:
    file_path: str; file_hash: str; as_of: datetime; timestamp_fallback: bool
    success: bool; error: Optional[str] = None; chunks: List[Chunk] = field(default_factory=list)

class FileIngestor:
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or get_config().ingestion.base_path)

    @staticmethod
    def calculate_hash(file_path: str) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""): sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def get_timestamp(file_path: str):
        from src.temporal.timestamp_extractor import TimestampExtractor
        extractor = TimestampExtractor()
        try: return extractor.get_as_of(Path(file_path))
        except Exception:
            import os as os_module
            return datetime.fromtimestamp(os_module.path.getmtime(file_path)), True

    def _extract_text(self, file_path: Path) -> Optional[str]:
        ext = file_path.suffix.lower()
        try:
            if ext == ".txt": return file_path.read_text(encoding="utf-8", errors="ignore")
            elif ext == ".pdf":
                try:
                    import pdfplumber
                    text = ""; p = pdfplumber.open(str(file_path))
                    for page in p.pages:
                        t = page.extract_text()
                        if t: text += t + "\n"
                    return text.strip() or None
                except Exception: return None
            elif ext == ".docx":
                try:
                    from docx import Document
                    return "\n".join([p.text for p in Document(str(file_path)).paragraphs])
                except Exception: return None
            elif ext == ".xlsx":
                try:
                    import openpyxl
                    wb = openpyxl.load_workbook(str(file_path), read_only=True)
                    texts = []
                    for sheet in wb:
                        for row in sheet.iter_rows(values_only=True):
                            texts.append(", ".join(str(c) if c else "" for c in row))
                    return "\n".join(texts)
                except Exception: return None
            elif ext == ".pptx":
                try:
                    from pptx import Presentation
                    return "\n".join(s.text for s in Presentation(str(file_path)).slides for shp in s.shapes if hasattr(shp, "text"))
                except Exception: return None
            return None
        except Exception: return None

    def ingest_one(self, file_path: str) -> IngestionResult:
        file_path = Path(file_path)
        if not file_path.exists(): return IngestionResult(file_path=str(file_path), file_hash="", as_of=datetime.now(), timestamp_fallback=True, success=False, error="File not found")
        if not file_path.is_file(): return IngestionResult(file_path=str(file_path), file_hash="", as_of=datetime.now(), timestamp_fallback=True, success=False, error="Not a file")
        ext = file_path.suffix.lower()
        config = get_config()
        if ext not in config.ingestion.allowed_extensions:
            return IngestionResult(file_path=str(file_path), file_hash="", as_of=datetime.now(), timestamp_fallback=True, success=False, error=f"Extension not allowed: {ext}")
        try:
            file_hash = self.calculate_hash(str(file_path))
            as_of, timestamp_fallback = self.get_timestamp(str(file_path))
            raw_text = self._extract_text(file_path)
            if raw_text is None:
                return IngestionResult(file_path=str(file_path), file_hash=file_hash, as_of=as_of, timestamp_fallback=timestamp_fallback, success=False, error="Failed to extract text")
            metadata = {"file_path": str(file_path), "file_hash": file_hash, "as_of": as_of, "extraction_path": "excel_table" if ext == ".xlsx" else "text"}
            chunker = TextChunker()
            chunks = chunker.chunk(raw_text, metadata)
            return IngestionResult(file_path=str(file_path), file_hash=file_hash, as_of=as_of, timestamp_fallback=timestamp_fallback, success=True, chunks=chunks)
        except Exception as e:
            return IngestionResult(file_path=str(file_path), file_hash="", as_of=datetime.now(), timestamp_fallback=True, success=False, error=str(e))

    def ingest_all(self) -> List[IngestionResult]:
        results = []
        for p in self.base_path.rglob("*"):
            if p.is_file(): results.append(self.ingest_one(str(p)))
        return results
PYEOF'

# Step 11: ingest_pipeline.py
echo "Creating ingest_pipeline.py..."
bash -c 'cat > /home/karthikean.juttumaha/mini-extract/RAG_data/ingest_pipeline.py << "PYEOF"
#!/usr/bin/env python3
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(description="Independent RAG Ingestion Pipeline")
    parser.add_argument("--batch", action="store_true", help="Run batch ingestion")
    parser.add_argument("--config", type=str, default=None, help="Path to config file")
    parser.add_argument("--base-path", type=str, default=None, help="Base path for ingestion")
    args = parser.parse_args()
    from src.config import get_config, reset_config
    from src.ingestion.file_ingestor import FileIngestor
    from src.embedding.embedder import Embedder
    from src.storage.qdrant_client import VectorSearcher
    from src.deduction.fact_deducer import FactDeducer
    from src.storage.jsonl_store import write_deduction
    if args.base_path:
        import os as os_module
        os_module.environ["RAG_INGESTION_BASE_PATH"] = args.base_path
    reset_config()
    config = get_config(args.config)
    ingestor = FileIngestor()
    vector_store = VectorSearcher()
    embedder = Embedder()
    deducer = FactDeducer()
    try: vector_store.initialize_collection(); print(f"Initialized Qdrant: {config.vector_store.collection_name}")
    except Exception as e: print(f"Qdrant init failed: {e}"); vector_store = None
    try: embedder.load_model(); print(f"Loaded model: {embedder.model_name}")
    except ImportError as e: print(f"Embedding model load failed: {e}"); embedder = None
    if args.batch:
        print(f"Starting batch ingestion of {config.ingestion.base_path}")
        results = ingestor.ingest_all()
        total_files = total_chunks = total_deductions = 0
        errors = []
        for result in results:
            if not result.success: errors.append(f"{result.file_path}: {result.error}"); continue
            total_files += 1; total_chunks += len(result.chunks)
            if embedder and result.chunks:
                texts = [c.content for c in result.chunks]
                embeddings = embedder.embed(texts)
                payloads = [{"chunk_id": c.chunk_id, "file_path": c.file_path, "file_hash": c.file_hash, "as_of": str(c.as_of), "chunk_index": c.chunk_index, "total_chunks": c.total_chunks, "start_offset": c.start_offset, "end_offset": c.end_offset, "extraction_path": c.metadata.get("extraction_path","text"), "content": c.content} for c in result.chunks]
                if vector_store:
                    try: vector_store.index(embeddings, payloads)
                    except Exception as e: print(f"Index error for {result.file_path}: {e}")
            deductions = deducer.deduct_batch(result.chunks)
            for d in deductions: write_deduction(d); total_deductions += 1
        print(f"\n_files:{total_files} chunks:{total_chunks} deductions:{total_deductions} errors:{len(errors)}")
        for e in errors[:5]: print(f"  - {e}")
    else: parser.print_help()

if __name__ == "__main__": main()
PYEOF'

chmod +x /home/karthikean.juttumaha/mini-extract/RAG_data/ingest_pipeline.py

# Step 12: conftest.py
echo "Creating conftest.py..."
bash -c 'cat > /home/karthikean.juttumaha/mini-extract/RAG_data/tests/conftest.py << "PYEOF"
import pytest
from pathlib import Path
import tempfile, shutil

@pytest.fixture
def temp_samples_dir():
    tmp = tempfile.mkdtemp(prefix="rag_test_")
    Path(tmp, "test.txt").write_text("Product X price is 100")
    yield tmp
    shutil.rmtree(tmp)
PYEOF'

# Step 13: test_config.py
echo "Creating test_config.py..."
bash -c 'cat > /home/karthikean.juttumaha/mini-extract/RAG_data/tests/unit/test_config.py << "PYEOF"
import os, pytest

def test_default_config():
    from src.config import get_config, reset_config
    reset_config()
    c = get_config()
    assert c.ingestion.base_path == "samples5"
    assert c.chunking.chunk_size == 512
    assert c.embedding.model_name == "all-MiniLM-L6-v2"

def test_env_override():
    from src.config import get_config, reset_config
    reset_config()
    os.environ["RAG_INGESTION_BASE_PATH"] = "/custom/path"
    c = get_config()
    assert c.ingestion.base_path == "/custom/path"
    del os.environ["RAG_INGESTION_BASE_PATH"]
    reset_config()
PYEOF'

# Step 14: tokens.py
echo "Creating tokens.py..."
bash -c 'cat > /home/karthikean.juttumaha/mini-extract/RAG_data/src/utils/tokens.py << "PYEOF"
import re

def tokenize(text: str) -> list:
    return re.findall(r"\\w+", text.lower())

def count_tokens(text: str) -> int:
    return len(tokenize(text))
PYEOF'

# =============================================================================
echo ""
echo ">>>>>>>>> VERIFICATION <<<<<<<<<"
echo ""

# Create __init__.py in remaining dirs
for dir in RAG_data/tests/data RAG_data/tests/data/sample_files RAG_data/tests/data/expected_outputs RAG_data/schemas; do
    touch $dir/__init__.py 2>/dev/null || true
done

# Count files
echo "=== Python Files ==="
find RAG_data -name "*.py" -type f | sort

echo ""
echo "=== All Files ==="  
find RAG_data -type f | sort

echo ""
echo "=== File Counts ==="
set -l py_count (find RAG_data -name "*.py" -type f | wc -l)
set -l all_count (find RAG_data -type f | wc -l)
echo "Python files: $py_count"
echo "Total files: $all_count"

echo ""
echo "=== Import Test ==="
cd /home/karthikean.juttumaha/mini-extract
python3 -c "
import sys
sys.path.insert(0, '/home/karthikean.juttumaha/mini-extract/RAG_data')
try:
    from src.config import get_config; print('✓ config')
    from src.ingestion.file_ingestor import FileIngestor; print('✓ file_ingestor')
    from src.chunking.text_chunkers import TextChunker; print('✓ text_chunkers')
    from src.embedding.embedder import Embedder; print('✓ embedder')
    from src.storage.qdrant_client import VectorSearcher; print('✓ qdrant_client')
    from src.deduction.fact_deducer import FactDeducer; print('✓ fact_deducer')
    from src.storage.jsonl_store import write_deduction, read_deductions; print('✓ jsonl_store')
    print('')
    print('✅ ALL IMPORTS SUCCESSFUL')
except Exception as e:
    print(f'❌ IMPORT FAILED: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo ">>>>>>>>> PHASE 1 COMPLETE <<<<<<<<<"
echo "Ready to run: python3 RAG_data/ingest_pipeline.py --batch"
```

---

## ✅ Simply Run This Command

From `/home/karthikean.juttumaha/mini-extract/`, run:

```fish
source /home/karthikean.juttumaha/mini-extract/RAG_data/RUN_ALL_PHASE1.md
```

Or copy the entire script above and paste it into your terminal.

---

**Result**: All Phase 1 P0 files will be created and verified.
