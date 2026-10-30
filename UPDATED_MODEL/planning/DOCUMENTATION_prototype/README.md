---
format: html
---

# Universal File Metadata & Version History Extractor - Prototype

## Overview

This prototype implements a system that can:
- Extract maximum metadata from ANY file type
- Track ALL historical changes to files
- Build knowledge graphs of file evolution
- Use multi-model extraction (multiple techniques per file)
- Assign evaluation bands (confidence scoring)

## Quick Start

### 1. Setup
```bash
cd /home/karthikean.juttumaha/mini-extract/prototype
mkdir -p samples results
```

### 2. Create Extractor Script
```bash
# Extract Python code from the template
python3 -c "
import re
with open('EXTRACTION_SCRIPT.md', 'r') as f:
    content = f.read()
code = re.search(r'```python(.*?)```', content, re.DOTALL)
if code:
    with open('extract.py', 'w') as f:
        f.write(code.group(1))
" 
```

### 3. Create Test File
```bash
cat > samples/test.txt << 'EOF'
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create -->
# Project Report
Initial content.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: bob | TYPE: add -->
## Introduction
Added introduction.

<!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: alice | TYPE: add -->
![Logo](logo.png)
EOF
```

### 4. Run
```bash
python3 extract.py samples/test.txt --output results/output.json
cat results/output.json
```

## File Structure

```
prototype/
├── README.md                    # This file
├── samples/                     # Test files
│   ├── test.txt                # Sample text with markers
│   ├── test.docx               # Sample Word with track changes
│   ├── test.pdf                # Sample PDF with metadata
│   └── ...
├── extract.py                   # Main extraction script
├── EXTRACTION_SCRIPT.md         # Extraction code template
├── RUN_INSTRUCTIONS.md          # How to run
├── RESULTS.md                   # Expected results
└── design/                      # Design documents
    ├── proposal.md
    ├── specs.md
    └── IMPLEMENTATION_ROADMAP.md
```

## Supported File Types

| Type | Extraction Method | Output |
|------|-------------------|--------|
| Text | Embedded markers | Edit history, timestamps, authors |
| Word | Track changes XML | Version history, authors |
| PDF | PyPDF2/pdfplumber | Metadata, text content |
| Images | Pillow/EXIF | Timestamps, camera info |
| Audio | pydub/mutagen | ID3 tags, duration |
| Video | OpenCV/FFmpeg | Codec, resolution, duration |
| Any | Filesystem | Size, timestamps, metadata |

## Knowledge Graph Output

Each file produces a knowledge graph with:
- **Nodes**: Individual edits/changes
- **Edges**: Relationships between edits
- **Properties**: Timestamps, authors, change types

Example output for text file with markers:
```json
{
  "knowledge_graph": {
    "nodes": [
      {
        "node_id": "edit_0",
        "timestamp": "2024-02-02T20:31:00Z",
        "author": "alice",
        "edit_type": "create",
        "content": "# Project Report...",
        "source": "embedded_marker",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_1",
        "timestamp": "2024-02-03T19:29:00Z",
        "author": "bob",
        "edit_type": "add",
        "content": "## Introduction...",
        "source": "embedded_marker",
        "evaluation_band": "high"
      }
    ],
    "edges": [
      {
        "source": "edit_0",
        "target": "edit_1",
        "relationship": "adds_to",
        "timestamp": "2024-02-03T19:29:00Z"
      }
    ]
  }
}
```

## Flow Pipeline

The extraction follows this structured flow:

1. **Ingestion** - File detection and validation
2. **Multi-Model Extraction** - Multiple extraction methods per file type
3. **Version Analysis** - Extract edit history from various sources
4. **Knowledge Graph Construction** - Build graph of changes
5. **Evaluation Band Assignment** - Confidence scoring
6. **Output** - JSON, GraphML, or GEXF format

## Evaluation Bands

All extracted data is assigned a confidence level:
- **High**: Git history, Word track changes, EXIF timestamps
- **Medium**: Embedded markers, most metadata
- **Low**: Filesystem-only metadata

## Dependencies

### Core (Required)
```bash
pip install python-magic
```

### For Full Functionality
```bash
pip install Pillow PyPDF2 pdfplumber python-docx openpyxl pydub networkx
```

### System Dependencies
- Tesseract OCR (for text extraction from images)
- FFmpeg (for audio/video processing)
- LibreOffice (for some document conversions)

## Testing

Test files are provided in the `samples/` directory with known edit histories. Run:

```bash
python3 extract.py samples/test.txt
python3 extract.py samples/test.docx
python3 extract.py samples/test.pdf
```

Each should produce a knowledge graph with the expected number of nodes and edges.

## Next Steps

1. Create all sample files
2. Install dependencies
3. Run extraction on each file
4. Validate results match expected outputs
5. Extend to additional file types as needed
