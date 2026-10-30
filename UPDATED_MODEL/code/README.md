# Code Directory

This directory contains all code files for the Temporal-Valid KG RAG System.

## Main Entry Point

The main entry point for the system is:
```
IMPLEMENTATION/main.py
```

This script starts the FastAPI server for the temporal-valid knowledge graph RAG system.

## Subdirectories

- **CONFIG/** - Project configuration files (pyproject.toml, requirements.txt, uv.lock)
- **IMPLEMENTATION/** - Main application code including:
  - `main.py` - FastAPI server entry point
  - `src/` - Source code modules
  - `lib/` - Library dependencies
  - `USER_INTERFACE/` - Streamlit UI (app.py)
- **DOCUMENTATION/** - Documentation artifacts (no .md files here - moved to planning/)
- **SAMPLES/** - Sample data and documentation
- **TESTS/** - Test files

## Running the System

```bash
# Start the FastAPI server
cd IMPLEMENTATION && python main.py --port 8000

# Or run with watch mode for document ingestion
python main.py --port 8000 --watch-dir ./samples5
```
