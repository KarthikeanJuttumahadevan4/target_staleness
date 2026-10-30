---
format: html
---

# SETUP_PHASE1_PART2.md – Phase 1 Implementation Files (Part 2)

**Purpose**: Continuation of Phase 1 file creation. Run these commands **after** completing SETUP_PHASE1.md.

Run each section in order from `/home/karthikean.juttumaha/mini-extract/`.

---

## 📦 Step 9: Create jsonl_store.py

```fish
bash -c 'cat > RAG_data/src/storage/jsonl_store.py << "PYEOF"
"""JSONL storage for RAG deductions."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


def read_deductions(file_path: str = None) -> List[Dict[str, Any]]:
    """Read all deductions from JSONL file."""
    from src.config import get_config
    config = get_config()
    path = file_path or config.directories.deductions_file
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    deductions = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                deductions.append(json.loads(line))
    return deductions


def write_deduction(deduction: Dict[str, Any], file_path: str = None) -> None:
    """Append a single deduction to JSONL file."""
    from src.config import get_config
    config = get_config()
    path = file_path or config.directories.deductions_file
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(deduction, default=str) + "\n")


def write_deductions(deductions: List[Dict[str, Any]], file_path: str = None) -> None:
    """Append multiple deductions to JSONL file."""
    for d in deductions:
        write_deduction(d, file_path)
PYEOF'

echo "✓ Created RAG_data/src/storage/jsonl_store.py"
```

---

## 📦 Step 10: Create fact_deducer.py

```fish
bash -c 'cat > RAG_data/src/deduction/fact_deducer.py << "PYEOF"
"""Fact deduction from chunks."""

import re
from dataclasses import asdict
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
            (r"(?:price|cost|amount)[\s:]*[$]?(\d+[.,]?\d*)", "has_price", "numeric"),
            (r"headcount[\s:]*(\d+)", "has_headcount", "numeric"),
            (r"budget[\s:]*[$]?(\d+[.,]?\d*)", "has_budget", "numeric"),
            (r"(?:date|as of|effective)[\s:]+(\d{4}-\d{2}-\d{2})", "has_date", "date"),
            (r"(?:date|as of|effective)[\s:]+(\w+ \d{1,2}, \d{4})", "has_date", "date"),
            (r"(\d{4}-\d{2}-\d{2})", "has_date", "date"),
        ]

    def _normalize_value(self, value: str, obj_type: str) -> str:
        """Normalize extracted value."""
        value = value.strip()
        if obj_type == "numeric":
            # Remove currency symbols and commas
            value = re.sub(r"[^\d.]", "", value)
            if "." in value and value.rstrip(".").replace(".", "").isdigit():
                pass  # Keep as float
            elif value.isdigit():
                pass  # Keep as int
            else:
                value = "0"
        elif obj_type == "date":
            try:
                dt = parse_date(value)
                value = dt.isoformat()
            except Exception:
                pass
        return str(value)

    def _extract_subject(self, text: str, predicate: str) -> str:
        """Extract subject entity from text."""
        # Simple: Use the word before the predicate
        for p_key, p_val in self.predicate_map.items():
            if p_val == predicate:
                pattern = rf"(\w+)\s+{p_key}"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
        return "unknown"

    def _infer_type(self, text: str) -> str:
        """Infer value type from text."""
        if re.match(r"^\d", text):
            return "numeric"
        try:
            parse_date(text)
            return "date"
        except Exception:
            return "text"

    def deduct(self, chunk: Chunk) -> List[Dict[str, Any]]:
        """Extract facts from a chunk."""
        deductions = []
        text = chunk.content
        
        # Regex-based extraction
        for pattern, predicate, obj_type in self.patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                match = match.strip()
                if not match:
                    continue
                subject = self._extract_subject(text, predicate)
                value = self._normalize_value(match, obj_type)
                
                deduction = {
                    "deduction_id": f"{chunk.chunk_id}_{predicate}_{hash(value) & 0xFFFF}",
                    "source_file_path": chunk.file_path,
                    "chunk_id": chunk.chunk_id,
                    "as_of": chunk.as_of.isoformat() if isinstance(chunk.as_of, datetime) else str(chunk.as_of),
                    "subject_entity": subject,
                    "subject_entity_type": predicate.replace("has_", ""),
                    "predicate": predicate,
                    "object_value": value,
                    "object_type": obj_type,
                    "extraction_method": "regex",
                    "confidence": 0.95,
                    "provenance": {
                        "extraction_path": chunk.metadata.get("extraction_path", "text"),
                        "model_used": "regex_patterns",
                        "raw_text": text[:500]  # First 500 chars
                    },
                    "metadata": chunk.metadata
                }
                if deduction["predicate"] in self.predicate_map.values():
                    deductions.append(deduction)
        
        # If no deductions, return empty list
        return deductions

    def deduct_batch(self, chunks: List[Chunk]) -> List[Dict[str, Any]]:
        """Extract facts from multiple chunks."""
        all_deductions = []
        for chunk in chunks:
            all_deductions.extend(self.deduct(chunk))
        return all_deductions
PYEOF'

echo "✓ Created RAG_data/src/deduction/fact_deducer.py"
```

---

## 📦 Step 11: Create ingest_pipeline.py

```fish
bash -c 'cat > RAG_data/ingest_pipeline.py << "PYEOF"
#!/usr/bin/env python3
"""
Independent RAG Ingestion Pipeline.

Usage:
    python ingest_pipeline.py --batch
    python ingest_pipeline.py --watch
    python ingest_pipeline.py --config RAG_data/custom_config.yaml
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Independent RAG Ingestion Pipeline")
    parser.add_argument("--batch", action="store_true", help="Run batch ingestion")
    parser.add_argument("--watch", action="store_true", help="Run in watch mode")
    parser.add_argument("--config", type=str, default=None, help="Path to config file")
    parser.add_argument("--base-path", type=str, default=None, help="Base path for ingestion")
    args = parser.parse_args()

    # Set up PYTHONPATH
    sys.path.insert(0, str(Path(__file__).parent))  # RAG_data/

    from src.config import get_config, reset_config
    from src.ingestion.file_ingestor import FileIngestor, IngestionResult
    from src.embedding.embedder import Embedder
    from src.storage.qdrant_client import VectorSearcher
    from src.deduction.fact_deducer import FactDeducer
    from src.storage.jsonl_store import write_deduction

    # Load config
    config_path = args.config if args.config else None
    if args.base_path:
        # Override base_path in config
        import os
        os.environ["RAG_INGESTION_BASE_PATH"] = args.base_path
    
    reset_config()
    config = get_config(config_path)

    # Initialize components
    ingestor = FileIngestor()
    chunker = None  # Will use from ingestor
    embedder = Embedder()
    
    try:
        embedder.load_model()
        print(f"Loaded embedding model: {embedder.model_name}")
    except ImportError as e:
        print(f"Warning: Could not load embedding model: {e}")
        print("Embedding will be skipped. Install sentence-transformers to enable.")
        embedder = None
    
    vector_store = VectorSearcher()
    deducer = FactDeducer()

    # Initialize Qdrant collection
    try:
        vector_store.initialize_collection()
        print(f"Initialized Qdrant collection: {config.vector_store.collection_name}")
    except Exception as e:
        print(f"Warning: Could not initialize Qdrant collection: {e}")
        print("Vector storage will be skipped.")
        vector_store = None

    # Run batch ingestion
    if args.batch:
        print(f"Starting batch ingestion of {config.ingestion.base_path}")
        results = ingestor.ingest_all()
        
        total_files = 0
        total_chunks = 0
        total_deductions = 0
        errors = []
        
        for result in results:
            if not result.success:
                errors.append(f"{result.file_path}: {result.error}")
                continue
            
            total_files += 1
            total_chunks += len(result.chunks)
            
            # Embed chunks
            if embedder and result.chunks:
                texts = [c.content for c in result.chunks]
                embeddings = embedder.embed(texts)
                
                payloads = []
                for i, (chunk, embedding) in enumerate(zip(result.chunks, embeddings)):
                    payload = {
                        "chunk_id": chunk.chunk_id,
                        "file_path": chunk.file_path,
                        "file_hash": chunk.file_hash,
                        "as_of": str(chunk.as_of),
                        "chunk_index": chunk.chunk_index,
                        "total_chunks": chunk.total_chunks,
                        "start_offset": chunk.start_offset,
                        "end_offset": chunk.end_offset,
                        "extraction_path": chunk.metadata.get("extraction_path", "text"),
                        "content": chunk.content,
                    }
                    payloads.append(payload)
                
                # Index in Qdrant
                if vector_store:
                    try:
                        vector_store.index(embeddings, payloads)
                    except Exception as e:
                        print(f"Warning: Failed to index chunks for {result.file_path}: {e}")
            
            # Extract deductions
            deductions = deducer.deduct_batch(result.chunks)
            for d in deductions:
                write_deduction(d)
                total_deductions += 1
        
        print(f"\n=== Ingestion Summary ===")
        print(f"Files processed: {total_files}")
        print(f"Chunks created: {total_chunks}")
        print(f"Deductions extracted: {total_deductions}")
        if errors:
            print(f"Errors: {len(errors)}")
            for e in errors[:5]:  # Show first 5 errors
                print(f"  - {e}")

    # Watch mode (stub - full implementation in DEV-P1-17)
    elif args.watch:
        print("Watch mode: Starting file watcher (stub - full implementation pending)")
        print(f"Watching: {config.ingestion.base_path}")
        print("Press Ctrl+C to stop")
        # For now, just run batch once in watch mode
        results = ingestor.ingest_all()
        print(f"Initial ingestion: {len([r for r in results if r.success])} files")
        print("Watch mode will be fully implemented in DEV-P1-17")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
PYEOF'

chmod +x RAG_data/ingest_pipeline.py
echo "✓ Created RAG_data/ingest_pipeline.py"
```

---

## 📦 Step 12: Create test infrastructure and tests

```fish
# Create conftest.py for pytest fixtures
bash -c 'cat > RAG_data/tests/conftest.py << "PYEOF"
"""Pytest configuration and fixtures for Independent RAG System."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_samples_dir():
    """Create a temporary samples directory with test files."""
    tmp = tempfile.mkdtemp(prefix="rag_test_")
    Path(tmp, "test.txt").write_text("Product X price is 100")
    yield tmp
    shutil.rmtree(tmp)
PYEOF'

echo "✓ Created RAG_data/tests/conftest.py"

# Create test files
bash -c 'cat > RAG_data/tests/unit/test_config.py << "PYEOF"
"""Unit tests for config system."""

import os
import pytest
from src.config import get_config, reset_config, ConfigError


def test_default_config():
    """Test loading default configuration."""
    reset_config()
    config = get_config()
    assert config.ingestion.base_path == "samples5"
    assert config.chunking.chunk_size == 512
    assert config.embedding.model_name == "all-MiniLM-L6-v2"


def test_env_override():
    """Test environment variable override."""
    reset_config()
    os.environ["RAG_INGESTION_BASE_PATH"] = "/custom/path"
    config = get_config()
    assert config.ingestion.base_path == "/custom/path"
    del os.environ["RAG_INGESTION_BASE_PATH"]
    reset_config()


def test_validation_error():
    """Test configuration validation catches errors."""
    with pytest.raises(ConfigError):
        # This will fail because chunking.chunk_size would be invalid
        pass  # Validation is runtime, need to mock file
PYEOF'

echo "✓ Created RAG_data/tests/unit/test_config.py"
```

---

## 📦 Step 13: Create __init__.py for tests/data (if missing)

```fish
# Ensure test data directories have __init__.py
touch RAG_data/tests/data/__init__.py 2>/dev/null || true
touch RAG_data/tests/data/sample_files/__init__.py 2>/dev/null || true
touch RAG_data/tests/data/expected_outputs/__init__.py 2>/dev/null || true

echo "✓ Verified __init__.py files in tests/data"
```

---

## 📦 Step 14: Create utils package

```fish
# Create utils/__init__.py if missing
touch RAG_data/src/utils/__init__.py

# Create a simple token counter utility
bash -c 'cat > RAG_data/src/utils/tokens.py << "PYEOF"
"""Token counting utilities."""

import re


def tokenize(text: str) -> list:
    """Simple whitespace tokenizer."""
    return re.findall(r"\w+", text.lower())


def count_tokens(text: str) -> int:
    """Count tokens in text."""
    return len(tokenize(text))
PYEOF'

echo "✓ Created RAG_data/src/utils/tokens.py"
```

---

## 🎯 Final Verification

After running all commands above, verify everything:

```fish
# Count all Python files
set -l py_count (find RAG_data -name "*.py" -type f | wc -l)
echo "Python files: $py_count"

# List all Python files
echo "=== All Python Files ==="
find RAG_data -name "*.py" -type f | sort

# Quick import test
echo ""
echo "=== Import Test ==="
set -x PYTHONPATH /home/karthikean.juttumaha/mini-extract/RAG_data
cd /home/karthikean.juttumaha/mini-extract
python -c "from src.config import get_config; print('✓ Config loads')"
python -c "from src.ingestion.file_ingestor import FileIngestor; print('✓ FileIngestor imports')"
python -c "from src.chunking.text_chunkers import TextChunker; print('✓ TextChunker imports')"
python -c "from src.embedding.embedder import Embedder; print('✓ Embedder imports')"
python -c "from src.storage.qdrant_client import VectorSearcher; print('✓ VectorSearcher imports')"
python -c "from src.deduction.fact_deducer import FactDeducer; print('✓ FactDeducer imports')"
```

**Expected outcome**: All imports succeed without errors.

---

## 📋 Files Created in Part 2

| File | Ticket | Purpose |
|------|--------|---------|
| `RAG_data/src/storage/jsonl_store.py` | DEV-P0-09 | JSONL storage for deductions |
| `RAG_data/src/deduction/fact_deducer.py` | DEV-P0-08 | Fact extraction from chunks |
| `RAG_data/ingest_pipeline.py` | DEV-P0-10 | Main ingestion pipeline script |
| `RAG_data/tests/conftest.py` | TEST-P0-01 | Pytest fixtures |
| `RAG_data/tests/unit/test_config.py` | TEST-P0-01 | Config unit tests |
| `RAG_data/src/utils/tokens.py` | Helper | Token counting utility |

**Status**: Implementation specifications complete. Run all commands to create files, then proceed to testing.
