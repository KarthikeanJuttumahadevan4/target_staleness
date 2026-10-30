# SETUP_PHASE1.md – Complete Phase 1 File Creation Script

**Purpose**: This document contains **all fish-compatible commands** needed to create every file for Phase 1 of the Independent RAG System implementation.  
**Status**: All files ready to be created.  

Copy and paste each section into your terminal to create all files.

---

## 📦 Step 1: Create config.yaml

```fish
bash -c 'cat > RAG_data/config.yaml << "YAMLEOF"
# Independent RAG System Configuration
# All values can be overridden via environment variables using the RAG_ prefix.
# Example: RAG_INGESTION_BASE_PATH=/custom/path

# File Ingestion Configuration
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

# Text Chunking Configuration
chunking:
  chunk_size: 512
  overlap: 102
  min_chunk_size: 50

# Embedding Configuration
embedding:
  model_name: "all-MiniLM-L6-v2"
  fallback_model: "BAAI/bge-small-en-v1.5"
  batch_size: 32
  normalize: true

# Vector Store (Qdrant) Configuration
vector_store:
  host: "localhost"
  port: 6333
  collection_name: "rag_deductions"
  vector_size: 384
  distance: "Cosine"

# Fact Deduction Configuration
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

# RAG vs KG Comparison Configuration
comparison:
  similarity_threshold: 0.85
  confidence_threshold: 0.9

# Inconsistency Resolution Configuration
resolution:
  rules:
    - "R1"
    - "R2"
    - "R3"
    - "R4"
    - "R5"
    - "R6"
    - "R7"

# Directory Configuration
directories:
  output: "RAG_data/output"
  logs: "RAG_data/logs"
  deductions_file: "RAG_data/deductions.jsonl"
  resolution_log: "RAG_data/resolution_log.jsonl"

# Performance Configuration
performance:
  max_file_size_mb: 100
  max_concurrent_files: 10
  query_timeout_ms: 500
YAMLEOF'

echo "✓ Created RAG_data/config.yaml"
```

---

## 📦 Step 2: Create config.py

```fish
bash -c 'cat > RAG_data/src/config.py << "PYEOF"
"""
Configuration management for the Independent RAG System.
"""

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
        "budget": "has_budget", "date": "has_date", "as of": "has_date", "effective": "has_date",
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ingestion": {k: v for k, v in self.ingestion.__dict__.items() if not k.startswith("_")},
            "chunking": {k: v for k, v in self.chunking.__dict__.items() if not k.startswith("_")},
            "embedding": {k: v for k, v in self.embedding.__dict__.items() if not k.startswith("_")},
            "vector_store": {k: v for k, v in self.vector_store.__dict__.items() if not k.startswith("_")},
            "deduction": {k: v for k, v in self.deduction.__dict__.items() if not k.startswith("_")},
            "comparison": {k: v for k, v in self.comparison.__dict__.items() if not k.startswith("_")},
            "resolution": {k: v for k, v in self.resolution.__dict__.items() if not k.startswith("_")},
            "directories": {k: v for k, v in self.directories.__dict__.items() if not k.startswith("_")},
            "performance": {k: v for k, v in self.performance.__dict__.items() if not k.startswith("_")},
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Config":
        return cls(
            ingestion=IngestionConfig(**d.get("ingestion", {})),
            chunking=ChunkingConfig(**d.get("chunking", {})),
            embedding=EmbeddingConfig(**d.get("embedding", {})),
            vector_store=VectorStoreConfig(**d.get("vector_store", {})),
            deduction=DeductionConfig(**d.get("deduction", {})),
            comparison=ComparisonConfig(**d.get("comparison", {})),
            resolution=ResolutionConfig(**d.get("resolution", {})),
            directories=DirectoryConfig(**d.get("directories", {})),
            performance=PerformanceConfig(**d.get("performance", {})),
        )


class ConfigError(Exception):
    """Raised when configuration is invalid."""
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
    else:
        return value


def _get_env_overrides() -> Dict[str, Any]:
    overrides = {}
    for key, value in os.environ.items():
        if not key.startswith("RAG_"):
            continue
        config_key = key[4:].lower().replace("__", ".").replace("_", ".")
        overrides[config_key] = value
    return overrides


def _apply_overrides(config_dict: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
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
                raise ConfigError(f"Cannot override {key}: {\".\".join(parts[:-1])} is not a dict")
        final_key = parts[-1]
        default_val = current.get(final_key, value)
        current[final_key] = _parse_env_value(value, default_val)
    return result


def _validate_config(config_dict: Dict[str, Any]) -> None:
    errors = []
    ingestion = config_dict.get("ingestion", {})
    if ingestion.get("batch_size", 0) <= 0:
        errors.append("ingestion.batch_size must be > 0")
    chunking = config_dict.get("chunking", {})
    cs = chunking.get("chunk_size", 0)
    ov = chunking.get("overlap", 0)
    mc = chunking.get("min_chunk_size", 0)
    if cs <= 0: errors.append("chunking.chunk_size must be > 0")
    if ov < 0: errors.append("chunking.overlap must be >= 0")
    if mc <= 0: errors.append("chunking.min_chunk_size must be > 0")
    if ov >= cs: errors.append("chunking.overlap must be < chunking.chunk_size")
    emb = config_dict.get("embedding", {})
    if emb.get("batch_size", 0) <= 0:
        errors.append("embedding.batch_size must be > 0")
    vs_cfg = config_dict.get("vector_store", {})
    p = vs_cfg.get("port", 0)
    if p <= 0 or p > 65535:
        errors.append("vector_store.port must be between 1 and 65535")
    if vs_cfg.get("vector_size", 0) <= 0:
        errors.append("vector_store.vector_size must be > 0")
    if vs_cfg.get("distance", "").upper() not in ("COSINE", "DOT", "EUCLIDEAN"):
        errors.append("vector_store.distance must be COSINE, DOT, or EUCLIDEAN")
    ded = config_dict.get("deduction", {})
    ct = ded.get("confidence_threshold", 0)
    if not (0.0 <= ct <= 1.0): errors.append("deduction.confidence_threshold must be between 0.0 and 1.0")
    cmp = config_dict.get("comparison", {})
    st = cmp.get("similarity_threshold", 0)
    if not (0.0 <= st <= 1.0): errors.append("comparison.similarity_threshold must be between 0.0 and 1.0")
    ct2 = cmp.get("confidence_threshold", 0)
    if not (0.0 <= ct2 <= 1.0): errors.append("comparison.confidence_threshold must be between 0.0 and 1.0")
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

echo "✓ Created RAG_data/src/config.py"
```

---

## 📦 Step 3: Create requirements.txt

```fish
bash -c 'cat > RAG_data/requirements.txt << "TEXTEOF"
# Independent RAG System Dependencies
PyYAML>=6.0
Sentence-Transformers>=2.2.2
qdrant-client>=1.8.0
pdfplumber>=0.10.0
python-docx>=1.1.0
openpyxl>=3.1.0
python-pptx>=0.6.21
pytesseract>=0.3.10
pdf2image>=1.16.0
Pillow>=9.0.0
watchdog>=4.0.0
TEXTEOF'

echo "✓ Created RAG_data/requirements.txt"
```

---

## 📦 Step 4: Create file_ingestor.py

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
    def __init__(self, base_path: Optional[str] = None, config_path: Optional[str] = None):
        from src.config import get_config
        self.config = get_config(config_path)
        if base_path is None:
            self.base_path = Path(self.config.ingestion.base_path)
        else:
            self.base_path = Path(base_path)
        self.ingested_files: Dict[str, str] = {}  # file_path -> hash

    @staticmethod
    def calculate_hash(file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def get_timestamp(file_path: str) -> tuple:
        """Get file modification timestamp using extract.py fallback to os.path.getmtime."""
        from src.temporal.timestamp_extractor import TimestampExtractor
        extractor = TimestampExtractor()
        try:
            as_of, fallback = extractor.get_as_of(Path(file_path))
            return as_of, fallback
        except Exception:
            import os
            mtime = os.path.getmtime(file_path)
            return datetime.fromtimestamp(mtime), True

    def ingest_one(self, file_path: str) -> IngestionResult:
        """Ingest a single file."""
        from src.chunking.text_chunkers import TextChunker
        from src.chunking.table_chunkers import TableChunker
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            return IngestionResult(
                file_path=str(file_path),
                file_hash="",
                as_of=datetime.now(),
                timestamp_fallback=True,
                success=False,
                error=f"File not found: {file_path}"
            )
        
        if not file_path.is_file():
            return IngestionResult(
                file_path=str(file_path),
                file_hash="",
                as_of=datetime.now(),
                timestamp_fallback=True,
                success=False,
                error=f"Not a file: {file_path}"
            )
        
        extension = file_path.suffix.lower()
        if extension not in self.config.ingestion.allowed_extensions:
            return IngestionResult(
                file_path=str(file_path), file_hash="", as_of=datetime.now(),
                timestamp_fallback=True, success=False,
                error=f"Extension not allowed: {extension}"
            )
        
        try:
            file_hash = self.calculate_hash(str(file_path))
            as_of, timestamp_fallback = self.get_timestamp(str(file_path))
            
            # Check if already ingested
            if str(file_path) in self.ingested_files:
                if self.ingested_files[str(file_path)] == file_hash:
                    return IngestionResult(
                        file_path=str(file_path), file_hash=file_hash,
                        as_of=as_of, timestamp_fallback=timestamp_fallback,
                        success=True, error=None, chunks=[]
                    )
            
            # Extract text based on file type
            raw_text = self._extract_text(file_path, extension)
            if raw_text is None:
                return IngestionResult(
                    file_path=str(file_path), file_hash=file_hash,
                    as_of=as_of, timestamp_fallback=timestamp_fallback,
                    success=False, error=f"Failed to extract text from {file_path}"
                )
            
            # Chunk the text
            chunker = TableChunker() if extension in (".xlsx",) else TextChunker()
            metadata = {
                "file_path": str(file_path),
                "file_hash": file_hash,
                "as_of": as_of,
                "extraction_path": "excel_table" if extension == ".xlsx" else "text"
            }
            chunks = chunker.chunk(raw_text, metadata)
            
            # Update ingested files tracker
            self.ingested_files[str(file_path)] = file_hash
            
            return IngestionResult(
                file_path=str(file_path), file_hash=file_hash,
                as_of=as_of, timestamp_fallback=timestamp_fallback,
                success=True, error=None, chunks=chunks
            )
            
        except Exception as e:
            return IngestionResult(
                file_path=str(file_path), file_hash="",
                as_of=datetime.now(), timestamp_fallback=True,
                success=False, error=str(e)
            )

    def _extract_text(self, file_path: Path, extension: str) -> Optional[str]:
        """Extract text from file based on extension."""
        try:
            if extension == ".txt":
                return file_path.read_text(encoding="utf-8", errors="ignore")
            elif extension == ".pdf":
                try:
                    import pdfplumber
                    text = ""
                    with pdfplumber.open(str(file_path)) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                    return text if text.strip() else None
                except Exception:
                    return None
            elif extension == ".docx":
                try:
                    from docx import Document
                    doc = Document(str(file_path))
                    return "\n".join([p.text for p in doc.paragraphs])
                except Exception:
                    return None
            elif extension == ".xlsx":
                try:
                    # For tables, we return structured data
                    import openpyxl
                    wb = openpyxl.load_workbook(str(file_path), read_only=True)
                    texts = []
                    for sheet in wb:
                        for row in sheet.iter_rows(values_only=True):
                            texts.append(", ".join(str(cell) if cell else "" for cell in row))
                    return "\n".join(texts)
                except Exception:
                    return None
            elif extension == ".pptx":
                try:
                    from pptx import Presentation
                    prs = Presentation(str(file_path))
                    texts = []
                    for slide in prs.slides:
                        for shape in slide.shapes:
                            if hasattr(shape, "text"):
                                texts.append(shape.text)
                    return "\n".join(texts)
                except Exception:
                    return None
            else:
                return None
        except Exception:
            return None

    def ingest_all(self) -> List[IngestionResult]:
        """Ingest all files in base_path recursively."""
        results = []
        for p in self.base_path.rglob("*"):
            if p.is_file():
                result = self.ingest_one(str(p))
                results.append(result)
        return results
PYEOF'

echo "✓ Created RAG_data/src/ingestion/file_ingestor.py"
```

---

## 📦 Continue with Next Files

Continue with these commands in the same session. Each section creates one or more files.

### Step 5: Create text_chunkers.py

```fish
bash -c 'cat > RAG_data/src/chunking/text_chunkers.py << "PYEOF"
"""Text Chunking utilities for the Independent RAG System."""

import re
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
        """Simple tokenizer: split on whitespace."""
        return text.split()

    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Split text into chunks with overlap."""
        tokens = self._tokenize(text)
        if not tokens:
            return []
        
        effective_chunk_size = self.chunk_size - self.overlap
        if effective_chunk_size <= 0:
            effective_chunk_size = self.chunk_size
        
        chunks = []
        index = 0
        chunk_idx = 0
        total = len(tokens)
        
        while index < total:
            end = min(index + self.chunk_size, total)
            chunk_tokens = tokens[index:end]
            
            # Check if chunk is too small and we can merge with previous
            if len(chunk_tokens) < self.min_chunk_size and chunk_idx > 0:
                index = end
                continue
            
            content = " ".join(chunk_tokens)
            chunk_id = f"{metadata.get('file_path', 'unknown')}_{index}_{chunk_idx}"
            
            chunk = Chunk(
                chunk_id=chunk_id,
                content=content,
                file_path=metadata.get("file_path", ""),
                file_hash=metadata.get("file_hash", ""),
                as_of=metadata.get("as_of", datetime.now()),
                chunk_index=chunk_idx,
                total_chunks=0,  # Will be updated
                start_offset=index,
                end_offset=end,
                metadata=metadata
            )
            chunks.append(chunk)
            
            index += effective_chunk_size
            chunk_idx += 1
        
        # Update total_chunks for all chunks
        for c in chunks:
            c.total_chunks = len(chunks)
        
        return chunks


class TableChunker:
    def __init__(self):
        pass

    def chunk(self, data: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Split table data into row-based chunks."""
        lines = data.strip().split("\n")
        if not lines:
            return []
        
        # Try to parse as CSV or table
        chunks = []
        for idx, line in enumerate(lines):
            content = line.strip()
            if not content:
                continue
            
            chunk_id = f"{metadata.get('file_path', 'unknown')}_row_{idx}"
            metadata_copy = metadata.copy()
            metadata_copy["row_number"] = idx
            metadata_copy["extraction_path"] = "excel_table"
            
            chunk = Chunk(
                chunk_id=chunk_id,
                content=content,
                file_path=metadata.get("file_path", ""),
                file_hash=metadata.get("file_hash", ""),
                as_of=metadata.get("as_of", datetime.now()),
                chunk_index=idx,
                total_chunks=0,
                start_offset=idx,
                end_offset=idx + 1,
                metadata=metadata_copy
            )
            chunks.append(chunk)
        
        for c in chunks:
            c.total_chunks = len(chunks)
        
        return chunks
PYEOF'

echo "✓ Created RAG_data/src/chunking/text_chunkers.py"
```

### Step 6: Create table_chunkers.py (simple version)

```fish
bash -c 'cat > RAG_data/src/chunking/table_chunkers.py << "PYEOF"
"""Table Chunking utilities for the Independent RAG System."""

from datetime import datetime
from typing import Any, Dict, List


class TableChunker:
    def __init__(self):
        pass

    def chunk_table(self, data: List[List[str]], headers: List[str], metadata: Dict[str, Any]) -> List:
        """Split table rows into chunks."""
        from src.chunking.text_chunkers import Chunk
        chunks = []
        for row_index, row in enumerate(data):
            content = " | ".join(row)
            metadata_copy = metadata.copy()
            metadata_copy["table_headers"] = headers
            metadata_copy["row_number"] = row_index
            metadata_copy["extraction_path"] = "excel_table"
            
            chunk = Chunk(
                chunk_id=f"{metadata.get('file_path', 'unknown')}_row_{row_index}",
                content=content,
                file_path=metadata.get("file_path", ""),
                file_hash=metadata.get("file_hash", ""),
                as_of=metadata.get("as_of", datetime.now()),
                chunk_index=row_index,
                total_chunks=0,
                start_offset=row_index,
                end_offset=row_index + 1,
                metadata=metadata_copy
            )
            chunks.append(chunk)
        
        for c in chunks:
            c.total_chunks = len(chunks)
        
        return chunks
PYEOF'

echo "✓ Created RAG_data/src/chunking/table_chunkers.py"
```

### Step 7: Create embedder.py

```fish
bash -c 'cat > RAG_data/src/embedding/embedder.py << "PYEOF"
"""Embedding utilities for the Independent RAG System."""

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
        """Load the embedding model."""
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
        """Generate embeddings for a list of texts."""
        if not texts:
            return []
        if self._model is None:
            self.load_model()
        embeddings = self._model.encode(texts, batch_size=self.batch_size, normalize_embeddings=self.normalize)
        return embeddings.tolist()

    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self.embed([text])[0]
PYEOF'

echo "✓ Created RAG_data/src/embedding/embedder.py"
```

### Step 8: Create qdrant_client.py

```fish
bash -c 'cat > RAG_data/src/storage/qdrant_client.py << "PYEOF"
"""Qdrant client for vector storage."""

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
        """Lazy initialization of Qdrant client."""
        if self._client is None:
            from qdrant_client import QdrantClient
            self._client = QdrantClient(host=self.host, port=self.port, prefer_grpc=False)
        return self._client

    def initialize_collection(self, vector_size: int = None, distance: str = None):
        """Create the collection if it does not exist."""
        from src.config import get_config
        config = get_config()
        vs = vector_size or config.vector_store.vector_size
        dist = distance or config.vector_store.distance
        client = self._get_client()
        client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config={
                "size": vs,
                "distance": dist
            }
        )

    def index(self, vectors: List[List[float]], payloads: List[Dict[str, Any]], ids: Optional[List[str]] = None):
        """Index vectors with payloads."""
        client = self._get_client()
        points = []
        for i, (vector, payload) in enumerate(zip(vectors, payloads)):
            point_id = ids[i] if ids else None
            points.append({
                "id": point_id,
                "vector": vector,
                "payload": payload
            })
        client.upload_points(
            collection_name=self.collection_name,
            points=points,
            batch_size=100
        )

    def search(self, query_vector: List[float], limit: int = 10, filters: Optional[Dict] = None):
        """Search the vector index."""
        client = self._get_client()
        results = client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True,
            with_vectors=True
        )
        return {
            "id": r.id,
            "score": r.score,
            "payload": r.payload,
            "vector": r.vector
        } for r in results

    def delete_by_file(self, file_path: str):
        """Delete all entries for a specific file."""
        client = self._get_client()
        client.delete(
            collection_name=self.collection_name,
            points_selector={"must": [{"key": "file_path", "match": {"value": file_path}}]}
        )
PYEOF'

echo "✓ Created RAG_data/src/storage/qdrant_client.py"
```

--- 

**⚠️ IMPORTANT**: Run all commands from `/home/karthikean.juttumaha/mini-extract/` in sequence. 
After creation, verify with:
```fish
echo "=== Files Created ==="
find RAG_data -name "*.py" -type f | sort
echo ""
echo "=== All Files ==="
find RAG_data -type f | sort
```

**Continue to Part 2 for remaining files (fact_deducer.py, jsonl_store.py, ingest_pipeline.py, tests)**
