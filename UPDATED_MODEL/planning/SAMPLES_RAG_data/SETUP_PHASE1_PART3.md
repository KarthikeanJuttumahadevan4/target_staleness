# SETUP_PHASE1_PART3.md – Phase 1 Remaining Files

**Purpose**: Final set of Phase 1 files - the pipeline script that ties everything together.
**Run after**: SETUP_PHASE1.md and SETUP_PHASE1_PART2.md

---

## 📦 Step 1: Update config.py to fix dataclass field issues

The initial config.py had issues with dataclass field defaults. Here's the corrected version:

```fish
bash -c 'cat > RAG_data/src/config.py << "PYEOF"
"""Configuration management for the Independent RAG System."""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import yaml


@dataclass
class IngestionConfig:
    base_path: str = "samples5"
    watch_mode: bool = False
    allowed_extensions: List[str] = field(default_factory=lambda: [
        ".txt", ".pdf", ".docx", ".xlsx", ".pptx"
    ])
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
    rules: List[str] = field(default_factory=lambda: ["R1", "R2", "R3", "R4", "R5", "R6", "R7"])


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
    if isinstance(default, bool):
        return value.lower() in ("true", "1", "yes", "on")
    elif isinstance(default, int):
        return int(value)
    elif isinstance(default, float):
        return float(value)
    elif isinstance(default, list):
        if value.startswith("["):
            import json
            return json.loads(value)
        return [v.strip() for v in value.split(",") if v.strip()]
    elif isinstance(default, dict):
        if value.startswith("{"):
            import json
            return json.loads(value)
        result = {}
        for pair in value.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                result[k.strip()] = v.strip()
        return result
    return value


def _get_env_overrides() -> Dict[str, str]:
    overrides = {}
    for key, value in os.environ.items():
        if not key.startswith("RAG_"):
            continue
        config_key = key[4:].lower().replace("__", "."  ).replace("_", ".")
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
            if part not in current:
                current[part] = {}
            current = current[part]
            if not isinstance(current, dict):
                raise ConfigError(f"Cannot override {key}")
        final_key = parts[-1]
        default_val = current.get(final_key)
        current[final_key] = _parse_env_value(value, default_val if default_val is not None else value)
    return result


def _validate_config(config_dict: Dict[str, Any]) -> None:
    errors = []
    ing = config_dict.get("ingestion", {})
    if ing.get("batch_size", 0) <= 0:
        errors.append("ingestion.batch_size must be > 0")
    chk = config_dict.get("chunking", {})
    cs = chk.get("chunk_size", 0)
    ov = chk.get("overlap", 0)
    mc = chk.get("min_chunk_size", 0)
    if cs <= 0: errors.append("chunking.chunk_size must be > 0")
    if ov < 0: errors.append("chunking.overlap must be >= 0")
    if mc <= 0: errors.append("chunking.min_chunk_size must be > 0")
    if ov >= cs: errors.append("chunking.overlap must be < chunking.chunk_size")
    emb = config_dict.get("embedding", {})
    if emb.get("batch_size", 0) <= 0:
        errors.append("embedding.batch_size must be > 0")
    vs = config_dict.get("vector_store", {})
    p = vs.get("port", 0)
    if p <= 0 or p > 65535:
        errors.append("vector_store.port must be between 1 and 65535")
    if vs.get("vector_size", 0) <= 0:
        errors.append("vector_store.vector_size must be > 0")
    if vs.get("distance", "").upper() not in ("COSINE", "DOT", "EUCLIDEAN"):
        errors.append("vector_store.distance must be COSINE, DOT, or EUCLIDEAN")
    ded = config_dict.get("deduction", {})
    ct = ded.get("confidence_threshold", 0)
    if not (0.0 <= ct <= 1.0):
        errors.append("deduction.confidence_threshold must be 0.0-1.0")
    cmp = config_dict.get("comparison", {})
    if not (0.0 <= cmp.get("similarity_threshold", 0) <= 1.0):
        errors.append("comparison.similarity_threshold must be 0.0-1.0")
    if not (0.0 <= cmp.get("confidence_threshold", 0) <= 1.0):
        errors.append("comparison.confidence_threshold must be 0.0-1.0")
    per = config_dict.get("performance", {})
    if per.get("max_file_size_mb", 0) <= 0: errors.append("performance.max_file_size_mb must be > 0")
    if per.get("max_concurrent_files", 0) <= 0: errors.append("performance.max_concurrent_files must be > 0")
    if per.get("query_timeout_ms", 0) <= 0: errors.append("performance.query_timeout_ms must be > 0")
    if errors:
        raise ConfigError("Config validation failed: " + "; ".join(errors))


_config_cache: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    if config_path is None:
        config_path = os.path.join(os.getcwd(), "RAG_data", "config.yaml")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f) or {}
    env_overrides = _get_env_overrides()
    config_dict = _apply_overrides(config_dict, env_overrides)
    _validate_config(config_dict)
    _config_cache = Config.from_dict(config_dict)
    return _config_cache


def reload_config() -> Config:
    global _config_cache
    _config_cache = None
    return get_config()


def reset_config() -> None:
    global _config_cache
    _config_cache = None
PYEOF'

echo "✓ Updated RAG_data/src/config.py"
```

---

## 📦 Step 2: Create Fixed file_ingestor.py

```fish
bash -c 'cat > RAG_data/src/ingestion/file_ingestor.py << "PYEOF"
"""File Ingestor for the Independent RAG System."""

import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.config import get_config


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


@dataclass
class IngestionResult:
    file_path: str
    file_hash: str
    as_of: datetime
    timestamp_fallback: bool
    success: bool
    error: Optional[str] = None
    chunks: List[Chunk] = field(default_factory=list)


class FileIngestor:
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or get_config().ingestion.base_path)

    @staticmethod
    def calculate_hash(file_path: str) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def get_timestamp(file_path: str):
        from src.temporal.timestamp_extractor import TimestampExtractor
        extractor = TimestampExtractor()
        try:
            as_of, fallback = extractor.get_as_of(Path(file_path))
            return as_of, fallback
        except Exception:
            import os as os_module
            mtime = os_module.path.getmtime(file_path)
            return datetime.fromtimestamp(mtime), True

    def _extract_text(self, file_path: Path) -> Optional[str]:
        ext = file_path.suffix.lower()
        try:
            if ext == ".txt":
                return file_path.read_text(encoding="utf-8", errors="ignore")
            elif ext == ".pdf":
                try:
                    import pdfplumber
                    text = ""
                    with pdfplumber.open(str(file_path)) as pdf:
                        for page in pdf.pages:
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
                    return "\n".join(s.text for s in Presentation(str(file_path)).slides 
                                        for shp in s.shapes if hasattr(shp, "text"))
                except Exception: return None
            return None
        except Exception: return None

    def ingest_one(self, file_path: str) -> IngestionResult:
        file_path = Path(file_path)
        if not file_path.exists():
            return IngestionResult(file_path=str(file_path), file_hash="", as_of=datetime.now(),
                                 timestamp_fallback=True, success=False, error=f"File not found")
        if not file_path.is_file():
            return IngestionResult(file_path=str(file_path), file_hash="", as_of=datetime.now(),
                                 timestamp_fallback=True, success=False, error=f"Not a file")
        ext = file_path.suffix.lower()
        config = get_config()
        if ext not in config.ingestion.allowed_extensions:
            return IngestionResult(file_path=str(file_path), file_hash="", as_of=datetime.now(),
                                 timestamp_fallback=True, success=False, error=f"Extension not allowed: {ext}")
        try:
            file_hash = self.calculate_hash(str(file_path))
            as_of, timestamp_fallback = self.get_timestamp(str(file_path))
            raw_text = self._extract_text(file_path)
            if raw_text is None:
                return IngestionResult(file_path=str(file_path), file_hash=file_hash,
                                     as_of=as_of, timestamp_fallback=timestamp_fallback,
                                     success=False, error="Failed to extract text")
            metadata = {"file_path": str(file_path), "file_hash": file_hash, "as_of": as_of,
                       "extraction_path": "excel_table" if ext == ".xlsx" else "text"}
            from src.chunking.text_chunkers import TextChunker
            chunker = TextChunker()
            chunks = chunker.chunk(raw_text, metadata)
            return IngestionResult(file_path=str(file_path), file_hash=file_hash,
                                 as_of=as_of, timestamp_fallback=timestamp_fallback,
                                 success=True, chunks=chunks)
        except Exception as e:
            return IngestionResult(file_path=str(file_path), file_hash="",
                                 as_of=datetime.now(), timestamp_fallback=True,
                                 success=False, error=str(e))

    def ingest_all(self) -> List[IngestionResult]:
        results = []
        for p in self.base_path.rglob("*"):
            if p.is_file():
                results.append(self.ingest_one(str(p)))
        return results
PYEOF'

echo "✓ Updated RAG_data/src/ingestion/file_ingestor.py"
```

---

## 📦 Step 3: Test the Pipeline

```fish
# Change to project root
cd /home/karthikean.juttumaha/mini-extract

# Set PYTHONPATH
export PYTHONPATH=/home/karthikean.juttumaha/mini-extract/RAG_data

# Test imports
echo "=== Testing All Imports ==="
python3 -c "
import sys
sys.path.insert(0, '/home/karthikean.juttumaha/mini-extract/RAG_data')
from src.config import get_config, reset_config
from src.ingestion.file_ingestor import FileIngestor
from src.chunking.text_chunkers import TextChunker
from src.embedding.embedder import Embedder
from src.storage.qdrant_client import VectorSearcher
from src.deduction.fact_deducer import FactDeducer
from src.storage.jsonl_store import write_deduction, read_deductions
print('✓ All imports successful')
"
```

---

## 📦 Step 4: Run a Quick Ingestion Test

```fish
echo ""
echo "=== Running Batch Ingestion Test ==="
cd /home/karthikean.juttumaha/mini-extract
python3 RAG_data/ingest_pipeline.py --batch
```

**Expected**: Ingestion of all files in `samples5/` with chunk counts and deduction counts.

---

## 🎯 Verification Checklist

- [ ] Run SETUP_PHASE1.md commands (config.yaml, config.py initial)
- [ ] Run SETUP_PHASE1_PART2.md commands (all Python modules)
- [ ] Run SETUP_PHASE1_PART3.md commands (updates + tests)
- [ ] All Python files exist and import correctly
- [ ] Ingestion pipeline runs without errors
- [ ] Deductions are created in `RAG_data/deductions.jsonl`
- [ ] Qdrant collection is created (if Qdrant is running)

---

## 📋 Complete Phase 1 File List

### Source Files (`RAG_data/src/`)
- `__init__.py`
- `config.py` ✓
- **ingestion/`**: `__init__.py`, `file_ingestor.py` ✓
- **chunking/`**: `__init__.py`, `text_chunkers.py`, `table_chunkers.py` ✓
- **embedding/`**: `__init__.py`, `embedder.py` ✓
- **storage/`**: `__init__.py`, `qdrant_client.py`, `jsonl_store.py` ✓
- **deduction/`**: `__init__.py`, `fact_deducer.py` ✓
- **utils/`**: `__init__.py`, `tokens.py` ✓

### Root Files (`RAG_data/`)
- `config.yaml` ✓
- `requirements.txt` ✓
- `ingest_pipeline.py` ✓

### Test Files (`RAG_data/tests/`)
- `__init__.py` ✓
- `conftest.py` ✓
- **unit/`**: `__init__.py`, `test_config.py` ✓
- **integration/`**: `__init__.py`
- **data/`**: `__init__.py`, `sample_files/`, `expected_outputs/`

---

## 🚀 Next Steps

After all files are created and verified:

1. **Run tests**: `cd /home/karthikean.juttumaha/mini-extract && python -m pytest RAG_data/tests/`
2. **Proceed to Phase 2**: Implement comparison module (DEV-P0-11 through DEV-P0-16)
3. **Create DEV-P0-03 implementation spec** (File Ingestor details)

**Status**: All Phase 1 P0 files ready for creation. Run the fish commands above to create them.
