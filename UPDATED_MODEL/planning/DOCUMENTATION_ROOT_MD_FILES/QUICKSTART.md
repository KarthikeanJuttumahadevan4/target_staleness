---
format: html
---

# 🚀 Quick Start Guide

## Get the Universal File Metadata & Version History Extractor Running in 2 Hours

This guide will take you from zero to a working MVP (Minimum Viable Product) that can extract edit history from files and build knowledge graphs.

---

## ⏰ Timeline: 2 Hours to MVP

| Time | Task | Duration |
|------|------|----------|
| Now | Read this guide | 5 min |
| Step 1 | Create directory structure | 5 min |
| Step 2 | Convert main template | 15 min |
| Step 3 | Create test files | 10 min |
| Step 4 | Install dependencies | 20 min |
| Step 5 | Test and debug | 30 min |
| Step 6 | Validate | 15 min |
| Step 7 | Celebrate! | 20 min |

**Total: ~2 hours**

---

## Step 1: Create Directory Structure (5 min)

```bash
# From the project root (mini-extract/)
cd /home/karthikean.juttumaha/mini-extract

# Create main directories
mkdir -p extractor/metadata extractor/content extractor/version
mkdir -p graph pipeline evaluation tests
mkdir -p samples4/text_files samples4/documents samples4/images samples4/pdfs

# Verify
find . -type d | grep -E "(extractor|graph|pipeline|evaluation|tests|samples4)" | sort
```

✅ **Expected Output**: Directory structure created

---

## Step 2: Convert Main Template to Python (15 min)

### Create extract.py

Copy the content from `artifacts/main_extractor.md` to `extract.py`, but:
- Remove all markdown formatting (```python, etc.)
- Remove all text that's not Python code (descriptions, headers)
- Keep only the Python code
- Save as `extract.py`

**Fast method**:
```bash
# Extract just the Python code from the markdown
# This is a manual step - use the content between the first ```python
cat artifacts/main_extractor.md | sed -n '/^```python$/,/^```$/p' | sed '1d;$d' > extract.py
```

Then manually clean up any remaining markdown. Or just copy-paste from the .md file.

### Test basic import
```bash
python3 -c "import extract; print('Import successful')"
```

⚠️ **Expected**: May fail if dependencies aren't installed yet - that's OK, we'll fix in Step 4

---

## Step 3: Create Test Files (10 min)

### Create multi_edit_text.txt

Copy the content from `samples4/text_files/multi_edit_text.txt.md` to `samples4/text_files/multi_edit_text.txt`:

```bash
# From the markdown file, extract just the text content
cat samples4/text_files/multi_edit_text.txt.md | sed -n '/^```text$/,/^```$/p' | sed '1d;$d' > samples4/text_files/multi_edit_text.txt
```

**Or manually copy**:
```text
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: user1 | TYPE: create | SECTION: document_root | DESCRIPTION: Initial file creation -->
# Project Documentation

This is the initial version.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: user2 | TYPE: add | SECTION: intro | DESCRIPTION: Added intro -->
## Introduction

Added content.
```
**Note**: Use the shorter version above (2 edits) for faster testing. You can add more edits later.

### Create history JSON
```bash
cat > samples4/text_files/multi_edit_text.history.json << 'EOF'
{
  "filename": "multi_edit_text.txt",
  "total_expected_edits": 2,
  "total_expected_edges": 1,
  "extraction_method": "embedded_marker",
  "known_edits": [
    {
      "edit_id": "edit_001",
      "timestamp": "2024-02-02T20:31:00Z",
      "author": "user1",
      "edit_type": "create",
      "description": "Initial file creation"
    },
    {
      "edit_id": "edit_002",
      "timestamp": "2024-02-03T19:29:00Z",
      "author": "user2",
      "edit_type": "add",
      "description": "Added intro"
    }
  ]
}
EOF
```

✅ **Verify**: `ls -la samples4/text_files/` should show both files

---

## Step 4: Install Dependencies (20 min)

```bash
# Install core dependencies
pip install python-magic Pillow PyPDF2 pdfplumber python-docx openpyxl pydub networkx

# If you get permission errors, use:
pip install --user python-magic Pillow PyPDF2 pdfplumber python-docx openpyxl pydub networkx
```

**If you encounter issues**:
- On Ubuntu/Debian: `sudo apt-get install python3-magic tesseract-ocr ffmpeg`
- On macOS: `brew install python-magic tesseract ffmpeg`

### Test dependencies
```bash
python3 -c "import magic, PIL, PyPDF2, pdfplumber, docx, openpyxl, pydub, networkx; print('All dependencies OK')"
```

✅ **Expected**: "All dependencies OK" or just no errors

---

## Step 5: Convert Version Extractor (15 min)

The `extract.py` needs the version history extractor. Let's create it:

```bash
# Create the version extractor
cat > extractor/version/__init__.py << 'EOF'
# Version extractor package
EOF

# Copy the version extractor code
# Extract from artifacts/version_history_extractor.md - same method as Step 2
cat > extractor/version/version_extractor.py << 'PYEOF'
import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logger

# Simple EditNode class
class EditNode:
    def __init__(self, edit_id, timestamp, author, edit_type, 
                 content_before=None, content_after=None, 
                 affected_sections=None, description="", 
                 file_version="", source="", confidence="medium"):
        self.edit_id = edit_id
        self.timestamp = timestamp
        self.author = author
        self.edit_type = edit_type
        self.content_before = content_before
        self.content_after = content_after
        self.affected_sections = affected_sections or []
        self.description = description
        self.file_version = file_version
        self.source = source
        self.confidence = confidence
    
    def to_dict(self):
        return {
            "node_id": self.edit_id,
            "node_type": "edit",
            "timestamp": self.timestamp,
            "author": self.author,
            "edit_type": self.edit_type,
            "content_before": self.content_before,
            "content_after": self.content_after,
            "affected_sections": self.affected_sections,
            "description": self.description,
            "file_version": self.file_version,
            "source": self.source,
            "evaluation_band": self.confidence
        }

# Simple version analyzer
class VersionAnalyzer:
    def extract_from_embedded_markers(self, file_path):
        edits = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return edits
        
        # Pattern: <!-- EDIT: timestamp | AUTHOR: author | TYPE: type ... -->
        pattern = r'<!--\s*EDIT:\s*([^|]+)\s*\|\s*AUTHOR:\s*([^|]+)\s*\|\s*TYPE:\s*([^|]+)'
        
        for i, match in enumerate(re.finditer(pattern, content)):
            timestamp = match.group(1).strip()
            author = match.group(2).strip()
            edit_type = match.group(3).strip().lower()
            
            # Get content after marker
            start = match.end()
            end = len(content)
            for next_match in re.finditer(pattern, content[start:]):
                end = start + next_match.start()
                break
            
            content_text = content[start:end].strip()
            
            edit_id = f"edit_{i+1}"
            edit = EditNode(
                edit_id=edit_id,
                timestamp=timestamp,
                author=author if author != "None" else None,
                edit_type=edit_type,
                content_after=content_text if edit_type != "delete" else None,
                content_before=content_text if edit_type == "delete" else None,
                source="embedded_marker",
                confidence="high"
            )
            edits.append(edit)
        
        return edits

    def extract_history(self, file_path, git_repo_path=None):
        # For now, only use embedded markers
        return self.extract_from_embedded_markers(file_path)
PYEOF
```

---

## Step 5.5: Update extract.py to use Version Extractor (10 min)

Since we have a simpler version extractor, let's update `extract.py` to use it. However, if the template already has extraction logic, we might be able to use it as-is.

Let's create a simple version of extract.py that just does the minimum:

```bash
cat > extract.py << 'PYEOF'
#!/usr/bin/env python3
"""Universal File Metadata & Version History Extractor - MVP"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Import our version extractor
from extractor.version.version_extractor import VersionAnalyzer

def extract_file(file_path_str, output_format="json"):
    file_path = Path(file_path_str)
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    # Extract version history
    analyzer = VersionAnalyzer()
    edits = analyzer.extract_history(file_path, None)
    
    # Build knowledge graph
    nodes = [edit.to_dict() for edit in edits]
    edges = []
    
    # Create edges between consecutive edits
    for i in range(len(edits) - 1):
        edge = {
            "edge_id": f"edge_{i}_{i+1}",
            "source": edits[i].edit_id,
            "target": edits[i+1].edit_id,
            "edge_type": "temporal",
            "relationship": "successor",
            "timestamp": edits[i+1].timestamp,
            "weight": 1.0
        }
        edges.append(edge)
    
    # Build result
    result = {
        "extraction_metadata": {
            "file": str(file_path),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "extractor_version": "1.0.0"
        },
        "version_history": {
            "edits": [n for n in nodes],
            "edit_count": len(edits)
        },
        "knowledge_graph": {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        },
        "summary": {
            "total_edits": len(edits),
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "sources_used": ["embedded_marker"]
        },
        "evaluation_bands": {
            "version_confidence": "high"
        }
    }
    
    return result

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract file edit history')
    parser.add_argument('file', help='Path to the file')
    parser.add_argument('--output-format', choices=['json', 'graphml'], default='json')
    parser.add_argument('--output', '-o', help='Output file')
    
    args = parser.parse_args()
    
    result = extract_file(args.file, args.output_format)
    
    if args.output_format == 'json':
        output = json.dumps(result, indent=2, default=str)
    else:
        output = "GraphML not yet implemented"
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)

if __name__ == "__main__":
    main()
PYEOF
```

---

## Step 6: Test the MVP (30 min)

### Run extraction
```bash
python3 extract.py samples4/text_files/multi_edit_text.txt
```

✅ **Expected Output**: JSON with:
- 2 (or 6) edit nodes
- 1 (or 5) edges
- Extraction metadata
- Summary information

### Check for errors
If you see errors, check:
1. Python 3 is being used: `python3 --version`
2. Dependencies are installed: `pip list | grep -E "(magic|Pillow|pdfplumber)"`
3. Files are in the right place: `ls -la extractor/version/`

---

## Step 7: Validate Results (15 min)

### Simple validation
```bash
# Count nodes in output
python3 extract.py samples4/text_files/multi_edit_text.txt | python3 -c "import json, sys; data = json.load(sys.stdin); print(f'Nodes: {len(data[\"knowledge_graph\"][\"nodes\"])}'); print(f'Edges: {len(data[\"knowledge_graph\"][\"edges\"])}')"
```

✅ **Expected**:
- Nodes: 2 (if using the simple 2-edit file)
- Edges: 1

### Full validation (manual)
```bash
# Save output and check manually
python3 extract.py samples4/text_files/multi_edit_text.txt > result.json
cat result.json
```

Check that:
1. All timestamps are present
2. All authors are present
3. Edit types are correct
4. Content is extracted (at least partially)

---

## 🎉 Celebration Time!

If you've made it this far and the extraction is working, **you have a working MVP!**

### What You've Built
✅ File ingestion
✅ Embedded marker extraction
✅ Edit node creation
✅ Knowledge graph construction
✅ CLI interface
✅ JSON output

### What's Working
- The extractor can read text files with embedded markers
- It can detect edits and their timestamps
- It can create a knowledge graph of the edits
- It can output the results as JSON

### Next Steps (Optional)
If you want to keep going:

1. **Add more test files**: Create files with 5-6 edits
2. **Add git extraction**: Implement `VersionAnalyzer._extract_from_git_history()`
3. **Add more extractors**: Use the templates in `artifacts/extraction_engine.md`
4. **Add GraphML output**: For visualization
5. **Create comprehensive tests**: Use `artifacts/validation_script.md`

But for now, **take a break and celebrate!** You've successfully built the core of a Universal File Metadata & Version History Extractor.

---

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**
```
ModuleNotFoundError: No module named 'pdfplumber'
```
**Fix**: `pip install pdfplumber`

**2. File Not Found**
```
FileNotFoundError: [Errno 2] No such file or directory
```
**Fix**: Check file paths, use absolute paths or correct relative paths

**3. Encoding Errors**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x80
```
**Fix**: The extractor uses UTF-8 with error replacement, but you can add encoding detection

**4. HTML Parser Not Found**
```
ImportError: lxml not found
```
**Fix**: `pip install lxml` (optional for advanced Word parsing)

### Debug Tips

```bash
# Run with Python debug
python3 -X dev extract.py file.txt

# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Check imports individually
python3 -c "import extractor.version.version_extractor; print('OK')"
```

---

## 📋 MVP Checklist

- [ ] Directory structure created
- [ ] extract.py created and working
- [ ] Version extractor created
- [ ] Test file created (multi_edit_text.txt)
- [ ] Dependencies installed
- [ ] Extraction runs without errors
- [ ] Output contains expected edits
- [ ] Knowledge graph is generated

**If all checked, MVP is complete! 🎉**

---

## 🚀 What's Next?

Once the MVP is working, consider:

1. **Adding more file types**: PDF, Word, Excel, Images, etc.
2. **Adding git history extraction**: For files in git repos
3. **Adding more extraction methods**: Multiple per file type
4. **Adding evaluation bands**: Confidence scoring
5. **Adding visualization**: GraphML export for visualization tools
6. **Creating comprehensive tests**: Automated validation
7. **Packaging for distribution**: pip install universal-extractor

But for now, enjoy your working MVP!

---

## 📞 Need Help?

Check these files for more information:
- **README.md** - Complete project overview
- **artifacts/proposal.md** - Project design
- **artifacts/IMPLEMENTATION_ROADMAP.md** - Detailed implementation plan
- **artifacts/version_history_extractor.md** - Full version extractor code
- **artifacts/extraction_engine.md** - Full extraction engine code

---

**You're ready to go! The project is designed, the templates are written, and the path is clear. Now it's time to bring it to life.**

Happy coding! 🎊
