"""
Intake module for document detection and routing.

This module provides the intake pipeline that detects new/modified
documents and routes them to appropriate extraction handlers.
"""

from .watcher import start_watcher, DocumentHandler
from .queue import JobQueue
from .router import route

__all__ = ["start_watcher", "DocumentHandler", "JobQueue", "route"]
