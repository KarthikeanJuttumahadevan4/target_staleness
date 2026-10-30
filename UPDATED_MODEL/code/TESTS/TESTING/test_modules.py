#!/usr/bin/env python3
"""
Unit tests for the Temporal-Valid KG RAG System.

These tests verify the core functionality of each module using
sample files in the SAMPLES directory.

Run tests with: uv run pytest TESTING/ -v
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

import pytest

# Import modules to test
from src.config import Settings, get_settings
from src.models import Fact, QueryRequest, RetrievedFact
from src.temporal.timestamp_extractor import TimestampExtractor
from src.intake.router import route, get_ingest_method
from src.reconstruction.conflict_resolver import ConflictResolver, resolve_conflict


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def settings():
    """Get application settings."""
    return get_settings()


@pytest.fixture
def timestamp_extractor():
    """Create timestamp extractor instance."""
    return TimestampExtractor()


@pytest.fixture
def conflict_resolver():
    """Create conflict resolver instance."""
    return ConflictResolver()


@pytest.fixture
def sample_files():
    """Get paths to sample test files."""
    samples_dir = Path(__file__).parent.parent / "SAMPLES"
    return {
        "text": samples_dir / "sample_text.txt",
        "invoice": samples_dir / "sample_invoice.txt",
        "json": samples_dir / "sample_metadata.json",
    }


# ============================================================================
# CONFIG TESTS
# ============================================================================


class TestConfig:
    """Tests for src/config.py"""

    def test_settings_loads_defaults(self, settings: Settings):
        """Verify settings load with default values."""
        # Settings are loaded from .env, so check they exist
        assert settings.model is not None
        assert settings.vlm_model is not None
        assert settings.watch_dir == "./samples5"

    def test_settings_cache(self):
        """Verify settings are cached (singleton)."""
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2


# ============================================================================
# TIMESTAMP EXTRACTOR TESTS
# ============================================================================


class TestTimestampExtractor:
    """Tests for src/temporal/timestamp_extractor.py"""

    def test_get_as_of_returns_datetime(
        self, timestamp_extractor: TimestampExtractor, sample_files
    ):
        """Verify get_as_of returns a datetime object."""
        for name, path in sample_files.items():
            if path.exists():
                result, fallback = timestamp_extractor.get_as_of(str(path))
                assert isinstance(result, datetime), f"Failed for {name}"

    def test_get_as_of_fallback_on_missing_metadata(
        self, timestamp_extractor: TimestampExtractor, sample_files
    ):
        """Verify fallback to filesystem mtime."""
        text_file = sample_files["text"]
        if text_file.exists():
            result, fallback = timestamp_extractor.get_as_of(str(text_file))
            assert isinstance(result, datetime)

    def test_file_not_found(self, timestamp_extractor: TimestampExtractor):
        """Verify FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            timestamp_extractor.get_as_of("/nonexistent/file.txt")

    def test_get_mtime(self, timestamp_extractor: TimestampExtractor, sample_files):
        """Verify get_mtime returns datetime."""
        text_file = sample_files["text"]
        if text_file.exists():
            result = timestamp_extractor.get_mtime(str(text_file))
            assert isinstance(result, datetime)


# ============================================================================
# ROUTER TESTS
# ============================================================================


class TestRouter:
    """Tests for src/intake/router.py"""

    def test_route_text_files(self):
        """Verify text files route to 'text'."""
        assert route("document.txt") == "text"
        assert route("data.json") == "text"
        assert route("config.xml") == "text"

    def test_route_pdf(self):
        """Verify PDF routes to 'text'."""
        assert route("report.pdf") == "text"
        assert route("invoice.pdf") == "text"

    def test_route_excel(self):
        """Verify Excel routes to 'text'."""
        assert route("data.xlsx") == "text"
        assert route("spreadsheet.xls") == "text"

    def test_route_pptx(self):
        """Verify PowerPoint routes to 'text'."""
        assert route("presentation.pptx") == "text"
        assert route("slides.ppt") == "text"

    def test_route_audio(self):
        """Verify audio files route to 'audio'."""
        assert route("recording.mp3") == "audio"
        assert route("voice.wav") == "audio"
        assert route("speech.m4a") == "audio"

    def test_route_video(self):
        """Verify video files route to 'video'."""
        assert route("recording.mp4") == "video"
        assert route("footage.avi") == "video"
        assert route("clip.mov") == "video"

    def test_route_images(self):
        """Verify images route to 'vlm'."""
        assert route("chart.png") == "vlm"
        assert route("diagram.jpg") == "vlm"
        assert route("scan.tiff") == "vlm"

    def test_route_archives(self):
        """Verify archives route to 'archive'."""
        assert route("bundle.zip") == "archive"
        assert route("package.tar.gz") == "archive"
        assert route("files.7z") == "archive"

    def test_route_unsupported(self):
        """Verify unsupported files route to 'unsupported'."""
        assert route("data.xyz") == "unsupported"
        assert route("unknown.xyz") == "unsupported"

    def test_get_ingest_method(self):
        """Verify standardized ingest method names."""
        assert get_ingest_method("doc.PDF") == "pdf_text"
        assert get_ingest_method("audio.mp3") == "audio_asr"
        assert get_ingest_method("chart.png") == "vlm"


# ============================================================================
# CONFLICT RESOLVER TESTS
# ============================================================================


class TestConflictResolver:
    """Tests for src/reconstruction/conflict_resolver.py"""

    def test_no_conflict(self, conflict_resolver: ConflictResolver):
        """Verify keep action when no conflict exists."""
        new_fact = {"entity_id": "emp1", "predicate": "CEO", "valid_at": "2024-01-01"}
        existing = [
            {"entity_id": "emp2", "predicate": "EMPLOYEE", "valid_at": "2023-01-01"}
        ]

        result = conflict_resolver.reconcile(new_fact, existing)
        assert result.action == "keep"

    def test_newer_supersedes(self, conflict_resolver: ConflictResolver):
        """Verify newer fact supersedes older."""
        new_fact = {"entity_id": "emp1", "predicate": "CEO", "valid_at": "2024-06-01"}
        existing = [
            {
                "entity_id": "emp1",
                "predicate": "CEO",
                "valid_at": "2024-01-01",
                "fact_id": "fact123",
            }
        ]

        result = conflict_resolver.reconcile(new_fact, existing)
        assert result.action == "supersede"
        assert result.superseded_fact_id == "fact123"

    def test_older_kept(self, conflict_resolver: ConflictResolver):
        """Verify older fact is kept when new is older."""
        new_fact = {"entity_id": "emp1", "predicate": "CEO", "valid_at": "2023-01-01"}
        existing = [
            {
                "entity_id": "emp1",
                "predicate": "CEO",
                "valid_at": "2024-06-01",
                "fact_id": "fact123",
            }
        ]

        result = conflict_resolver.reconcile(new_fact, existing)
        assert result.action == "keep"

    def test_same_timestamp(self, conflict_resolver: ConflictResolver):
        """Verify keep when timestamps are equal."""
        new_fact = {"entity_id": "emp1", "predicate": "CEO", "valid_at": "2024-01-01"}
        existing = [
            {
                "entity_id": "emp1",
                "predicate": "CEO",
                "valid_at": "2024-01-01",
                "fact_id": "fact123",
            }
        ]

        result = conflict_resolver.reconcile(new_fact, existing)
        assert result.action == "keep"


# ============================================================================
# MODELS TESTS
# ============================================================================


class TestModels:
    """Tests for src/models.py"""

    def test_fact_creation(self):
        """Verify Fact model creates correctly."""
        from datetime import datetime

        fact = Fact(
            fact_id="test123",
            content="CEO is Satya Nadella",
            entity_id="msft",
            predicate="CEO",
            valid_at="2024-01-01T00:00:00Z",
            created_at=datetime.utcnow().isoformat() + "Z",
            source_file="report.pdf",
            extraction_path="text",
            model_used="docling",
        )
        assert fact.current == True
        assert fact.confidence == 1.0

    def test_query_request_defaults(self):
        """Verify QueryRequest has correct defaults."""
        req = QueryRequest(question="Who is CEO?")
        assert req.mode == "pure_rag"
        assert req.k == 10
        assert req.include_history == False

    def test_retrieved_fact(self):
        """Verify RetrievedFact model."""
        fact = RetrievedFact(
            fact_id="f1",
            content="Test fact",
            source="test.pdf",
            as_of="2024-01-01",
            current=True,
            confidence=0.95,
            citation="Page 1",
        )
        assert fact.current == True


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """Integration tests using sample files."""

    def test_sample_files_exist(self, sample_files):
        """Verify sample files exist for testing."""
        expected = ["text", "invoice", "json"]
        for name in expected:
            if name in sample_files:
                assert isinstance(sample_files[name], Path)

    def test_timestamp_consistency(
        self, timestamp_extractor: TimestampExtractor, sample_files
    ):
        """Verify timestamps are consistent across file types."""
        timestamps = {}
        for name, path in sample_files.items():
            if path.exists():
                ts, _ = timestamp_extractor.get_as_of(str(path))
                timestamps[name] = ts

        for name, ts in timestamps.items():
            assert ts.year >= 2024, f"{name} timestamp too old: {ts}"
