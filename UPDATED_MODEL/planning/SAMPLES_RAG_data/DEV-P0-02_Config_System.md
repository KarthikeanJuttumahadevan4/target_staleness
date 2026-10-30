# DEV-P0-02: Implement Configuration System

**Ticket**: DEV-P0-02: Implement Configuration System  
**Priority**: P0  
**Owner**: Developer  
**Status**: Ready for Implementation  
**Dependencies**: DEV-P0-01 (Directory Structure)

---

## 1. Purpose

Implement a **flexible configuration system** that loads settings from:
1. `RAG_data/config.yaml` (primary)
2. Environment variables (override)
3. Command-line arguments (override, via future DEV-P0-20)

This system provides a **single source of truth** for all runtime parameters and ensures the Independent RAG System remains configurable without code changes.

---

## 2. Implementation Files

| File | Location | Purpose |
|------|----------|---------|
| `config.py` | `RAG_data/src/config.py` | Main configuration loader and validator |
| `config.yaml` | `RAG_data/config.yaml` | Default configuration values |

---

## 3. File: `RAG_data/src/config.py`

```python
"""
Configuration management for the Independent RAG System.

This module provides a centralized configuration system that loads settings
from config.yaml, with overrides from environment variables.

Usage:
    from src.config import get_config, Config
    
    config = get_config()
    print(config.ingestion.base_path)  # e.g., "samples5"

Environment Variables:
    All config keys can be overridden via environment variables with the
    prefix RAG_. For example:
    - RAG_INGESTION_BASE_PATH=/path/to/files
    - RAG_EMBEDDING_MODEL_NAME=bge-small-en-v1.5
"""

import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class IngestionConfig:
    """File ingestion configuration."""
    base_path: str = "samples5"
    watch_mode: bool = False
    allowed_extensions: List[str] = field(default_factory=lambda: [
        ".txt", ".pdf", ".docx", ".xlsx", ".pptx"
    ])
    batch_size: int = 100


@dataclass
class ChunkingConfig:
    """Text chunking configuration."""
    chunk_size: int = 512
    overlap: int = 102
    min_chunk_size: int = 50


@dataclass
class EmbeddingConfig:
    """Embedding model configuration."""
    model_name: str = "all-MiniLM-L6-v2"
    fallback_model: str = "BAAI/bge-small-en-v1.5"
    batch_size: int = 32
    normalize: bool = True


@dataclass
class VectorStoreConfig:
    """Vector store (Qdrant) configuration."""
    host: str = "localhost"
    port: int = 6333
    collection_name: str = "rag_deductions"
    vector_size: int = 384
    distance: str = "Cosine"


@dataclass
class DeductionConfig:
    """Fact deduction configuration."""
    confidence_threshold: float = 0.7
    predicate_map: Dict[str, str] = field(default_factory=lambda: {
        "price": "has_price",
        "cost": "has_price",
        "amount": "has_price",
        "headcount": "has_headcount",
        "employees": "has_headcount",
        "budget": "has_budget",
        "date": "has_date",
        "as of": "has_date",
        "effective": "has_date",
    })


@dataclass
class ComparisonConfig:
    """RAG vs KG comparison configuration."""
    similarity_threshold: float = 0.85
    confidence_threshold: float = 0.9


@dataclass
class ResolutionConfig:
    """Inconsistency resolution configuration."""
    rules: List[str] = field(default_factory=lambda: [
        "R1", "R2", "R3", "R4", "R5", "R6", "R7"
    ])


@dataclass
class DirectoryConfig:
    """Directory paths configuration."""
    output: str = "RAG_data/output"
    logs: str = "RAG_data/logs"
    deductions_file: str = "RAG_data/deductions.jsonl"
    resolution_log: str = "RAG_data/resolution_log.jsonl"


@dataclass
class PerformanceConfig:
    """Performance configuration."""
    max_file_size_mb: int = 100
    max_concurrent_files: int = 10
    query_timeout_ms: int = 500


@dataclass
class Config:
    """
    Master configuration container.
    
    All configuration is loaded from config.yaml with environment
    variable overrides. Environment variables use the RAG_ prefix
    and follow the nested key structure with underscores.
    
    Example:
        ingestion.base_path -> RAG_INGESTION_BASE_PATH
        embedding.model_name -> RAG_EMBEDDING_MODEL_NAME
    """
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
        """Convert config to dictionary."""
        return {
            "ingestion": self.ingestion.__dict__,
            "chunking": self.chunking.__dict__,
            "embedding": self.embedding.__dict__,
            "vector_store": self.vector_store.__dict__,
            "deduction": self.deduction.__dict__,
            "comparison": self.comparison.__dict__,
            "resolution": self.resolution.__dict__,
            "directories": self.directories.__dict__,
            "performance": self.performance.__dict__,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Config":
        """Create Config from dictionary."""
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


# =============================================================================
# Configuration Loader
# =============================================================================

class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


def _parse_env_value(value: str, default: Any) -> Any:
    """
    Parse an environment variable value to the appropriate type.
    
    Args:
        value: String value from environment variable
        default: Default value to infer type from
        
    Returns:
        Parsed value of the same type as default
    """
    if isinstance(default, bool):
        return value.lower() in ("true", "1", "yes", "on")
    elif isinstance(default, int):
        return int(value)
    elif isinstance(default, float):
        return float(value)
    elif isinstance(default, list):
        # Handle comma-separated or JSON list
        if value.startswith("["):
            import json
            return json.loads(value)
        return [v.strip() for v in value.split(",") if v.strip()]
    elif isinstance(default, dict):
        import json
        if value.startswith("{"):
            return json.loads(value)
        # Simple key:value,key:value format
        result = {}
        for pair in value.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                result[k.strip()] = v.strip()
        return result
    else:
        return value


def _get_env_overrides() -> Dict[str, Any]:
    """
    Get all configuration overrides from environment variables.
    
    Environment variables should be prefixed with RAG_ and use underscores
    to represent nested keys.
    
    Examples:
        RAG_INGESTION_BASE_PATH=/custom/path
        RAG_CHUNKING_CHUNK_SIZE=256
        RAG_DEDUCTION_CONFIDENCE_THRESHOLD=0.8
    """
    overrides = {}
    for key, value in os.environ.items():
        if not key.startswith("RAG_"):
            continue
        # Remove RAG_ prefix and convert to lowercase
        config_key = key[4:].lower()
        # Replace underscores with dots for nested access
        config_key = config_key.replace("__", ".")  # Double underscore for literal underscore
        config_key = config_key.replace("_", ".")
        overrides[config_key] = value
    return overrides


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries, with override taking precedence.
    
    Args:
        base: Base dictionary
        override: Override dictionary (values take precedence)
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _apply_overrides(config_dict: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply environment variable overrides to a configuration dictionary.
    
    Handles nested keys specified with dot notation.
    Example: "ingestion.base_path" -> config["ingestion"]["base_path"]
    """
    result = config_dict.copy()
    for key, value in overrides.items():
        parts = key.split(".")
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
            if not isinstance(current, dict):
                raise ConfigError(f"Cannot override {key}: {parts[:-1]} is not a dict")
        # Get the default value to infer type
        final_key = parts[-1]
        default_val = current.get(final_key, value)
        current[final_key] = _parse_env_value(value, default_val)
    return result


def _validate_config(config_dict: Dict[str, Any]) -> None:
    """
    Validate configuration values.
    
    Args:
        config_dict: Configuration dictionary to validate
        
    Raises:
        ConfigError: If any validation fails
    """
    errors = []
    
    # Validate ingestion
    ingestion = config_dict.get("ingestion", {})
    if ingestion.get("batch_size", 0) <= 0:
        errors.append("ingestion.batch_size must be > 0")
    
    # Validate chunking
    chunking = config_dict.get("chunking", {})
    chunk_size = chunking.get("chunk_size", 0)
    overlap = chunking.get("overlap", 0)
    min_chunk = chunking.get("min_chunk_size", 0)
    
    if chunk_size <= 0:
        errors.append("chunking.chunk_size must be > 0")
    if overlap < 0:
        errors.append("chunking.overlap must be >= 0")
    if min_chunk <= 0:
        errors.append("chunking.min_chunk_size must be > 0")
    if overlap >= chunk_size:
        errors.append("chunking.overlap must be < chunking.chunk_size")
    
    # Validate embedding
    embedding = config_dict.get("embedding", {})
    if embedding.get("batch_size", 0) <= 0:
        errors.append("embedding.batch_size must be > 0")
    
    # Validate vector_store
    vs = config_dict.get("vector_store", {})
    if vs.get("port", 0) <= 0 or vs.get("port", 0) > 65535:
        errors.append("vector_store.port must be between 1 and 65535")
    if vs.get("vector_size", 0) <= 0:
        errors.append("vector_store.vector_size must be > 0")
    if vs.get("distance", "").upper() not in ("COSINE", "DOT", "EUCLIDEAN"):
        errors.append("vector_store.distance must be COSINE, DOT, or EUCLIDEAN")
    
    # Validate deduction
    deduction = config_dict.get("deduction", {})
    conf = deduction.get("confidence_threshold", 0)
    if not (0.0 <= conf <= 1.0):
        errors.append("deduction.confidence_threshold must be between 0.0 and 1.0")
    
    # Validate comparison
    comparison = config_dict.get("comparison", {})
    sim = comparison.get("similarity_threshold", 0)
    if not (0.0 <= sim <= 1.0):
        errors.append("comparison.similarity_threshold must be between 0.0 and 1.0")
    conf_cmp = comparison.get("confidence_threshold", 0)
    if not (0.0 <= conf_cmp <= 1.0):
        errors.append("comparison.confidence_threshold must be between 0.0 and 1.0")
    
    # Validate performance
    perf = config_dict.get("performance", {})
    if perf.get("max_file_size_mb", 0) <= 0:
        errors.append("performance.max_file_size_mb must be > 0")
    if perf.get("max_concurrent_files", 0) <= 0:
        errors.append("performance.max_concurrent_files must be > 0")
    if perf.get("query_timeout_ms", 0) <= 0:
        errors.append("performance.query_timeout_ms must be > 0")
    
    if errors:
        raise ConfigError("Config validation failed: " + "; ".join(errors))


# Global config cache
_config_cache: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Load and return the configuration.
    
    Configuration is loaded once and cached. Subsequent calls return
    the cached configuration.
    
    Args:
        config_path: Optional path to config.yaml. If None, uses
                     RAG_data/config.yaml relative to cwd.
    
    Returns:
        Loaded Config object
        
    Raises:
        ConfigError: If configuration is invalid
        FileNotFoundError: If config file is missing
    """
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    # Determine config path
    if config_path is None:
        config_path = os.path.join(os.getcwd(), "RAG_data", "config.yaml")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}. "
            f"Please ensure RAG_data/config.yaml exists."
        )
    
    # Load YAML
    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f) or {}
    
    # Get environment overrides
    env_overrides = _get_env_overrides()
    
    # Apply overrides
    config_dict = _apply_overrides(config_dict, env_overrides)
    
    # Validate
    _validate_config(config_dict)
    
    # Convert to Config object
    _config_cache = Config.from_dict(config_dict)
    
    return _config_cache


def reload_config() -> Config:
    """
    Reload the configuration, clearing the cache.
    
    Useful for testing or when config changes during runtime.
    
    Returns:
        Fresh Config object
    """
    global _config_cache
    _config_cache = None
    return get_config()


def reset_config() -> None:
    """
    Reset the configuration cache.
    
    The next call to get_config() will reload from scratch.
    """
    global _config_cache
    _config_cache = None
```

---

## 4. File: `RAG_data/config.yaml`

```yaml
# =============================================================================
# Independent RAG System Configuration
# =============================================================================
# This file contains default configuration values.
# All values can be overridden via environment variables using the RAG_ prefix.
# Example: RAG_INGESTION_BASE_PATH=/custom/path
# =============================================================================

# -----------------------------------------------------------------------------
# File Ingestion Configuration
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# Text Chunking Configuration
# -----------------------------------------------------------------------------
chunking:
  chunk_size: 512        # Maximum tokens per chunk
  overlap: 102           # Overlapping tokens (20% of chunk_size)
  min_chunk_size: 50     # Minimum tokens per chunk

# -----------------------------------------------------------------------------
# Embedding Configuration
# -----------------------------------------------------------------------------
embedding:
  model_name: "all-MiniLM-L6-v2"      # Primary embedding model
  fallback_model: "BAAI/bge-small-en-v1.5"  # Fallback if primary unavailable
  batch_size: 32                    # Number of texts per batch
  normalize: true                   # L2-normalize embeddings

# -----------------------------------------------------------------------------
# Vector Store (Qdrant) Configuration
# -----------------------------------------------------------------------------
vector_store:
  host: "localhost"
  port: 6333
  collection_name: "rag_deductions"
  vector_size: 384
  distance: "Cosine"

# -----------------------------------------------------------------------------
# Fact Deduction Configuration
# -----------------------------------------------------------------------------
deduction:
  confidence_threshold: 0.7      # Minimum confidence for a valid deduction
  predicate_map:                  # Mapping of keywords to predicates
    price: "has_price"
    cost: "has_price"
    amount: "has_price"
    headcount: "has_headcount"
    employees: "has_headcount"
    budget: "has_budget"
    date: "has_date"
    as of: "has_date"
    effective: "has_date"

# -----------------------------------------------------------------------------
# RAG vs KG Comparison Configuration
# -----------------------------------------------------------------------------
comparison:
  similarity_threshold: 0.85     # Minimum similarity for semantic matching
  confidence_threshold: 0.9      # Minimum confidence for fuzzy matching

# -----------------------------------------------------------------------------
# Inconsistency Resolution Configuration
# -----------------------------------------------------------------------------
resolution:
  rules:                          # Rule IDs to apply (in priority order)
    - "R1"
    - "R2"
    - "R3"
    - "R4"
    - "R5"
    - "R6"
    - "R7"

# -----------------------------------------------------------------------------
# Directory Configuration
# -----------------------------------------------------------------------------
directories:
  output: "RAG_data/output"
  logs: "RAG_data/logs"
  deductions_file: "RAG_data/deductions.jsonl"
  resolution_log: "RAG_data/resolution_log.jsonl"

# -----------------------------------------------------------------------------
# Performance Configuration
# -----------------------------------------------------------------------------
performance:
  max_file_size_mb: 100
  max_concurrent_files: 10
  query_timeout_ms: 500
```

---

## 5. File: `RAG_data/requirements.txt` (Optional dependency file)

```text
# Core Dependencies
PyYAML>=6.0

# Sentence Transformers (embedding models)
# Note: These are large packages. Install only if models are not already available.
# sentence-transformers>=2.2.2
# torch>=2.0.0

# Qdrant Client
# qdrant-client>=1.8.0

# File Parsing
# pdfplumber>=0.10.0
# python-docx>=1.1.0
# openpyxl>=3.1.0
# python-pptx>=0.6.21
# pytesseract>=0.3.10
# pdf2image>=1.16.0
# pillow>=9.0.0

# For file watching (incremental mode)
# watchdog>=4.0.0
```

---

## 6. Verification Commands

### 6.1 Verify Files Exist

```fish
# Check config.py exists
ls -la RAG_data/src/config.py

# Check config.yaml exists
ls -la RAG_data/config.yaml

# Check requirements.txt exists (optional)
ls -la RAG_data/requirements.txt 2>/dev/null && echo "requirements.txt exists" || echo "requirements.txt not created (optional)"
```

### 6.2 Test Config Loading

```fish
# Test basic import and config loading
set -x PYTHONPATH /home/karthikean.juttumaha/mini-extract/RAG_data
python -c "from src.config import get_config; print('Config loaded successfully')"
```

### 6.3 Test Environment Variable Override

```fish
# Test env var override
set -x RAG_INGESTION_BASE_PATH /custom/path
set -x RAG_CHUNKING_CHUNK_SIZE 256
python -c "from src.config import get_config, reload_config; c = reload_config(); print(f'base_path={c.ingestion.base_path}, chunk_size={c.chunking.chunk_size}')"
unset RAG_INGESTION_BASE_PATH
unset RAG_CHUNKING_CHUNK_SIZE
```

### 6.4 Test Validation

```fish
# Test invalid config values are caught
python -c "
from src.config import ConfigError, get_config, reset_config
reset_config()
try:
    import yaml
    bad_config = {'chunking': {'chunk_size': -10}}
    with open('RAG_data/config.yaml', 'w') as f:
        yaml.dump(bad_config, f)
    get_config()
except ConfigError as e:
    print(f'Validation caught error: {e}')
"
```

---

## 7. Expected Outputs

### 7.1 File Creation

```
RAG_data/
├── config.yaml              # NEW - Default configuration
├── requirements.txt         # NEW - Dependencies (optional)
└── src/
    └── config.py            # NEW - Configuration loader
```

### 7.2 Config Object Access

```python
>>> from src.config import get_config
>>> c = get_config()
>>> c.ingestion.base_path
'samples5'
>>> c.chunking.chunk_size
512
>>> c.embedding.model_name
'all-MiniLM-L6-v2'
>>> c.vector_store.host
'localhost'
>>> c.deduction.confidence_threshold
0.7
```

---

## 8. Notes for Subsequent Tickets

### 8.1 For DEV-P0-03 (File Ingestor)
- Import config: `from src.config import get_config`
- Get config: `config = get_config()`
- Access settings: `config.ingestion.base_path`, `config.ingestion.allowed_extensions`
- **DO NOT** hardcode values - always use config

### 8.2 For DEV-P0-04 through DEV-P0-09
- All components should accept config as parameter or load it internally
- Example pattern for a module:
  ```python
  from src.config import get_config
  
  class SomeComponent:
      def __init__(self):
          self.config = get_config()
          self.chunk_size = self.config.chunking.chunk_size
  ```

### 8.3 For All Components
- **NO KG DEPENDENCIES**: Do not import from `src/temporal/`, `src/ingestion/`, or `src/indexing/`
- Use only the config system for shared settings
- Validate config values at initialization time

### 8.4 Configuration Precedence
The system respects this precedence order (highest to lowest):
1. Command-line arguments (future: DEV-P0-20)
2. Environment variables (`RAG_*`)
3. `config.yaml` file
4. Default values in dataclasses

---

## 9. Validation Checklist

- [ ] `RAG_data/src/config.py` exists with all code from Section 3
- [ ] `RAG_data/config.yaml` exists with all settings from Section 4
- [ ] `RAG_data/requirements.txt` exists (optional but recommended)
- [ ] Config loads without errors: `python -c "from src.config import get_config; get_config()"`
- [ ] Environment variable override works: `RAG_INGESTION_BASE_PATH=/test python -c "from src.config import get_config, reload_config; reload_config().ingestion.base_path"`
- [ ] Validation catches invalid values
- [ ] No KG dependencies introduced

---

## 10. Next Step

After this ticket is **validated and approved**, proceed to:
**DEV-P0-03: Implement File Ingestor** (depends on config system)

---

**Status**: Implementation specification complete. Awaiting validation.
