"""
File watcher module for detecting new and modified documents.

This module implements a file system watcher that monitors the samples5/
directory for new or modified files and queues them for ingestion.

The watcher uses watchdog's Observer pattern for efficient file system
monitoring and supports filtering of file types and size limits.

Usage:
    from src.intake.watcher import start_watcher

    start_watcher("./samples5")
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Callable
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent

from src.intake.queue import JobQueue


# Maximum file size to process (500MB)
MAX_FILE_SIZE = 500 * 1024 * 1024

# File extensions to skip (binary archives, etc.)
SKIP_EXTENSIONS = {".pyc", ".pyo", ".so", ".dll"}


class DocumentHandler(FileSystemEventHandler):
    """
    Event handler for file system events in the watched directory.

    Handles file creation and modification events, filtering out
    temporary files and unsupported formats.
    """

    def __init__(self, job_queue: JobQueue) -> None:
        """
        Initialize the handler with a job queue.

        Args:
            job_queue: Queue to enqueue detected file events
        """
        super().__init__()
        self.queue = job_queue

    def on_created(self, event: FileCreatedEvent) -> None:
        """Handle file creation events."""
        if event.is_directory:
            return

        if self._should_process(event.src_path):
            self.queue.enqueue(event.src_path, "created")

    def on_modified(self, event: FileModifiedEvent) -> None:
        """Handle file modification events."""
        if event.is_directory:
            return

        if self._should_process(event.src_path):
            self.queue.enqueue(event.src_path, "modified")

    def _should_process(self, path: str) -> bool:
        """
        Determine if a file should be processed.

        Checks:
        - File exists and is readable
        - File size within limits
        - File extension is supported
        - Not a temporary/hidden file
        """
        try:
            p = Path(path)

            # Skip directories
            if not p.is_file():
                return False

            # Skip size limit
            if p.stat().st_size > MAX_FILE_SIZE:
                return False

            # Skip unsupported extensions
            if p.suffix.lower() in SKIP_EXTENSIONS:
                return False

            # Skip hidden/temporary files
            if p.name.startswith(".") or p.name.startswith("~"):
                return False

            return True

        except OSError, PermissionError:
            return False


def start_watcher(
    watch_dir: str,
    job_queue: Optional[JobQueue] = None,
    callback: Optional[Callable[[str, str], None]] = None,
) -> None:
    """
    Start watching a directory for new and modified files.

    This function blocks and runs indefinitely, monitoring the
    specified directory for changes.

    Args:
        watch_dir: Directory path to watch
        job_queue: Optional job queue (creates one if not provided)
        callback: Optional callback for processing events

    Example:
        >>> queue = JobQueue()
        >>> start_watcher("./samples5", job_queue=queue)
    """
    watch_path = Path(watch_dir).resolve()

    if not watch_path.exists():
        raise FileNotFoundError(f"Watch directory does not exist: {watch_path}")

    if job_queue is None:
        job_queue = JobQueue()

    # Create event handler and observer
    handler = DocumentHandler(job_queue)
    observer = Observer()

    # Schedule watching (recursive)
    observer.schedule(handler, str(watch_path), recursive=True)

    # Start the observer
    observer.start()

    try:
        # Keep the main thread alive
        while True:
            observer.join(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
