"""
Temporal-Valid KG RAG System - User Interface
================================================
A Streamlit-based web interface for querying the knowledge graph
with temporal awareness, fuzzy query support, and real-time updates.

Features:
- Fuzzy query support (semantic + keyword matching)
- Real-time database queries
- Temporal filtering with "as_of" timestamps
- Current vs superseded data indicators
- Multi-modal retrieval (Pure RAG, RAG+KG, KG-only)
- Live updates as data changes

Usage:
    cd /home/karthikean.juttumaha/mini-extract
    uv run streamlit run USER_INTERFACE/app.py
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import time
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import system modules
try:
    from src.retrieval.hybrid import query
    from src.models import QueryRequest, RetrievedFact
    from src.config import get_settings
    from src.classification.query_classifier import classify_query, auto_query

    QUERY_AVAILABLE = True
except ImportError:
    QUERY_AVAILABLE = False
    st.warning("System modules not available - running in demo mode")


class TemporalRAGInterface:
    """Main UI class for the Temporal-Valid KG RAG System."""

    def __init__(self):
        self.settings = get_settings() if QUERY_AVAILABLE else None
        self.last_query_time = None
        self.last_results = None

    def render_header(self):
        """Render the application header."""
        st.set_page_config(
            page_title="Temporal-Valid KG RAG System",
            page_icon="🕐",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        st.title("🕐 Temporal Knowledge Graph RAG System")
        st.markdown("""
        Query your documents with temporal awareness. The system tracks how facts change over time
        and always returns the most current information by default.
        """).unsafe_html = True

        # Status indicator
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", "🟢 Online" if QUERY_AVAILABLE else "🟡 Demo Mode")
        with col2:
            st.metric("Database", "Neo4j + Qdrant")
        with col3:
            st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))

    def render_query_panel(self) -> tuple:
        """Render the query input panel and return user inputs."""
        with st.expander("📝 Query Configuration", expanded=True):
            # Query input with fuzzy search hint
            st.markdown("### Enter your question (supports fuzzy queries)")
            st.markdown(
                "*Examples: 'Who is CEO?', 'What changed in 2024?', 'Find all contracts'"
            )

            question = st.text_area(
                "Question",
                height=100,
                placeholder="Enter natural language question...",
                key="question_input",
            )

            # Retrieval mode selection
            mode = st.radio(
                "Retrieval Mode",
                options=["auto", "pure_rag", "rag_kg_validator", "kg_only"],
                format_func=lambda x: {
                    "auto": "🤖 Auto (AI decides)",
                    "pure_rag": "🔍 Pure RAG (Vector Search)",
                    "rag_kg_validator": "🔗 RAG + KG Validator",
                    "kg_only": "🧠 KG Only (Graph Traversal)",
                }[x],
                horizontal=True,
                key="mode_selector",
            )

            # Temporal filtering
            st.markdown("---")
            st.markdown("### Temporal Settings")

            col1, col2 = st.columns(2)
            with col1:
                as_of_date = st.date_input(
                    "As Of Date (History)",
                    value=None,
                    help="Query as of a specific date (shows data valid at that time)",
                    key="as_of_date",
                )

            with col2:
                include_history = st.checkbox(
                    "Include Historical Facts",
                    value=False,
                    help="Show superseded facts in results",
                    key="history_checkbox",
                )

            # Advanced settings
            with st.expander("⚙️ Advanced Settings"):
                k = st.slider("Number of Results", 1, 100, 10, key="k_slider")
                show_confidence = st.checkbox(
                    "Show Confidence Scores", value=True, key="confidence_checkbox"
                )

            return question, mode, as_of_date, include_history, k, show_confidence

    def process_query(
        self,
        question: str,
        mode: str,
        as_of: Optional[datetime],
        include_history: bool,
        k: int,
    ) -> Optional[dict]:
        """Process a query and return results."""
        if not question.strip():
            return None

        if not QUERY_AVAILABLE:
            # Demo mode - generate mock results
            return self._generate_demo_results(question)

        try:
            with st.spinner("🔍 Searching knowledge graph..."):
                start_time = time.time()

                # Build as-of string
                as_of_str = as_of.isoformat() if as_of else None

                # Auto-classify if mode is "auto"
                actual_mode = mode
                if mode == "auto":
                    actual_mode, reason, confidence = classify_query(question)
                    st.info(
                        f"🤖 Auto-selected mode: {actual_mode} ({confidence:.0%} confidence)"
                    )

                # Execute query
                results = query(
                    question=question,
                    mode=actual_mode,
                    as_of=as_of_str,
                    include_history=include_history,
                    k=k,
                )

                latency = time.time() - start_time

                return {
                    "results": results,
                    "latency": latency,
                    "timestamp": datetime.now().isoformat(),
                    "selected_mode": actual_mode,
                }
        except Exception as e:
            st.error(f"❌ Query failed: {str(e)}")
            return None

    def _generate_demo_results(self, question: str) -> dict:
        """Generate demo results when system is not available."""
        return {
            "results": None,
            "latency": 0.1,
            "timestamp": datetime.now().isoformat(),
            "demo": True,
            "message": "Demo mode - System modules not available",
        }

    def render_results(self, results: dict, show_confidence: bool):
        """Render query results."""
        if not results:
            st.info("Enter a question to see results")
            return

        if results.get("demo"):
            st.warning(results.get("message", "Demo mode"))
            return

        # Results header
        st.markdown("---")
        st.markdown("### 📊 Results")

        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Latency", f"{results['latency'] * 1000:.0f}ms")
        with col2:
            fact_count = len(results["results"].facts) if results["results"] else 0
            st.metric("Facts Found", fact_count)
        with col3:
            st.metric(
                "Mode",
                results["results"].mode.replace("_", " ").title()
                if results["results"]
                else "N/A",
            )

        # Display facts
        if results["results"] and results["results"].facts:
            for i, fact in enumerate(results["results"].facts, 1):
                # Determine if current
                is_current = fact.current
                current_label = "🟢 Current" if is_current else "🟡 Superseded"

                with st.container():
                    st.markdown(f"---")
                    st.markdown(f"**Result {i}** {current_label}")

                    # Fact content
                    st.markdown(f"**Fact:** {fact.content}")

                    # Metadata
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"**Source:** `{fact.source}`")
                    with col2:
                        st.markdown(f"**As-of:** `{fact.as_of}`")
                    with col3:
                        st.markdown(f"**Method:** `{fact.extraction_path or 'N/A'}`")
                    with col4:
                        if show_confidence:
                            st.markdown(f"**Confidence:** {fact.confidence:.2f}")

                    # Citation
                    st.markdown(f"**Citation:** {fact.citation}")

                    # Timestamp info
                    st.caption(f"*Retrieved at: {results['timestamp']}*")
        else:
            st.info("No results found for this query")

    def render_history_panel(self):
        """Render query history panel."""
        st.markdown("---")
        with st.expander("📋 Query History"):
            if "query_history" not in st.session_state:
                st.session_state.query_history = []

            for i, entry in enumerate(
                reversed(st.session_state.query_history[-10:]), 1
            ):
                st.markdown(f"{i}. **{entry['question']}** ({entry['timestamp']})")

    def run(self):
        """Main application loop."""
        self.render_header()

        st.markdown("---")

        # Query panel
        question, mode, as_of, include_history, k, show_confidence = (
            self.render_query_panel()
        )

        # Process query on button click
        if st.button("🚀 Execute Query", type="primary", use_container_width=True):
            if question.strip():
                results = self.process_query(question, mode, as_of, include_history, k)

                if results:
                    # Store in session state for history
                    if "query_history" not in st.session_state:
                        st.session_state.query_history = []
                    st.session_state.query_history.append(
                        {
                            "question": question,
                            "mode": mode,
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "as_of": str(as_of) if as_of else "Now",
                        }
                    )

                    self.last_query_time = time.time()
                    self.last_results = results

                    # Render results
                    self.render_results(results, show_confidence)

        # History panel
        self.render_history_panel()

        # Footer
        st.markdown("---")
        st.markdown("*Temporal-Valid KG RAG System v2.0 - Built for production use*")


def main():
    """Entry point for the UI application."""
    app = TemporalRAGInterface()
    app.run()


if __name__ == "__main__":
    main()
