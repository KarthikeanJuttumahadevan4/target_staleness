"""
Timestamp extractor module for temporal validity.

This module provides the temporal authority for the knowledge graph,
extracting as-of timestamps from file metadata. It reuses and improves
the logic from the legacy extract.py file.

The system requires every fact to be linked to a timestamp indicating
when it was valid in the world, enabling temporal queries and conflict
resolution.

Usage:
    from src.temporal.timestamp_extractor import TimestampExtractor

    extractor = TimestampExtractor()
    valid_at, fallback = extractor.get_as_of("path/to/file.pdf")
"""

from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Tuple, Optional, Dict, Any


class TimestampExtractor:
    """
    Extracts temporal metadata from files for temporal KG construction.

    This class provides the "as-of" timestamp that serves as the temporal
    authority for all facts extracted from a document. The timestamp comes
    from file modification time (mtime) when no embedded timestamp is available.

    For military documents, this enables:
    - Tracking when information was current in the field
    - Detecting conflicts based on document modification chronology
    - Historical queries (what did we know on date X?)

    Attributes:
        metadata_extractor: Legacy MetadataExtractor instance (reused from extract.py)
    """

    def __init__(self) -> None:
        """Initialize the timestamp extractor with legacy metadata extractor."""
        # Import here to avoid circular dependency and allow gradual migration
        try:
            from extract import MetadataExtractor

            self._metadata_extractor = MetadataExtractor()
        except ImportError:
            # Fallback if legacy extract.py not available
            self._metadata_extractor = None

    def get_as_of(self, file_path: str) -> Tuple[datetime, bool]:
        """
        Get the 'as-of' timestamp for a file.

        This is the temporal authority for all facts extracted from this file.
        The timestamp represents when the information in the file was valid.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Tuple of (valid_at, fallback_used):
            - valid_at: datetime object representing when this file's content is valid
            - fallback_used: True if falling back to filesystem mtime

        Raises:
            FileNotFoundError: If the file doesn't exist

        Example:
            >>> extractor = TimestampExtractor()
            >>> valid_at, fallback = extractor.get_as_of("report.pdf")
            >>> print(f"Valid from: {valid_at.isoformat()}")
            >>> print(f"Fallback used: {fallback}")
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        fallback_used = False

        # Try to get metadata from legacy extractor (includes embedded timestamps)
        try:
            if self._metadata_extractor:
                metadata: Dict[str, Any] = self._metadata_extractor.extract(path)
                modified_iso = metadata.get("filesystem", {}).get("modified_time")
                if modified_iso:
                    # Parse ISO format, handle both Z and +00:00 timezone formats
                    as_of = self._parse_iso_datetime(modified_iso)
                    return as_of, fallback_used
        except Exception:
            # If metadata extraction fails, log and fall back to filesystem
            fallback_used = True

        # Fallback to filesystem modification time
        mtime = os.path.getmtime(path)
        as_of = datetime.fromtimestamp(mtime, tz=timezone.utc)
        return as_of, fallback_used

    def get_mtime(self, file_path: str) -> datetime:
        """
        Get the filesystem modification time of a file.

        Args:
            file_path: Path to the file

        Returns:
            datetime object representing the file's modification time (UTC)

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        mtime = os.path.getmtime(path)
        return datetime.fromtimestamp(mtime, tz=timezone.utc)

    def get_created_at(self, file_path: str) -> datetime:
        """
        Get the file creation time (if available on the platform).

        Note: On some filesystems (Linux), creation time may not be available
        and will return the modification time instead.

        Args:
            file_path: Path to the file

        Returns:
            datetime object representing the file's creation time (UTC)
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = path.stat()
        # On Linux, st_ctime is metadata change time, not creation time
        # We use it as a fallback since true creation time isn't available
        return datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)

    @staticmethod
    def _parse_iso_datetime(iso_str: str) -> datetime:
        """
        Parse an ISO-8601 datetime string to a timezone-aware datetime.

        Handles various ISO formats including:
        - 2024-01-15T10:30:00Z
        - 2024-01-15T10:30:00+00:00
        - 2024-01-15T10:30:00.000Z

        Args:
            iso_str: ISO-8601 formatted datetime string

        Returns:
            timezone-aware datetime in UTC
        """
        # Replace Z with +00:00 for Python 3.10 compatibility
        normalized = iso_str.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)


def get_as_of(file_path: str) -> Tuple[datetime, bool]:
    """
    Convenience function to get the as-of timestamp for a file.

    This is a module-level convenience function that creates a
    TimestampExtractor instance and calls get_as_of.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (valid_at, fallback_used)
    """
    extractor = TimestampExtractor()
    return extractor.get_as_of(file_path)
