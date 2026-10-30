"""
Audit logger module for immutable audit trails.

This module provides append-only audit logging with SHA-256 hash chains
for tamper evidence. Every significant operation is logged with
cryptographic verification.

Usage:
    from src.audit.logger import AuditLogger

    logger = AuditLogger("./data/audit.jsonl")
    audit_id = logger.log({"event": "query", "question": "Who is CEO?"})
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional


class AuditLogger:
    """
    Append-only audit logger with hash chain for tamper evidence.

    Each log entry includes:
    - The event data
    - A timestamp
    - The hash of the previous entry (hash chain)
    - Its own hash for verification

    This provides immutable audit trail suitable for compliance
    in military/government environments.
    """

    def __init__(self, path: str) -> None:
        """
        Initialize the audit logger.

        Args:
            path: Path to the audit log file (will be created if needed)
        """
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._prev_hash = self._read_last_hash()

    def _read_last_hash(self) -> str:
        """Read the hash of the last entry in the log."""
        if not self.path.exists():
            return "GENESIS"  # Initial hash for first entry

        try:
            with open(self.path, "r") as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    if last_line:
                        entry = json.loads(last_line)
                        return entry.get("hash", "GENESIS")
        except json.JSONDecodeError, KeyError:
            pass

        return "GENESIS"

    def log(self, event: Dict[str, Any]) -> str:
        """
        Log an audit event.

        Creates an append-only entry with hash chain linking.

        Args:
            event: Event data to log (will be JSON-serialized)

        Returns:
            The hash of this entry for verification
        """
        # Build entry with chain link
        entry = {
            **event,
            "ts": datetime.now(timezone.utc).isoformat(),
            "prev_hash": self._prev_hash,
        }

        # Compute hash
        content = json.dumps(entry, sort_keys=True)
        entry_hash = hashlib.sha256(content.encode()).hexdigest()
        entry["hash"] = entry_hash

        # Append to file
        with open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # Update chain
        self._prev_hash = entry_hash

        return entry_hash

    def verify_chain(self) -> bool:
        """
        Verify the integrity of the audit log.

        Returns:
            True if all hashes chain correctly, False otherwise
        """
        if not self.path.exists():
            return True

        prev_hash = "GENESIS"

        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)

                    # Check prev_hash matches
                    if entry.get("prev_hash") != prev_hash:
                        return False

                    # Verify entry hash
                    entry_copy = {k: v for k, v in entry.items() if k != "hash"}
                    expected_hash = hashlib.sha256(
                        json.dumps(entry_copy, sort_keys=True).encode()
                    ).hexdigest()

                    if entry.get("hash") != expected_hash:
                        return False

                    prev_hash = entry.get("hash")

                except json.JSONDecodeError, KeyError:
                    return False

        return True

    def get_entries(
        self, event_type: Optional[str] = None, limit: int = 100
    ) -> list[Dict[str, Any]]:
        """
        Get audit log entries.

        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of entries to return

        Returns:
            List of audit entries
        """
        if not self.path.exists():
            return []

        entries = []
        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                    if event_type is None or entry.get("event") == event_type:
                        entries.append(entry)

                        if len(entries) >= limit:
                            break
                except json.JSONDecodeError:
                    continue

        return entries
