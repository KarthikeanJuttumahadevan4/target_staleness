# DEV-P0-01: Create RAG_data Directory Structure

**Ticket**: DEV-P0-01: Create RAG_data Directory Structure  
**Priority**: P0  
**Owner**: Developer  
**Status**: Ready for Implementation  
**Dependencies**: None

---

## 1. Purpose

This implementation specification provides the **exact commands** to create the complete directory structure for the Independent RAG System, as defined in Section 7 of `04_RAG_Architecture.md`. This is the **foundation** for all subsequent development tasks.

---

## 2. Prerequisites

- Working directory: `/home/karthikean.juttumaha/mini-extract/`
- RAG_data directory already exists (from previous stages)
- Fish or bash shell available

---

## 3. Implementation: Exact Commands

### 3.1 Verify Working Directory

```bash
# Confirm we are in the correct directory
pwd
# Expected output: /home/karthikean.juttumaha/mini-extract

# Verify RAG_data exists
ls -la RAG_data/
# Expected: Should see 01_RAG_Proposal.md, 02_..., 03_..., 04_..., 05_..., 06_...
```

### 3.2 Create All Directories (Single Command)

```bash
# Create the complete directory tree with one command
# This creates all directories and subdirectories in one go
mkdir -p \
  RAG_data/src \
  RAG_data/src/ingestion \
  RAG_data/src/chunking \
  RAG_data/src/embedding \
  RAG_data/src/retrieval \
  RAG_data/src/deduction \
  RAG_data/src/comparison \
  RAG_data/src/resolution \
  RAG_data/src/storage \
  RAG_data/src/utils \
  RAG_data/tests \
  RAG_data/tests/unit \
  RAG_data/tests/integration \
  RAG_data/tests/data/sample_files \
  RAG_data/tests/data/expected_outputs \
  RAG_data/schemas
```

### 3.3 Create `__init__.py` Files

```bash
# Create empty __init__.py files in all Python directories
# This makes them proper Python packages

# Root src
> RAG_data/src/__init__.py

# Ingestion
> RAG_data/src/ingestion/__init__.py

# Chunking
> RAG_data/src/chunking/__init__.py

# Embedding
> RAG_data/src/embedding/__init__.py

# Retrieval
> RAG_data/src/retrieval/__init__.py

# Deduction
> RAG_data/src/deduction/__init__.py

# Comparison
> RAG_data/src/comparison/__init__.py

# Resolution
> RAG_data/src/resolution/__init__.py

# Storage
> RAG_data/src/storage/__init__.py

# Utils
> RAG_data/src/utils/__init__.py

# Tests
> RAG_data/tests/__init__.py
> RAG_data/tests/unit/__init__.py
> RAG_data/tests/integration/__init__.py
```

### 3.4 Fish-Compatible Command (Recommended)

Since the working environment uses **fish shell**, use this command:

```fish
# Create all directories
mkdir -p RAG_data/src/ingestion \
          RAG_data/src/chunking \
          RAG_data/src/embedding \
          RAG_data/src/retrieval \
          RAG_data/src/deduction \
          RAG_data/src/comparison \
          RAG_data/src/resolution \
          RAG_data/src/storage \
          RAG_data/src/utils \
          RAG_data/tests/unit \
          RAG_data/tests/integration \
          RAG_data/tests/data/sample_files \
          RAG_data/tests/data/expected_outputs \
          RAG_data/schemas

# Create all __init__.py files using touch
set -l dirs \
  src \
  src/ingestion \
  src/chunking \
  src/embedding \
  src/retrieval \
  src/deduction \
  src/comparison \
  src/resolution \
  src/storage \
  src/utils \
  tests \
  tests/unit \
  tests/integration

for dir in $dirs
    touch RAG_data/$dir/__init__.py
end

# Verify all __init__.py files exist
echo "Created __init__.py files:"
find RAG_data -name "__init__.py" -type f
```

### 3.5 Alternative: Python Script to Create Structure

If preferring a Python script approach:

```python
# save as create_rag_structure.py and run: python create_rag_structure.py
import os
from pathlib import Path

base = Path("RAG_data")

# All directories to create
dirs = [
    "src",
    "src/ingestion",
    "src/chunking",
    "src/embedding",
    "src/retrieval",
    "src/deduction",
    "src/comparison",
    "src/resolution",
    "src/storage",
    "src/utils",
    "tests",
    "tests/unit",
    "tests/integration",
    "tests/data",
    "tests/data/sample_files",
    "tests/data/expected_outputs",
    "schemas",
]

# Create directories
for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)
    print(f"Created: {base / d}")

# Create __init__.py files
python_dirs = [
    "src",
    "src/ingestion",
    "src/chunking",
    "src/embedding",
    "src/retrieval",
    "src/deduction",
    "src/comparison",
    "src/resolution",
    "src/storage",
    "src/utils",
    "tests",
    "tests/unit",
    "tests/integration",
]

for d in python_dirs:
    init_file = base / d / "__init__.py"
    init_file.touch(exist_ok=True)
    print(f"Created: {init_file}")

print("Directory structure created successfully!")
```

Run it with:
```fish
set -x PYTHONPATH /home/karthikean.juttumaha/mini-extract
python create_rag_structure.py
```

---

## 4. Final Directory Layout Confirmation

After running the commands above, the final directory structure **must** match:

```
RAG_data/
├── 01_RAG_Proposal.md              # Existing
├── 02_RAG_Requirements_Analysis.md # Existing
├── 03_RAG_Specifications.md        # Existing
├── 04_RAG_Architecture.md          # Existing
├── 05_RAG_Task_Breakdown.md        # Existing
├── 06_RAG_Tickets.md               # Existing
│
├── schemas/                        # NEW
│   └── (empty initially)
│
├── src/                            # NEW
│   ├── __init__.py                 # NEW
│   ├── ingestion/                  # NEW
│   │   └── __init__.py             # NEW
│   ├── chunking/                   # NEW
│   │   └── __init__.py             # NEW
│   ├── embedding/                  # NEW
│   │   └── __init__.py             # NEW
│   ├── retrieval/                  # NEW
│   │   └── __init__.py             # NEW
│   ├── deduction/                  # NEW
│   │   └── __init__.py             # NEW
│   ├── comparison/                 # NEW
│   │   └── __init__.py             # NEW
│   ├── resolution/                 # NEW
│   │   └── __init__.py             # NEW
│   ├── storage/                    # NEW
│   │   └── __init__.py             # NEW
│   └── utils/                      # NEW
│       └── __init__.py             # NEW
│
└── tests/                          # NEW
    ├── __init__.py                 # NEW
    ├── conftest.py                 # Will be created later
    ├── unit/                       # NEW
    │   └── __init__.py             # NEW
    └── integration/                # NEW
        └── __init__.py             # NEW
        └── data/                   # NEW
            ├── sample_files/       # NEW
            └── expected_outputs/   # NEW
```

### 4.1 Verification Commands

```fish
# Verify all directories exist
echo "=== Directory Structure ==="
find RAG_data -type d | sort

# Verify all __init__.py files exist
echo ""
echo "=== __init__.py Files ==="
find RAG_data -name "__init__.py" -type f | sort

# Count directories and files
echo ""
echo "=== Counts ==="
echo "Directories: $(find RAG_data -type d | wc -l)"
echo "__init__.py files: $(find RAG_data -name "__init__.py" | wc -l)"
```

**Expected Output**:
- 20 directories (including RAG_data itself and all subdirs)
- 13 `__init__.py` files

---

## 5. Notes for Subsequent Tickets

### 5.1 For DEV-P0-02 (Config System)
- The `config.py` file will be created in `RAG_data/src/`
- The `config.yaml` file will be created in `RAG_data/` root
- No KG dependencies allowed - verify with: `grep -r "from temporal\|from ingestion\|from indexing" RAG_data/src/`

### 5.2 For DEV-P0-03 (File Ingestor)
- Will be created in `RAG_data/src/ingestion/file_ingestor.py`
- Uses `extract.py` from parent project (allowed - it's filesystem only, not KG)
- Integration path: `from src.temporal.timestamp_extractor import TimestampExtractor`

### 5.3 For All Python Modules
- MUST import from `RAG_data.src` or relative paths
- MUST NOT import from `src/temporal/`, `src/ingestion/`, or `src/indexing/` (KG dependencies)
- SHOULD use type hints from `typing` module

### 5.4 File Naming Convention
- All module files: `snake_case.py`
- All test files: `test_<module>.py`
- All config files: `*.yaml` or `*.json`

---

## 6. Validation Checklist

- [ ] Run fish command from Section 3.4
- [ ] Verify all directories exist using `find RAG_data -type d`
- [ ] Verify all `__init__.py` files exist using `find RAG_data -name "__init__.py"`
- [ ] Verify directory count: 20
- [ ] Verify `__init__.py` count: 13
- [ ] Verify no unexpected files were created

---

## 7. Next Step

After this ticket is **validated and approved**, proceed to:
**DEV-P0-02: Implement Configuration System** (depends on this directory structure)

---

**Status**: Implementation specification complete. Awaiting validation.
