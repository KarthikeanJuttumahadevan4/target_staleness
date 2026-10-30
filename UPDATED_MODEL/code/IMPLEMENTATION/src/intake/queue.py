"""
Job queue module for managing document ingestion tasks.

This module provides a SQLite-backed job queue for managing
document ingestion tasks. It ensures idempotent processing
by tracking file paths and modification times.

The queue is designed for single-writer scenarios (typical in
single-process deployments) but can be extended for multi-process
if needed.

Usage:
    from src.intake.queue import JobQueue

    queue = JobQueue()
    queue.enqueue("/path/to/file.pdf", "created")
    job = queue.dequeue()
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json
import hashlib


class JobQueue:
    """
    SQLite-backed job queue for document ingestion.

    Implements idempotent job management where the same file
    (by path + mtime) won't be queued multiple times.
    """

    def __init__(self, db_path: str = "./data/jobs.db") -> None:
        """
        Initialize the job queue.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    mtime REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(file_path, mtime)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status ON jobs(status)
            """)

    def enqueue(self, file_path: str, event_type: str = "created") -> int:
        """
        Add a file to the job queue.

        Idempotent: if the same file (path + mtime) already exists,
        this is a no-op.

        Args:
            file_path: Path to the file to process
            event_type: "created" or "modified"

        Returns:
            Job ID (not currently used, but available for future use)
        """
        try:
            mtime = Path(file_path).stat().st_mtime
        except OSError:
            return -1

        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    "INSERT INTO jobs (file_path, mtime, event_type) VALUES (?, ?, ?)",
                    (file_path, mtime, event_type),
                )
                return conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            except sqlite3.IntegrityError:
                # Already queued - skip
                return -1

    def dequeue(self) -> Optional[Dict[str, Any]]:
        """
        Get the next pending job.

        Marks the job as 'processing' to prevent race conditions.

        Returns:
            Job dict with id, file_path, event_type, or None if empty
        """
        with sqlite3.connect(self.db_path) as conn:
            # Find a pending job and mark as processing
            cur = conn.execute("""
                UPDATE jobs 
                SET status = 'processing' 
                WHERE id = (
                    SELECT id FROM jobs WHERE status = 'pending' 
                    LIMIT 1
                )
                RETURNING id, file_path, event_type, created_at
            """)
            row = cur.fetchone()

            if row:
                return {
                    "id": row[0],
                    "file_path": row[1],
                    "event_type": row[2],
                    "created_at": row[3],
                }
            return None

    def mark_done(self, job_id: int, status: str = "done") -> None:
        """
        Mark a job as complete.

        Args:
            job_id: Job ID to update
            status: New status (default: "done")
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))

    def mark_failed(self, job_id: int, error: str) -> None:
        """
        Mark a job as failed with error message.

        Args:
            job_id: Job ID to update
            error: Error message
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE jobs SET status = ?, error = ? WHERE id = ?",
                ("failed", error, job_id),
            )

    def list_pending(self) -> list[Dict[str, Any]]:
        """List all pending jobs."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT id, file_path, event_type, created_at FROM jobs WHERE status = 'pending'"
            )
            return [
                {
                    "id": row[0],
                    "file_path": row[1],
                    "event_type": row[2],
                    "created_at": row[3],
                }
                for row in cur.fetchall()
            ]

    def get_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific job by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT id, file_path, event_type, status, created_at FROM jobs WHERE id = ?",
                (job_id,),
            )
            row = cur.fetchone()
            if row:
                return {
                    "id": row[0],
                    "file_path": row[1],
                    "event_type": row[2],
                    "status": row[3],
                    "created_at": row[4],
                }
            return None
