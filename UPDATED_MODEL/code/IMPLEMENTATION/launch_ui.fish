#!/usr/bin/env fish
set -x PYTHONPATH /home/karthikean.juttumaha/mini-extract
python -m streamlit run ui_streamlit.py --server.port 8501 --server.headless true &
echo "Streamlit starting at http://localhost:8501"
sleep 3
