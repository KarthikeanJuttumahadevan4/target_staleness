# 07_ACCEPTANCE_CHECKS — Per-Module Test Recipes

| Module | Test file | Check |
|--------|-----------|-------|
| config | tests/test_config.py | `Settings()` loads; missing required raises |
| temporal timestamp | tests/test_timestamp_extractor.py | mtime parse + fallback |
| temporal kg schema | (inline) | init_schema idempotent |
| temporal kg facts | tests/test_temporal_kg.py | upsert + get_current + as_of |
| conflict resolver | tests/test_conflict_resolver.py | newer supersedes; older stays |
| intake router | tests/test_router.py | extension → handler |
| intake queue | tests/test_queue.py | idempotent enqueue |
| extraction text | tests/test_extraction_text.py | samples5 README.pdf → text |
| extraction ocr | (part of pipeline) | <80 chars triggers OCR |
| vlm | (manual) | image → fact list |
| vector indexer | tests/test_vector.py | search current-only filter |
| retrieval (3 modes) | tests/test_retrieval_temporal.py | all return newest |
| generation | (manual) | citations present |
| audit | tests/test_audit.py | hash-chain verifies |
| api | smoke | `/health`, `/ready`, `/query` |
| pipeline integration | tests/test_incremental_integration.py | end-to-end ingest |

## Gate (must pass before P1 begins)
`uv run pytest -q tests/test_temporal_validity.py tests/test_conflict_resolver.py tests/test_kg_schema.py tests/test_timestamp_extractor.py`

## Eval band
- Temporal correctness ≥95%
- CFI ≥0.9, Hit@K ≥0.9, MRR ≥0.8
- Query latency <3s on 1k facts
