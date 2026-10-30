# DEV-P0-01 Implementation Specification - Locate and Wrap extract.py

## Ticket Summary
Priority: P0
Title: Locate and Wrap extract.py
Goal: Provide a reusable TimestampExtractor wrapper around existing extract.py timestamp logic with fallback.

## Existing Code Findings

Search results for `**/extract.py`:
- `/home/karthikean.juttumaha/mini-extract/extract.py` - Main implementation, 505 lines
- `/home/karthikean.juttumaha/mini-extract/samples4/extract.py` - Duplicate copy
- `/home/karthikean.juttumaha/mini-extract/prototype/extract.py` - Prototype copy
- `/home/karthikean.juttumaha/mini-extract/artifacts/extract.py` - Empty

Key classes in main extract.py:
- `MetadataExtractor.extract(file_path: Path) -> Dict`
  Returns `metadata['filesystem']['modified_time']` in ISO format with Z suffix
- `VersionHistoryExtractor._extract_from_filesystem(file_path: Path) -> List[EditNode]`
  Uses `stat.st_mtime` to generate timestamp
- `extract_file(file_path, ...)` orchestrator

Timestamp extraction capability already exists. Wrapper needed for clean API and fallback flag.

## Files to Create

1. `/home/karthikean.juttumaha/mini-extract/src/temporal/timestamp_extractor.py`
2. `/home/karthikean.juttumaha/mini-extract/tests/test_timestamp_extractor.py`

## Implementation Code

### File: src/temporal/timestamp_extractor.py

```python
#!/usr/bin/env python3
"""
TimestampExtractor wrapper for existing extract.py

Provides a simple interface to obtain file modification timestamp
for temporal validity tracking. Falls back to os.path.getmtime if
extract.py metadata extraction fails.
"""

from pathlib import Path
from datetime import datetime, timezone
from typing import Tuple
import os

# Import existing extractor from extract.py
from extract import MetadataExtractor

class TimestampExtractor:
    """
    Wrapper around existing extract.py timestamp extraction logic.
    
    Returns:
        as_of: datetime object representing file modification time
        fallback: bool indicating if fallback was used
    """
    
    def __init__(self):
        self.metadata_extractor = MetadataExtractor()
    
    def get_as_of(self, file_path: str | Path) -> Tuple[datetime, bool]:
        """
        Get as-of timestamp for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            (as_of_datetime, fallback_used)
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        fallback_used = False
        
        # Try using existing extract.py MetadataExtractor
        try:
            metadata = self.metadata_extractor.extract(path)
            modified_iso = metadata.get("filesystem", {}).get("modified_time")
            if modified_iso:
                iso_clean = modified_iso.replace("Z", "+00:00")
                as_of = datetime.fromisoformat(iso_clean)
                return as_of, False
        except Exception as e:
            fallback_used = True
        
        # Fallback to os.path.getmtime
        try:
            mtime = os.path.getmtime(path)
            as_of = datetime.fromtimestamp(mtime, tz=timezone.utc)
            return as_of, fallback_used
        except Exception as e:
            raise RuntimeError(f"Failed to get timestamp for {file_path}: {e}")
    
    def get_as_of_iso(self, file_path: str | Path) -> Tuple[str, bool]:
        """
        Get as-of timestamp as ISO string with Z suffix.
        """
        as_of, fallback = self.get_as_of(file_path)
        iso_str = as_of.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        return iso_str, fallback
```

### File: tests/test_timestamp_extractor.py

```python
#!/usr/bin/env python3
"""
Unit tests for TimestampExtractor
"""

import tempfile
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from temporal.timestamp_extractor import TimestampExtractor

def test_get_as_of_existing_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test content")
        temp_path = f.name
    
    try:
        extractor = TimestampExtractor()
        as_of, fallback = extractor.get_as_of(temp_path)
        assert isinstance(as_of, datetime)
        assert isinstance(fallback, bool)
        # as_of should be recent
        now = datetime.now(timezone.utc)
        assert now - as_of < timedelta(seconds=10)
        print("PASS: test_get_as_of_existing_file")
    finally:
        os.unlink(temp_path)

def test_get_as_of_iso_format():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test")
        temp_path = f.name
    
    try:
        extractor = TimestampExtractor()
        iso_str, fallback = extractor.get_as_of_iso(temp_path)
        assert iso_str.endswith("Z")
        # Should parse back
        parsed = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        assert isinstance(parsed, datetime)
        print("PASS: test_get_as_of_iso_format")
    finally:
        os.unlink(temp_path)

def test_file_not_found():
    extractor = TimestampExtractor()
    try:
        extractor.get_as_of("/nonexistent/path/file.txt")
        assert False, "Should raise FileNotFoundError"
    except FileNotFoundError:
        print("PASS: test_file_not_found")

def test_fallback_path():
    """Verify fallback to os.path.getmtime when MetadataExtractor fails."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test")
        temp_path = f.name
    try:
        extractor = TimestampExtractor()
        # Simulate failure by temporarily replacing metadata_extractor.extract
        original_extract = extractor.metadata_extractor.extract
        def failing_extract(path):
            raise RuntimeError("Simulated failure")
        extractor.metadata_extractor.extract = failing_extract
        
        as_of, fallback = extractor.get_as_of(temp_path)
        assert fallback is True, "Fallback flag should be True"
        assert isinstance(as_of, datetime)
        print("PASS: test_fallback_path")
        
        # Restore
        extractor.metadata_extractor.extract = original_extract
    finally:
        os.unlink(temp_path)

if __name__ == "__main__":
    test_get_as_of_existing_file()
    test_get_as_of_iso_format()
    test_file_not_found()
    test_fallback_path()
    print("All TimestampExtractor tests passed")
```

## Integration Notes

- Import path: `from src.temporal.timestamp_extractor import TimestampExtractor`
- TimestampExtractor is used by Intake Module to generate `as_of` for all facts derived from a file
- `as_of` is stored in Knowledge Graph Fact nodes and Provenance records
- Fallback flag is logged for audit; if fallback_used is True, set `timestamp_fallback=true` in Provenance metadata
- The wrapper reuses existing `extract.py` without modifying it, satisfying reuse requirement
- Future improvement: support git commit timestamps if file is in git repo

## Acceptance Criteria Verification

- [x] Existing extract.py located and analyzed
- [x] Wrapper design provides get_as_of with fallback
- [x] Unit tests cover existing file, ISO format, and missing file
- [x] Integration point documented for Intake Module

## Status
Ready for implementation
