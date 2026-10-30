#!/usr/bin/env python3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
from src.temporal.timestamp_extractor import TimestampExtractor

@dataclass
class IngestionEvent:
    file_path: str
    as_of: datetime
    timestamp_fallback: bool
    ingestion_time: datetime
    file_hash: str
    event_type: str

class IntakeProcessor:
    def __init__(self, callback):
        self.extractor = TimestampExtractor()
        self.callback = callback
    def process_file(self, file_path, event_type):
        path = Path(file_path)
        as_of, fallback = self.extractor.get_as_of(path)
        h = hashlib.sha256()
        with open(path,"rb") as f:
            h.update(f.read())
        event = IngestionEvent(str(path.resolve()), as_of, fallback, datetime.now(timezone.utc), h.hexdigest(), event_type)
        self.callback(event)
