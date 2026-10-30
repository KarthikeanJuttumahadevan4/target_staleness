# Test Data Report - Mock Extractions for extract.py & Knowledge Graph Prototype

## Overview
Created mock extraction JSON files to validate `extract.py` and the knowledge graph prototype (`build_graph.py`). Files simulate batch_extract output with fields expected by both components.

**Location:** `/home/karthikean.juttumaha/mini-extract/artifacts/tests/extractions/`

## Test Files Created

| File | Type | Vendor | Invoice Date | Total | file_mtime | Recency | Notes |
|------|------|--------|--------------|-------|------------|---------|-------|
| invoice_1.pdf.json | pdf | Acme Corp | 2026-09-28 | 1250.75 | 2026-09-29 | last_7d | pdfplumber |
| invoice_3.txt.json | txt | Beta Supplies | 2026-09-19 | 899.00 | 2026-09-20 | last_30d | text |
| data_1.xlsx.json | excel | Gamma Industries | 2026-08-10 | 4520.50 | 2026-08-15 | older | openpyxl |
| audio_1.wav.json | audio | Delta Services | 2026-09-29 | 320.00 | 2026-09-30 | last_7d | audio_transcription_not_available |
| video_1.avi.json | video | Epsilon Ltd | 2025-11-28 | 7800.25 | 2025-12-01 | older | ffmpeg_not_installed |
| invoice_5.pdf.json | pdf | null | null | null | 2026-09-25 | last_30d | no LLM key simulation |

All files contain fields: file_path, file_name, suffix, file_size, file_mtime, file_ctime, vendor, invoice_date, total, notes, extracted_at, ingest_path, source, stderr, exit_code.

## Expected Knowledge Graph

Generated via `build_graph_from_mocks.py` -> `artifacts/graph_test/graph.json`

### Nodes
- **Invoice nodes:** 6 (`invoice:file_name`)
- **Vendor nodes:** 6 (Acme Corp, Beta Supplies, Gamma Industries, Delta Services, Epsilon Ltd, Unknown Vendor)
- **File nodes:** 6
- **Month nodes:** 3 (2026-09, 2026-08, 2025-11)

Total nodes: 21

### Edges
- `invoice -> vendor` (from_vendor): 6
- `invoice -> file` (stored_in): 6
- `invoice -> month` (in_month): 5 (invoice_5.pdf has null dates, uses file_mtime -> 2026-09)

Total edges: 18

### Stats
Vendors:
- Acme Corp: 1
- Beta Supplies: 1
- Delta Services: 1
- Epsilon Ltd: 1
- Gamma Industries: 1
- Unknown Vendor: 1

Months:
- 2026-09: 4
- 2026-08: 1
- 2025-11: 1

Recency tagging:
- last_7d: invoice_1.pdf, audio_1.wav
- last_30d: invoice_3.txt, invoice_5.pdf
- older: data_1.xlsx, video_1.avi

## Usage

Generate graph from mocks:
```bash
/home/karthikean.juttumaha/mini-extract/.venv/bin/python3 artifacts/tests/build_graph_from_mocks.py
```

Output: `artifacts/graph_test/graph.json` and summary printed to console.

To use with real prototype, point `EXTRACTIONS_DIR` to `artifacts/tests/extractions` or copy files to `artifacts/extractions/` and run `build_graph.py`.

## Validation Points
- Null vendor/invoice_date/total handled → Unknown Vendor node created
- Different ingest_path values preserved
- File metadata preserved for recency calculation
- Audio/video stubs correctly represented in notes/ingest_path
- Month aggregation works with invoice_date fallback to file_mtime
