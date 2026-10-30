#!/usr/bin/env python3
"""
Main entry point for the Temporal-Valid KG RAG System.

This script starts the FastAPI server and optionally the file watcher
for document ingestion.

Usage:
    python main.py --port 8000 --watch-dir ./samples5
"""

from __future__ import annotations

import argparse
import threading
import logging

import uvicorn

from src.api.server import app
from src.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the RAG system.

    Starts the FastAPI server and optionally the file watcher
    for continuous document ingestion.
    """
    parser = argparse.ArgumentParser(
        description="Temporal-Valid Knowledge Graph RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for the HTTP API server (default: 8000)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--watch-dir",
        default=None,
        help="Directory to watch for new documents (overrides config)",
    )
    parser.add_argument(
        "--no-watch", action="store_true", help="Disable file watching (run API only)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Get settings
    settings = get_settings()
    watch_dir = args.watch_dir or settings.watch_dir

    # Start file watcher in background (if enabled)
    if not args.no_watch:
        try:
            from src.intake.watcher import start_watcher

            def watch_thread():
                """Background thread for file watching."""
                logger.info(f"Starting file watcher on {watch_dir}")
                start_watcher(watch_dir)

            watcher_thread = threading.Thread(target=watch_thread, daemon=True)
            watcher_thread.start()
            logger.info("File watcher started in background")
        except Exception as e:
            logger.warning(f"Failed to start file watcher: {e}")

    # Start FastAPI server
    logger.info(f"Starting server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level.lower())


if __name__ == "__main__":
    main()
