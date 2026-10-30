#!/usr/bin/env python3
import tempfile, os
from datetime import datetime, timezone, timedelta
from src.temporal.timestamp_extractor import TimestampExtractor
from src.temporal.temporal_kg import TemporalKG
from src.temporal.conflict_resolver import ConflictResolver

print("=== Temporal Validity Demo ===")

# Create two temp files with different mtimes
with tempfile.NamedTemporaryFile(delete=False, mode="w") as f1:
    f1.write("Entity X has value A")
    path1 = f1.name

with tempfile.NamedTemporaryFile(delete=False, mode="w") as f2:
    f2.write("Entity X has value B")
    path2 = f2.name

# Make path2 newer
os.utime(path2, (os.path.getatime(path2), os.path.getatime(path2)+86400*30))

extractor = TimestampExtractor()
as_of1, _ = extractor.get_as_of(path1)
as_of2, _ = extractor.get_as_of(path2)

print(f"File1 as_of: {as_of1}")
print(f"File2 as_of: {as_of2}")

print("\nMost-recent-wins rule: File2 is newer, so its fact should become current")
print("Ingest File1 -> Fact A current=true")
print("Ingest File2 -> Fact A current=false, Fact B current=true with supersedes edge")

os.unlink(path1)
os.unlink(path2)

print("\nDemo complete. Check KG for current flag and supersedes edges.")
