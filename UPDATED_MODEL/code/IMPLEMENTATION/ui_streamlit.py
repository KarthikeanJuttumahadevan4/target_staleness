"""
Streamlit UI for Temporal KG-RAG System.

This UI connects to the FastAPI backend and displays query results
with proper formatting, citations, and provenance.
"""

import streamlit as st
import requests
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"

# Page setup
st.set_page_config(
    page_title="Temporal KG-RAG Demo",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main {padding: 2rem;}
    .answer-box {background: #f0f2f6; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #4285f4; margin: 1rem 0;}
    .fact-box {background: #ffffff; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; border: 1px solid #ddd;}
    .citation {font-size: 0.85rem; color: #666; margin-top: 0.5rem; padding: 0.5rem; background: #fafafa; border-radius: 3px;}
    .confidence {font-size: 0.9rem; color: #555; font-weight: 500;}
    .stButton > button {width: 100%;}
</style>
""",
    unsafe_allow_html=True,
)

# Title and description
st.title("🔍 Temporal KG-RAG System")
st.markdown(
    "Query documents with temporal validity. **Most recent facts are shown by default.**"
)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown(f"**API URL:** `{API_URL}`")

    st.markdown("---")
    st.header("📊 Status")

    # Check API health
    try:
        health = requests.get(f"{API_URL}/health", timeout=2)
        if health.status_code == 200:
            st.markdown("✅ **API: Online**")
        else:
            st.markdown(f"⚠️ **API: Status {health.status_code}**")
    except Exception:
        st.markdown("❌ **API: Offline**")

    try:
        ready = requests.get(f"{API_URL}/ready", timeout=2)
        if ready.status_code == 200:
            st.markdown("✅ **Ready: Yes**")
        else:
            st.markdown("⚠️ **Ready: No**")
    except Exception:
        st.markdown("⚠️ **Ready: Unknown**")

    st.markdown("---")
    st.header("💡 Example Queries")
    st.markdown("- What is the status of operation Alpha?")
    st.markdown("- What is the budget of operation Alpha?")
    st.markdown("- Who is the commander of operation Alpha?")
    st.markdown("- When does operation Alpha begin?")

# Main query interface
with st.form("query_form", clear_on_submit=False):
    col1, col2 = st.columns([5, 1])

    with col1:
        question = st.text_input(
            "Enter your query:",
            placeholder="What is the status of operation Alpha?",
            value="What is the status of operation Alpha?",
            label_visibility="collapsed",
        )

    with col2:
        mode = st.selectbox(
            "Mode:",
            options=["pure_rag", "rag_kg_validator", "kg_only"],
            format_func=lambda x: x.replace("_", " ").title(),
            label_visibility="collapsed",
        )

    st.markdown("---")
    submitted = st.form_submit_button(
        "🔍 Search", type="primary", use_container_width=True
    )

# Process query
if submitted and question:
    with st.spinner("Searching knowledge graph..."):
        try:
            # Prepare request
            payload = {"question": question, "mode": mode, "include_history": False}

            # Call API
            response = requests.post(
                f"{API_URL}/query",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()

                # Display results
                st.markdown("---")
                st.markdown("## 📋 Results")

                # Answer
                st.markdown("### ✅ Answer")
                st.markdown(
                    f'<div class="answer-box">{data["answer"]}</div>',
                    unsafe_allow_html=True,
                )

                # Confidence
                if data.get("confidence", 0) > 0:
                    st.markdown(f"**Confidence:** {data['confidence']:.0%}")

                # Citations
                if data.get("citations"):
                    st.markdown("### 📜 Citations")
                    for citation in data["citations"]:
                        st.markdown(
                            f'<div class="citation">{citation}</div>',
                            unsafe_allow_html=True,
                        )

                # Facts
                if data.get("facts"):
                    st.markdown("### 📊 Supporting Facts")
                    for i, fact in enumerate(data["facts"], 1):
                        with st.container():
                            st.markdown(
                                f'<div class="fact-box">', unsafe_allow_html=True
                            )
                            st.markdown(f"**Fact {i}:** {fact['content']}")
                            st.markdown(f"**Source:** {fact['source']}")
                            st.markdown(f"**As-of:** {fact['as_of']}")
                            st.markdown(f"**Confidence:** {fact['confidence']:.0%}")
                            st.markdown("</div>", unsafe_allow_html=True)

                # Audit ID
                st.markdown(f"**Audit ID:** `{data['audit_id']}`")

            else:
                st.error(f"❌ API Error: {response.status_code}")
                try:
                    error_detail = response.json().get("detail", response.text)
                    st.code(error_detail)
                except:
                    st.code(response.text)

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API server")
            st.markdown("**Solution:** Start the API server with:")
            st.code("python src/api/server.py")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.markdown(
                "**Details:** Check that the API server is running on port 8000"
            )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.85rem;'>"
    "Temporal-Valid KG-RAG System | Demo Mode | Using Mock Data"
    "</div>",
    unsafe_allow_html=True,
)

# If no query submitted, show welcome message
if not submitted:
    st.markdown("---")
    st.markdown("### 🎯 Get Started")
    st.markdown("""
    1. Enter a query in the text box above
    2. Select a retrieval mode
    3. Click **Search**
    4. View the answer with citations and provenance
    
    **Demo Facts in System:**
    - Operation Alpha status: APPROVED
    - Operation Alpha budget: $500,000
    - Operation Alpha commander: Captain Smith
    - Operation Beta status: PENDING
    """)
