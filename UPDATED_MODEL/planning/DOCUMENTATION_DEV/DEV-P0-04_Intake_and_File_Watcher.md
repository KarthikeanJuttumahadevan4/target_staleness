---
format: html
---

# DEV-P0-04 Implementation Specification - Intake & File Watcher

## Ticket Summary
Priority: P0
Title: Intake & File Watcher
Goal: Monitor samples5/ directory for new/modified files, emit IngestionEvent with as_of timestamp from TimestampExtractor.

## Files to Create

1. `/home/karthikean.juttumaha/mini-extract/src/ingestion/intake.py`
2. `/home/karthikean.juttumaha/mini-extract/src/ingestion/file_watcher.py`
3. `/home/karthikean.juttumaha/mini-extract/tests/test_intake.py`

## 1. Data Structure

### IngestionEvent

```python
@dataclass
class IngestionEvent:
    file_path: str
    as_of: datetime
    timestamp_fallback: bool
    ingestion_time: datetime
    file_hash: str
    event_type: str  # 'created' | 'modified'
```

## 2. Implementation Code

### File: src/ingestion/intake.py

```python
#!/usr/bin/env python3
"""
Intake module for file ingestion with timestamp extraction
"""

from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Callable
import hashlib

from temporal.timestamp_extractor import TimestampExtractor

@dataclass
class IngestionEvent:
    file_path: str
    as_of: datetime
    timestamp_fallback: bool
    ingestion_time: datetime
    file_hash: str
    event_type: str

class IntakeProcessor:
    def __init__(self, callback: Callable[[IngestionEvent], None]):
        self.timestamp_extractor = TimestampExtractor()
        self.callback = callback
    
    def process_file(self, file_path: str, event_type: str):
        path = Path(file_path)
        if not path.is_file():
            return
        
        # Get as_of timestamp
        as_of, fallback = self.timestamp_extractor.get_as_of(file_path)
        
        # Compute file hash for change detection
        file_hash = self._compute_hash(path)
        
        event = IngestionEvent(
            file_path=str(path.resolve()),
            as_of=as_of,
            timestamp_fallback=fallback,
            ingestion_time=datetime.now(timezone.utc),
            file_hash=file_hash,
            event_type=event_type
        )
        
        # Emit event to downstream
        self.callback(event)
    
    def _compute_hash(self, path: Path) -> str:
        hasher = hashlib.sha256()
        try:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""
```

### File: src/ingestion/file_watcher.py

```python
#!/usr/bin/env python3
"""
File watcher using watchdog for samples5/
"""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from ingestion.intake import IntakeProcessor

class SamplesEventHandler(FileSystemEventHandler):
    def __init__(self, intake_processor: IntakeProcessor):
        self.intake_processor = intake_processor
        self._seen_hashes = {}
    
    def on_created(self, event):
        if event.is_directory:
            return
        self._handle_event(event.src_path, 'created')
    
    def on_modified(self, event):
        if event.is_directory:
            return
        self._handle_event(event.src_path, 'modified')
    
    def _handle_event(self, file_path: str, event_type: str):
        # Debounce rapid modifications
        time.sleep(0.1)
        self.intake_processor.process_file(file_path, event_type)

class FileWatcher:
    def __init__(self, watch_dir: str, callback):
        self.watch_dir = Path(watch_dir)
        self.intake_processor = IntakeProcessor(callback)
        self.handler = SamplesEventHandler(self.intake_processor)
        self.observer = Observer()
    
    def start(self):
        self.observer.schedule(self.handler, str(self.watch_dir), recursive=True)
        self.observer.start()
        print(f"Watching {self.watch_dir} for changes...")
    
    def stop(self):
        self.observer.stop()
        self.observer.join()
```

## 3. Integration Points

### Downstream Flow
1. FileWatcher detects create/modify in samples5/
2. IntakeProcessor.process_file() called
3. TimestampExtractor.get_as_of() called → as_of datetime
4. IngestionEvent emitted via callback
5. Downstream Extraction Module receives event:
   - Uses event.file_path for multi-path extraction
   - Uses event.as_of for fact provenance
   - Uses event.timestamp_fallback for audit flag
6. ConflictResolver uses as_of for most-recent-wins comparison

### Callback Signature
```python
def on_ingestion(event: IngestionEvent):
    # Pass to extraction pipeline
    extraction_result = extract_file(event.file_path)
    # Pass to conflict resolver with event.as_of
    resolver.upsert_fact_with_resolution(..., as_of=event.as_of, ...)
```

## 4. Unit / Integration Tests

### File: tests/test_intake.py

```python
#!/usr/bin/env python3
"""
Tests for Intake and FileWatcher
"""

import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ingestion.intake import IntakeProcessor, IngestionEvent
from temporal.timestamp_extractor import TimestampExtractor

def test_intake_processor_emits_event():
    events = []
    def callback(event):
        events.append(event)
    
    processor = IntakeProcessor(callback)
    
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test content")
        temp_path = f.name
    
    try:
        processor.process_file(temp_path, 'created')
        assert len(events) == 1
        event = events[0]
        assert event.file_path == str(Path(temp_path).resolve())
        assert isinstance(event.as_of, datetime)
        assert event.event_type == 'created'
        assert isinstance(event.file_hash, str)
        print("PASS: test_intake_processor_emits_event")
    finally:
        os.unlink(temp_path)

def test_timestamp_extractor_integration():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test")
        temp_path = f.name
    
    try:
        extractor = TimestampExtractor()
        as_of, fallback = extractor.get_as_of(temp_path)
        assert isinstance(as_of, datetime)
        
        processor = IntakeProcessor(lambda e: None)
        event = IngestionEvent(
            file_path=temp_path,
            as_of=as_of,
            timestamp_fallback=fallback,
            ingestion_time=datetime.now(timezone.utc),
            file_hash="abc",
            event_type="created"
        )
        assert event.timestamp_fallback == fallback
        print("PASS: test_timestamp_extractor_integration")
    finally:
        os.unlink(temp_path)

def test_file_hash_computation():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"unique content")
        temp_path = f.name
    
    try:
        processor = IntakeProcessor(lambda e: None)
        # Access private method for test
        h1 = processor._compute_hash(Path(temp_path))
        h2 = processor._compute_hash(Path(temp_path))
        assert h1 == h2
        assert len(h1) == 64
        print("PASS: test_file_hash_computation")
    finally:
        os.unlink(temp_path)

if __name__ == "__main__":
    test_intake_processor_emits_event()
    test_timestamp_extractor_integration()
    test_file_hash_computation()
    print("All Intake tests passed")
```

## 5. Incremental Update Notes

- Watchdog monitors samples5/ recursively
- On file creation: process once with event_type='created'
- On modification: debounce 100ms to avoid duplicate events during write
- File hash used to detect actual content change vs metadata-only change
- IngestionEvent carries as_of from file modification time, not ingestion time
- This ensures conflict resolution compares file timestamps, not processing order
- Initial load: FileWatcher.start() can be combined with initial scan of existing files

## 6. Configuration

Default watch directory: `samples5/`
Can be overridden via environment variable `SAMPLES_DIR`

## Acceptance Criteria

- [x] File watcher monitors samples5/ with watchdog
- [x] TimestampExtractor called to obtain as_of
- [x] IngestionEvent data structure defined
- [x] Integration points with Extraction and Conflict Resolution documented
- [x] Unit tests for event emission, timestamp integration, hash computation
- [x] Incremental update flow described

Status: Ready for implementation
