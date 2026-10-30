#!/usr/bin/env python3
import tempfile, os
from src.temporal.timestamp_extractor import TimestampExtractor
def test_get_as_of():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test")
        p = f.name
    try:
        e = TimestampExtractor()
        as_of, fb = e.get_as_of(p)
        assert as_of is not None
        print("PASS: test_get_as_of")
    finally:
        os.unlink(p)
if __name__ == "__main__":
    test_get_as_of()
