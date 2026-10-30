# User Interface for Temporal-Valid KG RAG System

## Overview

This is the user interface for the Temporal-Valid Knowledge Graph RAG System.
It provides a web-based interface for querying documents with temporal awareness.

## Features

- **Fuzzy Query Support**: Natural language queries with semantic matching
- **Three Retrieval Modes**:
  - Pure RAG (vector search)
  - RAG + KG Validator (hybrid with validation)
  - KG-only (graph traversal)
- **Temporal Filtering**: Query as of a specific date
- **Current Data Only**: By default shows only current facts
- **Historical Access**: Option to include superseded facts
- **Real-time Updates**: Data is always current from the database
- **Confidence Scoring**: Shows confidence levels for results
- **Query History**: Tracks recent queries

## Installation

```bash
# Install UI dependencies
pip install streamlit python-multipart requests

# Or using uv
uv pip install streamlit python-multipart requests
```

## Running the UI

### Option 1: Direct Streamlit Run
```bash
cd /home/karthikean.juttumaha/mini-extract
uv run streamlit run USER_INTERFACE/app.py
```

### Option 2: Using Python
```bash
cd /home/karthikean.juttumaha/mini-extract
python USER_INTERFACE/app.py
```

## Accessing the UI

Once running, open your browser and go to:
```
http://localhost:8501
```

## UI Components

### Query Panel
1. **Question Input**: Enter natural language questions
2. **Retrieval Mode**: Select one of three modes
3. **Temporal Settings**:
   - As Of Date: Query historical state
   - Include History: Show superseded facts
4. **Advanced Settings**:
   - Number of Results
   - Show Confidence Scores

### Results Display
- **Latency**: Query execution time
- **Facts Found**: Count of retrieved facts
- **Fact Details**: Content, source, timestamp, confidence
- **Current Status**: Visual indicator (Current vs Superseded)
- **Citations**: Source references

### Query History
- Tracks recent queries
- Shows question, mode, and timestamp

## Query Examples

1. **Simple Query**: "Who is the CEO of Microsoft?"
2. **Temporal Query**: "What was the policy in 2023?"
3. **Fuzzy Query**: "Find all contracts with Acme"
4. **Multi-hop Query**: "Show relationships between entities X and Y"

## System Requirements

- Python 3.10+
- Neo4j database running
- Qdrant vector database running
- Core system modules accessible

## Architecture

The UI connects to the backend via:
- Direct Python imports for synchronous queries
- FastAPI endpoints (future enhancement)

## Troubleshooting

### "System modules not available"
- Ensure you're running from the project root
- Check that `src/` directory exists
- Verify all dependencies are installed

### Database Connection Errors
- Ensure Neo4j is running on configured port
- Check Qdrant is running on configured port
- Verify network connectivity

### Slow Queries
- Check database performance
- Reduce number of results (k parameter)
- Try different retrieval mode

## License

MIT License - See main project LICENSE file