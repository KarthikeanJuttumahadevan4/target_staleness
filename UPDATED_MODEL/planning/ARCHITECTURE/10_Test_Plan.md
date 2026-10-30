# 10_Test_Plan — Tests

## Unit Tests
- `timestamp_extractor.get_as_of` (mtime path, audio MOD, fallback)
- `entity_resolver.merge` (fuzzy match cases)
- `conflict_resolver.supersede` (newer/older/equal)
- `intake.router` (MIME, extension, archive)
- `extraction` each path
- `retrieval.*` each mode (mocked KG)

## Temporal Correctness Tests (provided suite adapted)
- Most-recent-wins on conflicting ingest
- Supersession flags propagate to all 3 modes
- `as_of` historical query returns correct version
- System-time replay returns belief at date
- Audit trail complete

## Integration Tests (samples5)
- Ingest initial + add newer conflicting file → old fact superseded.
- All modes return newest; citations include timestamp+source.
- No crash on unsupported formats.

## Performance Tests
- 1000 facts query <3s (Qdrant + index).
- Ingest 100MB PDF <60s.
- Video key-frame extraction 10x speedup from scene-change.

## Eval Band (Evaluation Band)
- Precision/recall on extraction (samples5 golden labels).
- Temporal correctness ≥95%.
- CFI faithfulness ≥0.9.
- Hit@K ≥0.9; MRR ≥0.8.

## Acceptance
- All provided test_* files pass.
- `uv run pytest -q` green.
- `main.py` serves 3 modes.
- README updated to reflect new system.
