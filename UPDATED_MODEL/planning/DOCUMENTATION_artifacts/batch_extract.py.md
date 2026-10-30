---
format: html
---

# batch_extract.py
```python
#!/usr/bin/env python3
"""Batch extract samples/ using existing extract.py and persist JSON outputs."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import subprocess

ROOT = Path(__file__).parent.parent
SAMPLES = ROOT / "samples"
OUT_DIR = ROOT / "artifacts" / "extractions"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED = {".pdf", ".xlsx", ".txt", ".wav", ".mp3", ".m4a", ".ogg", ".mp4", ".mov", ".mkv", ".webm"}

def run_extract(file_path: Path):
    cmd = [sys.executable, str(ROOT / "extract.py"), str(file_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    stderr = result.stderr
    stdout = result.stdout.strip()
    try:
        data = json.loads(stdout) if stdout else {}
    except json.JSONDecodeError:
        data = {"error": "invalid json", "stdout": stdout, "stderr": stderr}
    stat = file_path.stat()
    data.update({
        "file_path": str(file_path),
        "file_name": file_path.name,
        "suffix": file_path.suffix.lower(),
        "file_size": stat.st_size,
        "file_mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "file_ctime": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
        "stderr": stderr.strip(),
        "exit_code": result.returncode,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
    })
    return data

def main():
    files = [p for p in SAMPLES.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED]
    results = []
    for f in sorted(files):
        print(f"Processing {f.relative_to(ROOT)}...", file=sys.stderr)
        data = run_extract(f)
        out_path = OUT_DIR / f"{f.stem}.json"
        if out_path.exists():
            out_path = OUT_DIR / f"{f.stem}_{f.parent.name}.json"
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        results.append(data)
    index_path = OUT_DIR / "index.json"
    with index_path.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(f"Wrote {len(results)} extractions to {OUT_DIR}", file=sys.stderr)

if __name__ == "__main__":
    main()
```
