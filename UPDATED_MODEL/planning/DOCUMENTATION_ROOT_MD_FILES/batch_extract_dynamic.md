# batch_extract_dynamic.py
```python
#!/usr/bin/env python3
"""Batch extract from a user-specified directory using existing extract.py and persist JSON outputs."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import subprocess
import argparse

ROOT = Path(__file__).parent
DEFAULT_SAMPLES = ROOT / "samples"
OUT_DIR = ROOT / "artifacts" / "extractions"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED = {".pdf", ".xlsx", ".txt", ".wav", ".mp3", ".m4a", ".ogg", ".mp4", ".mov", ".mkv", ".webm"}

def parse_args():
    parser = argparse.ArgumentParser(description="Batch extract files")
    parser.add_argument(
        "input_dir",
        nargs="?",
        default=str(DEFAULT_SAMPLES),
        help="Directory to scan for supported files. Defaults to samples/"
    )
    parser.add_argument(
        "--out-dir",
        default=str(OUT_DIR),
        help="Directory to write extraction JSON files"
    )
    return parser.parse_args()

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
    args = parse_args()
    input_dir = Path(args.input_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Input directory {input_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    files = [p for p in input_dir.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED]
    results = []
    for f in sorted(files):
        print(f"Processing {f.relative_to(input_dir)}...", file=sys.stderr)
        data = run_extract(f)
        # make output filename unique per input dir
        rel_path = f.relative_to(input_dir).with_suffix("")
        safe_name = "_".join(rel_path.parts) + ".json"
        out_path = out_dir / safe_name
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        results.append(data)
    
    index_path = out_dir / "index.json"
    with index_path.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(f"Wrote {len(results)} extractions to {out_dir}", file=sys.stderr)

if __name__ == "__main__":
    main()
```
