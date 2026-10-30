---
format: html
---

# 🚀 Quick Start: Test the Temporal KG-RAG Model

## What's Ready to Test

The **temporal core** of your UPDATED_MODEL is already implemented:
- ✅ Timestamp extraction from files
- ✅ Knowledge Graph schema
- ✅ Conflict resolution (most-recent-wins)
- ✅ Temporal KG operations
- ✅ All 3 retrieval modes (Pure RAG, RAG+KG, KG-only)

---

## 5-Minute Test

### 1. Check Imports
```bash
cd /home/karthikean.juttumaha/mini-extract
python -c "from src.temporal.timestamp_extractor import get_file_timestamps; print('✅ timestamp OK')"
python -c "from src.temporal.conflict_resolver import ConflictResolver; print('✅ conflict OK')"
python -c "from src.temporal.kg_schema import KGSchema; print('✅ schema OK')"
```

### 2. Run Timestamp Extraction
```bash
python -c "
from src.temporal.timestamp_extractor import get_file_timestamps
import json
result = get_file_timestamps('SAMPLES/test.txt')
print(json.dumps(result, default=str, indent=2))
"
```

### 3. Run Conflict Resolution Demo
```bash
python -c "
from src.temporal.conflict_resolver import ConflictResolver
from datetime import datetime

resolver = ConflictResolver()

fact_old = {'fact_id': 'v1', 'subject': 'doc', 'predicate': 'status', 
            'object_value': 'draft', 'as_of': datetime(2024,1,1), 'current': True,
            'valid_from': datetime(2024,1,1), 'valid_to': None, 'superseded_by': None}

fact_new = {'fact_id': 'v2', 'subject': 'doc', 'predicate': 'status',
            'object_value': 'published', 'as_of': datetime(2024,2,1), 'current': True,
            'valid_from': datetime(2024,2,1), 'valid_to': None, 'superseded_by': None}

print('Conflict detected:', resolver.detect_conflict(fact_old, fact_new))
resolved = resolver.resolve_conflict(fact_old, fact_new)
print('Newer fact current:', resolved['v2']['current'])
print('Older fact superseded:', resolved['v1']['current'] == False)
"
```

---

## One-Command Demo

Run all tests automatically:

```bash
# Save and run this script
cat > /tmp/quick_test.sh << 'EOF'
#!/bin/bash
cd /home/karthikean.juttumaha/mini-extract

echo "=== Testing Imports ==="
python -c "from src.temporal.timestamp_extractor import get_file_timestamps" && echo "✅ timestamp_extractor" || echo "❌ timestamp_extractor"
python -c "from src.temporal.conflict_resolver import ConflictResolver" && echo "✅ conflict_resolver" || echo "❌ conflict_resolver"
python -c "from src.temporal.kg_schema import KGSchema" && echo "✅ kg_schema" || echo "❌ kg_schema"
python -c "from src.temporal.temporal_kg import TemporalKG" && echo "✅ temporal_kg" || echo "❌ temporal_kg"

echo ""
echo "=== Testing Retrieval Modules ==="
python -c "from src.retrieval.pure_rag import PureRAGRetriever" && echo "✅ pure_rag" || echo "❌ pure_rag"
python -c "from src.retrieval.kg_only import KGOnlyRetriever" && echo "✅ kg_only" || echo "❌ kg_only"
python -c "from src.retrieval.rag_kg_validator import RAGKGValidator" && echo "✅ rag_kg_validator" || echo "❌ rag_kg_validator"
python -c "from src.retrieval.hybrid import HybridRetriever" && echo "✅ hybrid" || echo "❌ hybrid"

echo ""
echo "=== All Core Modules Loaded ==="
EOF

chmod +x /tmp/quick_test.sh
/tmp/quick_test.sh
```

---

## What to Expect

### ✅ Success
All imports work, and you can:
- Extract timestamps from files
- Resolve conflicts (newer facts win)
- Initialize KG schema
- Load retrieval modules

### ⚠️ Missing Dependencies
If you see `ModuleNotFoundError`:
```bash
uv add graphiti-core ragbrain qdrant-client neo4j sentence-transformers watchdog python-dotenv
uv sync
```

### ❌ Failed Imports
If modules are missing, they haven't been implemented yet. Check:
```bash
ls -la src/temporal/
ls -la src/retrieval/
```

---

## Next Steps

Once all imports work:

1. **Run the full demo**:
   ```bash
   python UPDATED_MODEL/demo_real_time.py
   ```

2. **Run acceptance tests**:
   ```bash
   uv run pytest -q tests/test_temporal_validity.py tests/test_conflict_resolver.py tests/test_kg_schema.py tests/test_timestamp_extractor.py
   ```

3. **Start the server**:
   ```bash
   python main.py --port 8000
   ```

---

## Need Help?

Check these files:
- **Full demo guide**: `UPDATED_MODEL/DEMO_TEST_GUIDE.md`
- **Implementation plan**: `UPDATED_MODEL/ARCHITECTURE/05_IMPLEMENTATION_ORDER.md`
- **Acceptance tests**: `UPDATED_MODEL/CODE DIRECTIONS AND PRODUCTS/07_ACCEPTANCE_CHECKS.md`
- **Technical design**: `UPDATED_MODEL/ARCHITECTURE/01_Technical_Design.md`

---

## Status Summary

| Component | Status | Test Command |
|-----------|--------|--------------|
| Config | ✅ | `python -c "from src.config import Settings"` |
| Timestamp Extractor | ✅ | `python -c "from src.temporal.timestamp_extractor import get_file_timestamps"` |
| KG Schema | ✅ | `python -c "from src.temporal.kg_schema import KGSchema"` |
| Temporal KG | ✅ | `python -c "from src.temporal.temporal_kg import TemporalKG"` |
| Conflict Resolver | ✅ | `python -c "from src.temporal.conflict_resolver import ConflictResolver"` |
| Pure RAG | ✅ | `python -c "from src.retrieval.pure_rag import PureRAGRetriever"` |
| RAG+KG Validator | ✅ | `python -c "from src.retrieval.rag_kg_validator import RAGKGValidator"` |
| KG-only | ✅ | `python -c "from src.retrieval.kg_only import KGOnlyRetriever"` |
| Hybrid | ✅ | `python -c "from src.retrieval.hybrid import HybridRetriever"` |
| Intake | ❌ Not implemented |
| Extraction | ❌ Not implemented |
| Indexing | ❌ Not implemented |
| Generation | ❌ Not implemented |

**You're ready to test the temporal core!** 🎉
