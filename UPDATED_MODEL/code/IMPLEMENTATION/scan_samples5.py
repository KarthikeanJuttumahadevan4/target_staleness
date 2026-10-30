#!/usr/bin/env python3
import os
from pathlib import Path
from src.temporal.timestamp_extractor import TimestampExtractor

base = Path("samples5")
extractor = TimestampExtractor()

print("samples5 temporal scan")
print("="*60)
for p in sorted(base.rglob("*")):
    if p.is_file():
        try:
            as_of, fallback = extractor.get_as_of(p)
            rel = str(p.relative_to(base))
            print(f"{rel:40} | as_of={as_of.isoformat()} | fallback={fallback}")
        except Exception as e:
            rel = str(p.relative_to(base))
            print(f"{rel:40} | ERROR: {e}")

print("="*60)
print("Done.")
