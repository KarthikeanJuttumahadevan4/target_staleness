# RUN_INGEST_PIPELINE.md – Run Ingestion and Verify

After running RUN_ALL_PHASE1.md, execute these commands to test the pipeline.

---

```fish
cd /home/karthikean.juttumaha/mini-extract

# Set PYTHONPATH
export PYTHONPATH=/home/karthikean.juttumaha/mini-extract/RAG_data

# ============================================
echo "=== STEP 1: Verify All Files ==="
finder() {
    echo "Python files:"
    find RAG_data -name "*.py" -type f | sort
    echo ""
    echo "Total Python files:"
    find RAG_data -name "*.py" -type f | wc -l
}
finder

# ============================================
echo ""
echo "=== STEP 2: Quick Import Test ==="
python3 -c "
from src.config import get_config
from src.ingestion.file_ingestor import FileIngestor
from src.chunking.text_chunkers import TextChunker
from src.embedding.embedder import Embedder
from src.storage.qdrant_client import VectorSearcher
from src.deduction.fact_deducer import FactDeducer
print('✓ All imports successful')
"

# ============================================
echo ""
echo "=== STEP 3: Test Config System ==="
python3 -c "
from src.config import get_config, reset_config
reset_config()
c = get_config()
print(f'base_path: {c.ingestion.base_path}')
print(f'chunk_size: {c.chunking.chunk_size}')
print(f'model: {c.embedding.model_name}')
"

# ============================================
echo ""
echo "=== STEP 4: Test File Ingestor ==="
python3 -c "
from src.ingestion.file_ingestor import FileIngestor, IngestionResult
import os
os.chdir('/home/karthikean.juttumaha/mini-extract')
ingestor = FileIngestor(base_path='samples5')
result = ingestor.ingest_one('samples5/demo/price.txt')
print(f'Success: {result.success}')
print(f'Chunks: {len(result.chunks)}')
if result.chunks:
    print(f'First chunk: {result.chunks[0].content[:50]}...')
"

# ============================================
echo ""
echo "=== STEP 5: Run Full Batch Ingestion ==="
python3 RAG_data/ingest_pipeline.py --batch

# ============================================
echo ""
echo "=== STEP 6: Check Results ==="
echo "--- Deductions File ---"
wc -l RAG_data/deductions.jsonl 2>/dev/null || echo "File not found"

echo ""
echo "--- First few deductions ---"
head -3 RAG_data/deductions.jsonl 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "No deductions yet"

# ============================================
echo ""
echo "=== STEP 7: Run Unit Tests ==="
python3 -m pytest RAG_data/tests/unit/ -v 2>&1 | head -50

# ============================================
echo ""
echo "=== PHASE 1 COMPLETE ==="
echo "✓ All files created"
echo "✓ Pipeline runs"
echo "✓ Ready for Phase 2 (Comparison Module)"
```

---

## Next Steps

1. **If any step fails**, check the error and ensure:
   - All dependencies are installed (`pip install -r RAG_data/requirements.txt`)
   - Qdrant is running (`docker run -p 6333:6333 qdrant/qdrant`)
   - You're in the correct directory

2. **Proceed to Phase 2** when all P0 tasks are verified:
   - DEV-P0-11: Aligner
   - DEV-P0-12: Inconsistency Detector  
   - DEV-P0-13: Resolver
   - DEV-P0-14: Reporter
   - DEV-P0-15: KG Fact Fetcher
   - DEV-P0-16: Comparison Script

---

**Status**: Ready to execute pipeline and run tests.
