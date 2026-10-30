#!/usr/bin/env python3
"""
Test runner script for the Temporal-Valid KG RAG System.

This script runs all unit tests and produces structured output
that can be used to verify the implementation.

Usage:
    python TESTING/run_tests.py
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


def run_pytest():
    """Run pytest and capture output."""
    result = subprocess.run(
        ["uv", "run", "pytest", "TESTING/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    return result


def run_tests_and_format():
    """Run tests and format results."""
    print("=" * 60)
    print("TEMPORAL-VALID KG RAG SYSTEM - TEST RUNNER")
    print("=" * 60)
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print()

    # Run pytest
    print("Running pytest...")
    result = run_pytest()

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Parse results
    output = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "passed": "passed" in result.stdout.lower(),
        "failed": result.returncode != 0,
    }

    # Write results
    results_file = Path(__file__).parent / "test_results.json"
    with open(results_file, "w") as f:
        json.dump(output, f, indent=2)

    print()
    print("=" * 60)
    print(f"Results written to: {results_file}")
    print("=" * 60)

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests_and_format())
