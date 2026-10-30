"""
Tests for the User Interface module.
Verifies that the UI can be loaded and configured properly.
"""

import pytest
from pathlib import Path


def test_ui_file_exists():
    """Verify UI app file exists."""
    ui_path = Path(__file__).parent.parent / "USER_INTERFACE" / "app.py"
    assert ui_path.exists(), "UI app.py should exist"


def test_ui_requirements_exist():
    """Verify UI requirements file exists."""
    req_path = Path(__file__).parent.parent / "USER_INTERFACE" / "requirements.txt"
    assert req_path.exists(), "UI requirements.txt should exist"


def test_ui_readme_exists():
    """Verify UI README exists."""
    readme_path = Path(__file__).parent.parent / "USER_INTERFACE" / "README.md"
    assert readme_path.exists(), "UI README.md should exist"


def test_ui_syntax_valid():
    """Verify UI code has valid Python syntax."""
    import ast

    ui_path = Path(__file__).parent.parent / "USER_INTERFACE" / "app.py"
    with open(ui_path, "r") as f:
        code = f.read()

    try:
        ast.parse(code)
    except SyntaxError as e:
        pytest.fail(f"UI code has syntax error: {e}")


def test_ui_imports():
    """Verify UI can import system modules."""
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))

    # This should not raise an exception
    from src.retrieval.hybrid import query
    from src.models import QueryRequest, RetrievedFact

    assert callable(query), "query should be callable"
    assert QueryRequest is not None, "QueryRequest should exist"
    assert RetrievedFact is not None, "RetrievedFact should exist"


def test_ui_startup_script_exists():
    """Verify startup script exists and is executable."""
    script_path = Path(__file__).parent.parent / "USER_INTERFACE" / "start.sh"
    assert script_path.exists(), "start.sh should exist"

    # Check if executable
    assert script_path.stat().st_mode & 0o111, "start.sh should be executable"


def test_ui_features():
    """Test that UI has all required features."""
    ui_path = Path(__file__).parent.parent / "USER_INTERFACE" / "app.py"
    with open(ui_path, "r") as f:
        content = f.read()

    # Check for required features
    required_features = [
        "TemporalRAGInterface",  # Main class
        "query",  # Query function
        "RetrievedFact",  # Model import
        "pure_rag",  # Mode 1
        "rag_kg_validator",  # Mode 2
        "kg_only",  # Mode 3
        "as_of",  # Temporal filtering
        "include_history",  # History checkbox
        "confidence",  # Confidence scores
        "citation",  # Citations
    ]

    for feature in required_features:
        assert feature in content, f"UI should have feature: {feature}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
