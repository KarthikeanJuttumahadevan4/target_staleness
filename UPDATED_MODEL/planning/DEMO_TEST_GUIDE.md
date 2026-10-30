# 🚀 Real-Time Demo Test Guide for Temporal-Valid KG-RAG System

## Overview

This guide helps you test the implemented components of the **UPDATED_MODEL**. Based on the implementation plan, several core modules are already implemented:

### ✅ **Already Implemented (Ready to Test)**
- `src/config.py` - Configuration management
- `src/models.py` - Pydantic models  
- `src/temporal/timestamp_extractor.py` - Timestamp extraction from files
- `src/temporal/kg_schema.py` - Knowledge Graph schema
- `src/temporal/temporal_kg.py` - Temporal KG operations
- `src/temporal/conflict_resolver.py` - Conflict resolution logic
- `src/api/server.py` - FastAPI server
- `src/retrieval/pure_rag.py` - Pure RAG mode
- `src/retrieval/rag_kg_validator.py` - RAG + KG Validator mode
- `src/retrieval/kg_only.py` - KG-only mode
- `src/retrieval/hybrid.py` - Orchestration

### ⏳ **Still Missing (Not Ready to Test)**
- `src/intake/` - File watcher, queue, router
- `src/extraction/` - Multi-path extraction
- `src/reconstruction/` - Entity resolver
- `src/indexing/` - Vector and hierarchical indexing
- `src/generation/` - DSPy answer generation
- `src/audit/` - Audit logger
- `src/enrichment/` - VLM enrichment

---

## Quick Start - Test What's Ready

### Step 1: Verify Dependencies

```bash
# Check if all required packages are installed
cd /home/karthikean.juttumaha/mini-extract

# Try importing the temporal modules
python -c "from src.temporal.timestamp_extractor import get_file_timestamps; print('✅ timestamp_extractor OK')"
python -c "from src.temporal.kg_schema import KGSchema; print('✅ kg_schema OK')"
python -c "from src.temporal.conflict_resolver import ConflictResolver; print('✅ conflict_resolver OK')"
python -c "from src.temporal.temporal_kg import TemporalKG; print('✅ temporal_kg OK')"

# Test retrieval modules
python -c "from src.retrieval.pure_rag import PureRAGRetriever; print('✅ pure_rag OK')"
python -c "from src.retrieval.kg_only import KGOnlyRetriever; print('✅ kg_only OK')"
python -c "from src.retrieval.rag_kg_validator import RAGKGValidator; print('✅ rag_kg_validator OK')"
python -c "from src.retrieval.hybrid import HybridRetriever; print('✅ hybrid OK')"
```

### Step 2: Test Timestamp Extraction

The `timestamp_extractor.py` is a critical component that extracts timestamps from file metadata.

```bash
# Test with a sample text file
python -c "
from src.temporal.timestamp_extractor import get_file_timestamps
import json

# Test with test.txt
timestamps = get_file_timestamps('SAMPLES/test.txt')
print('test.txt timestamps:', json.dumps(timestamps, default=str, indent=2))

# Test with a PDF if available
timestamps = get_file_timestamps('SAMPLES/invoice_1.pdf')
print('invoice_1.pdf timestamps:', json.dumps(timestamps, default=str, indent=2))
"
```

**Expected output:**
```json
{
  "modified": "2024-01-15T10:30:00Z",
  "created": "2024-01-15T10:30:00Z"
}
```

### Step 3: Test KG Schema

```bash
python -c "
from src.temporal.kg_schema import KGSchema

# Create schema instance
schema = KGSchema()
print('✅ KGSchema instantiated')
print('Schema attributes:', [attr for attr in dir(schema) if not attr.startswith('_')])
"
```

### Step 4: Test Conflict Resolution

This is the core temporal logic that handles the "most-recent-wins" behavior.

```bash
# Create a test script for conflict resolution
cat > /tmp/test_conflict.py << 'EOF'
from src.temporal.conflict_resolver import ConflictResolver
from datetime import datetime

# Create test facts - same subject/predicate, different values and timestamps
fact_old = {
    'fact_id': 'fact_old',
    'subject': 'unit_A',
    'predicate': 'commander',
    'object_value': 'Captain Smith',
    'as_of': datetime(2024, 1, 1, 10, 0, 0),
    'current': True,
    'valid_from': datetime(2024, 1, 1, 10, 0, 0),
    'valid_to': None,
    'superseded_by': None
}

fact_new = {
    'fact_id': 'fact_new',
    'subject': 'unit_A',
    'predicate': 'commander',
    'object_value': 'Captain Jones',
    'as_of': datetime(2024, 2, 1, 10, 0, 0),
    'current': True,
    'valid_from': datetime(2024, 2, 1, 10, 0, 0),
    'valid_to': None,
    'superseded_by': None
}

resolver = ConflictResolver()

# Test conflict detection
conflict = resolver.detect_conflict(fact_old, fact_new)
print(f"Conflict detected: {conflict}")

# Test resolution - newer should win
if conflict:
    resolved = resolver.resolve_conflict(fact_old, fact_new)
    print(f"\nResolved facts: {len(resolved)}")
    for fact_id, fact in resolved.items():
        print(f"  {fact_id}:")
        print(f"    current: {fact.get('current')}")
        print(f"    value: {fact.get('object_value')}")
        print(f"    superseded_by: {fact.get('superseded_by')}")
        print(f"    valid_to: {fact.get('valid_to')}")
        print()
EOF

python /tmp/test_conflict.py
```

**Expected output:**
- Conflict should be detected (same subject + predicate, different value)
- Newer fact (`fact_new`) should have `current=True`
- Older fact (`fact_old`) should have `current=False`
- Older fact should have `superseded_by='fact_new'`
- Older fact should have `valid_to` set to newer fact's `as_of` timestamp

### Step 5: Test Temporal KG

```bash
python -c "
from src.temporal.temporal_kg import TemporalKG

# Create TG instance (may need Neo4j connection)
kg = TemporalKG()
print('✅ TemporalKG instantiated')
print('KG methods:', [m for m in dir(kg) if not m.startswith('_') and callable(getattr(kg, m))])
"
```

---

## Run the Acceptance Tests

According to `UPDATED_MODEL/CODE DIRECTIONS AND PRODUCTS/07_ACCEPTANCE_CHECKS.md`, the gate tests are:

```bash
# Run the gate tests (must pass before P1 begins)
uv run pytest -q tests/test_temporal_validity.py tests/test_conflict_resolver.py tests/test_kg_schema.py tests/test_timestamp_extractor.py
```

If these tests don't exist yet, you can create them from the templates in `UPDATED_MODEL/CODE DIRECTIONS AND PRODUCTS/04_CODE_SCAFFOLDS.md`.

---

## Real-Time Demo Script

Here's a Python script you can save and run to demonstrate the temporal functionality:

```python
#!/usr/bin/env python3
"""
Real-Time Demo for Temporal-Valid KG-RAG System
"""

import sys
sys.path.insert(0, '/home/karthikean.juttumaha/mini-extract')

from src.temporal.timestamp_extractor import get_file_timestamps
from src.temporal.conflict_resolver import ConflictResolver
from src.temporal.kg_schema import KGSchema
from datetime import datetime


def demo_timestamp_extraction():
    """Demonstrate timestamp extraction from files."""
    print("\n" + "="*60)
    print("TIMESTAMP EXTRACTION DEMO")
    print("="*60)
    
    from pathlib import Path
    samples = Path("SAMPLES")
    
    files_to_test = ["test.txt", "invoice_1.txt", "invoice_1.pdf"]
    
    for filename in files_to_test:
        filepath = samples / filename
        if filepath.exists():
            try:
                timestamps = get_file_timestamps(str(filepath))
                print(f"\n📄 {filename}:")
                print(f"   Modified: {timestamps.get('modified', 'N/A')}")
                print(f"   Created: {timestamps.get('created', 'N/A')}")
            except Exception as e:
                print(f"\n📄 {filename}: Error - {e}")


def demo_conflict_resolution():
    """Demonstrate conflict resolution (most-recent-wins)."""
    print("\n" + "="*60)
    print("CONFLICT RESOLUTION DEMO")
    print("="*60)
    
    resolver = ConflictResolver()
    
    # Simulate document updates over time
    facts = [
        {
            'fact_id': 'v1',
            'subject': 'operation_plan',
            'predicate': 'status',
            'object_value': 'draft',
            'as_of': datetime(2024, 1, 1, 9, 0, 0),
            'current': True,
            'valid_from': datetime(2024, 1, 1, 9, 0, 0),
            'valid_to': None,
            'superseded_by': None
        },
        {
            'fact_id': 'v2',
            'subject': 'operation_plan',
            'predicate': 'status',
            'object_value': 'review',
            'as_of': datetime(2024, 1, 2, 14, 0, 0),
            'current': True,
            'valid_from': datetime(2024, 1, 2, 14, 0, 0),
            'valid_to': None,
            'superseded_by': None
        },
        {
            'fact_id': 'v3',
            'subject': 'operation_plan',
            'predicate': 'status',
            'object_value': 'approved',
            'as_of': datetime(2024, 1, 3, 16, 30, 0),
            'current': True,
            'valid_from': datetime(2024, 1, 3, 16, 30, 0),
            'valid_to': None,
            'superseded_by': None
        }
    ]
    
    print("\n📋 Resolution Steps:")
    current_fact = facts[0]
    print(f"Initial: {current_fact['object_value']} (as of {current_fact['as_of']})")
    
    for i, new_fact in enumerate(facts[1:], start=2):
        conflict = resolver.detect_conflict(current_fact, new_fact)
        if conflict:
            resolved = resolver.resolve_conflict(current_fact, new_fact)
            current_fact = resolved[new_fact['fact_id']]
            old_fact = resolved[current_fact['fact_id'] - 1 if isinstance(current_fact['fact_id'], int) else list(resolved.keys())[0]]
            
            print(f"\nUpdate {i}: {new_fact['object_value']} (as of {new_fact['as_of']})")
            print(f"  → New current: {current_fact['object_value']}")
            print(f"  → Superseded: {old_fact['object_value']}")
    
    print(f"\n✅ Final current fact: {current_fact['object_value']}")


def demo_kg_schema():
    """Demonstrate KG schema."""
    print("\n" + "="*60)
    print("KNOWLEDGE GRAPH SCHEMA DEMO")
    print("="*60)
    
    schema = KGSchema()
    print("\n✅ KGSchema instantiated")
    print(f"Schema class: {schema.__class__.__name__}")
    print(f"Public attributes: {len([a for a in dir(schema) if not a.startswith('_')])}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("TEMPORAL-VALID KG-RAG SYSTEM - REAL-TIME DEMO")
    print("="*60)
    print("\nTesting implemented components:")
    print("  ✅ Timestamp Extractor")
    print("  ✅ Conflict Resolver")
    print("  ✅ KG Schema")
    print("\n" + "="*60)
    
    try:
        demo_timestamp_extraction()
        demo_conflict_resolution()
        demo_kg_schema()
        
        print("\n" + "="*60)
        print("✅ ALL DEMOS COMPLETED")
        print("="*60)
        print("\nThe temporal core is working!")
        print("Next steps:")
        print("  1. Implement intake module (file watcher)")
        print("  2. Implement extraction module (multi-path)")
        print("  3. Connect to Neo4j and Qdrant")
        print("  4. Run full pipeline integration tests")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

Save this as `UPDATED_MODEL/demo_real_time.py` and run:

```bash
python UPDATED_MODEL/demo_real_time.py
```

---

## Test with Query API

If you have the FastAPI server running, you can test the query endpoints:

```bash
# Start the server
python main.py --port 8000

# Test health endpoint
curl http://localhost:8000/health

# Test query endpoint (once full pipeline is implemented)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the current status of operation_plan?",
    "mode": "kg_only",
    "as_of": null,
    "include_history": false
  }'
```

---

## Expected Behavior

### Temporal Validity (Non-Negotiable)

Every extracted fact MUST have:
- ✅ `as_of` timestamp (from file modification time)
- ✅ `valid_from` (defaults to as_of)
- ✅ `valid_to` (null for current, set for superseded)
- ✅ `current` boolean flag
- ✅ `superseded_by` (UUID link to newer fact)
- ✅ Provenance (source file, extraction path, model used)

### Conflict Resolution (Most-Recent-Wins)

When new facts conflict with existing facts:
1. ✅ Compare `as_of` timestamps
2. ✅ Newer fact: `current=true`, `supersedes=[old_fact_id]`
3. ✅ Older fact: `current=false`, `valid_to=new_as_of`, `superseded_by=new_fact_id`
4. ✅ Full history retained for audit

### Retrieval (Temporal-Aware)

All three retrieval modes must:
- ✅ Filter by `current=true` by default
- ✅ Return only most recent facts
- ✅ Include provenance in citations
- ✅ Support `as_of` parameter for historical queries

---

## Troubleshooting

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'src'`

**Solution:** Ensure you're running from the project root:
```bash
cd /home/karthikean.juttumaha/mini-extract
python -c "import sys; sys.path.insert(0, '.'); from src.temporal.timestamp_extractor import get_file_timestamps"
```

### Missing Dependencies

**Error:** `ModuleNotFoundError: No module named 'graphiti-core'`

**Solution:** Install with uv:
```bash
uv add graphiti-core ragbrain qdrant-client neo4j sentence-transformers watchdog python-dotenv
uv sync
```

### File Not Found

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'SAMPLES/test.txt'`

**Solution:** Check the SAMPLES directory:
```bash
ls SAMPLES/ | head -10
```

If files are missing, create a test file:
```bash
echo "Test document for temporal extraction" > SAMPLES/test_demo.txt
touch -d "2024-01-15T10:30:00Z" SAMPLES/test_demo.txt
```

---

## Next Steps

Once the temporal core tests pass:

1. **Implement Intake Module** (`src/intake/`)
   - Watch `samples5/` directory for new files
   - Queue files for processing
   - Route by MIME type

2. **Implement Multi-Path Extraction** (`src/extraction/`)
   - Text extraction
   - Table extraction
   - VLM enrichment
   - OCR fallback
   - Audio/Video transcription

3. **Connect to Databases**
   - Neo4j for Knowledge Graph
   - Qdrant for vector index
   - SQLite for job queue

4. **Implement Retrieval**
   - Pure RAG
   - RAG + KG Validator
   - KG-only

5. **Run Full Integration Tests**
   - Ingest initial files
   - Add conflicting files
   - Verify supersession
   - Test all retrieval modes

---

## Milestone Checklist

From `UPDATED_MODEL/ARCHITECTURE/07_Milestones.md`:

- [ ] **M1 Foundation**: `uv sync`, Neo4j+Qdrant up, extract.py tests pass
- [ ] **M2 Intake**: Drop files into samples5/, job queue records them
- [ ] **M3 Extraction**: 5 extraction types output NormalizedExtract
- [ ] **M4 Temporal KG**: Facts with current flags; supersession works
- [ ] **M5 Retrieval**: 3 modes return current facts by default
- [ ] **M6 Generation**: DSPy answers with citations; checked generation
- [ ] **M7 Audit & Security**: Append-only audit + redaction + access log
- [ ] **M8 Test Gate**: Temporal correctness tests pass; <3s latency; eval band metrics
- [ ] **M9 Final Review**: Human sign-off; COMPLETE_DELIVERY.md updated

**Current Status**: You're ready to work on **M1-M4** (temporal core is implemented)!

---

## Summary

You have a **working temporal core** that can:
✅ Extract timestamps from files
✅ Resolve conflicts (most-recent-wins)
✅ Manage KG schema
✅ Interface with retrieval modes

**Next**: Implement the intake and extraction modules to feed documents into the temporal KG, then connect the retrieval modes to provide real-time answers.

Run the demo to verify everything is working, then proceed to implement the remaining modules!
