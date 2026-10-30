# Knowledge Graph Prototype – Tonight Plan

## Current capability
extract.py can ingest PDF/XLSX/TXT/Audio/Video, extract raw text, optionally call LLM and output one JSON per file with vendor/invoice_date/total.

## Steps to prototype

1. **Batch extract**
   - Copy `artifacts/batch_extract.py.md` code to `batch_extract.py`
   - Run `uv run python batch_extract.py`
   - Outputs `artifacts/extractions/*.json` + `index.json`

2. **Wrangle & temporal tag**
   - The batch script already adds file_mtime, file_ctime, extracted_at, stderr, exit_code
   - `build_graph.py` normalizes vendor, total, parses dates, adds recency buckets last_7d / last_30d / older, month key

3. **Grouping criteria**
   - Nodes: Invoice, Vendor, File, Month
   - Edges: Invoice -> Vendor, Invoice -> File, Invoice -> Month
   - Group by Vendor count, Month count, recency

4. **Build graph**
   - Copy `artifacts/build_graph.py.md` code to `build_graph.py`
   - `uv run python build_graph.py`
   - Outputs `artifacts/graph/graph.json`, `graph.html`, `summary.md`

5. **Review**
   - Open `artifacts/graph/graph.html` for visual prototype
   - Check `artifacts/graph/summary.md` for stats

Dependencies needed for graph step: `networkx`, `pyvis`. Add them to pyproject.toml if missing.

Temporal filtering tip: in batch_extract.py set recent_cutoff and filter files by `file_mtime`.
