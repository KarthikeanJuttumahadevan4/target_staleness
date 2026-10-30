#!/bin/bash
# Startup script for Temporal-Valid KG RAG System UI
# This script starts both the backend and the UI

echo "🚀 Starting Temporal-Valid KG RAG System UI..."
echo ""

# Check if we're in the right directory
if [ ! -d "src" ]; then
    echo "❌ Error: Please run from project root directory"
    exit 1
fi

# Install UI dependencies if needed
echo "📦 Checking dependencies..."
uv pip install streamlit python-multipart requests 2>/dev/null

echo ""
echo "🌐 Starting UI on http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""

# Start Streamlit
uv run streamlit run USER_INTERFACE/app.py --server.port 8501 --server.headless false