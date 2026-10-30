---
format: html
---

# PDF with Metadata

**Filename**: `metadata.pdf`  
**Type**: Adobe Portable Document Format  
**Extraction Method**: PDF metadata parsing (PyPDF2, pdfplumber)  
**Expected Nodes**: 1 (basic) or 1+ (full)  
**Expected Edges**: 0  
**Confidence**: Low (basic) or High (full)  
**Creation Difficulty**: ⭐⭐ Medium

---

## 📋 Overview

PDF files can contain rich **metadata** including:
- Document title
- Author
- Subject
- Keywords
- Creation date
- Modification date
- Creator application

The extractor can extract this metadata and create a knowledge graph node representing the document's creation.

---

## 🎯 Creation Steps

### Option 1: Using Microsoft Word (Easiest)

1. **Open Microsoft Word**
2. **Create document** with content:
   ```
   PDF Test Document
   
   This document has embedded metadata for testing.
   
   Created: 2024-02-01
   Modified: 2024-02-02
   Author: PDF Test User
   ```

3. **Set document properties**:
   - Go to **File** → **Info**
   - Click **Properties** → **Advanced Properties**
   - **Summary Tab**:
     - Title: `Metadata Test Document`
     - Subject: `Testing PDF metadata extraction`
     - Author: `PDF Test User`
     - Keywords: `test, pdf, metadata`
     - Comments: `Created for testing Universal File Extractor`
   - **Statistics Tab**: (auto-filled)
   - **Custom Tab**: (optional)
   - Click **OK**

4. **Save as PDF**:
   - Go to **File** → **Export** → **Create PDF/XPS**
   - Filename: `metadata.pdf`
   - Location: `samples4/`
   - Click **Publish**

### Option 2: Using LibreOffice (Free Alternative)

1. **Open LibreOffice Writer**
2. **Create document** with same content as above
3. **Set properties**:
   - Go to **File** → **Properties**
   - **Description Tab**:
     - Title: `Metadata Test Document`
     - Subject: `Testing PDF metadata extraction`
     - Author: `PDF Test User`
     - Keywords: `test, pdf, metadata`
   - Click **OK**
4. **Export as PDF**:
   - Go to **File** → **Export As** → **Export as PDF**
   - Filename: `metadata.pdf`
   - Location: `samples4/`
   - Click **Export**

### Option 3: Using Online PDF Creator

1. Go to https://www.pdfescape.com/
2. Click **Create Free PDF**
3. Create a document with text:
   ```
   PDF Test Document
   
   This document has embedded metadata.
   ```
4. Go to **Document Properties** (usually under File menu)
5. Set title, author, subject
6. Download as PDF and save to `samples4/metadata.pdf`

### Option 4: Using Command Line (Advanced)

```bash
# Create a simple PDF using Python (requires reportlab)
pip install reportlab

python << 'EOF'
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

# Create PDF
c = canvas.Canvas("samples4/metadata.pdf", pagesize=letter)

# Set PDF metadata
c.setTitle("Metadata Test Document")
c.setAuthor("PDF Test User")
c.setSubject("Testing PDF metadata extraction")
c.setKeywords("test, pdf, metadata")
c.setCreator("Python ReportLab")

# Add content
c.drawString(100, 750, "PDF Test Document")
c.drawString(100, 730, "")
c.drawString(100, 710, "This document has embedded metadata for testing.")
c.drawString(100, 690, "")
c.drawString(100, 670, "Created: 2024-02-01")
c.drawString(100, 650, "Modified: 2024-02-02")
c.drawString(100, 630, "Author: PDF Test User")

# Save
c.save()
print("PDF created: samples4/metadata.pdf")
EOF
```

**Note**: The timestamps in the content are for display only. The actual PDF metadata timestamps are set by the PDF creation time.

---

## 🔍 File Verification

After creating the PDF, verify it:

```bash
# Check file exists
ls -la samples4/metadata.pdf

# Check file type
file samples4/metadata.pdf  # Should be: "PDF document"

# Check file size (should be reasonable for a PDF)
ls -lh samples4/metadata.pdf

# View PDF metadata (requires pdfinfo)
pdfinfo samples4/metadata.pdf
```

If `pdfinfo` is not installed:
```bash
# Ubuntu/Debian
sudo apt install poppler-utils

# macOS
brew install poppler
```

---

## 🎯 Extraction Commands

### Basic Version (Filesystem Only)
```bash
python extract.py samples4/metadata.pdf --output results/metadata.json
```

### Expected Output (Basic)
```json
{
  "extraction_metadata": {
    "file": "samples4/metadata.pdf",
    "timestamp": "2026-10-05T16:00:00Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": 15678,
      "created_time": "2026-10-05T15:55:00Z",
      "modified_time": "2026-10-05T15:55:00Z",
      "accessed_time": "2026-10-05T16:00:00Z"
    },
    "file_type": "application/pdf"
  },
  "version_history": {
    "edits": [
      {
        "node_id": "fs_metadata.pdf",
        "node_type": "edit",
        "timestamp": "2026-10-05T15:55:00Z",
        "author": null,
        "edit_type": "create",
        "content_after": "[Binary file: metadata.pdf]",
        "source": "filesystem",
        "evaluation_band": "low"
      }
    ],
    "edit_count": 1
  },
  "knowledge_graph": {
    "nodes": 1,
    "edges": 0,
    "total_nodes": 1,
    "total_edges": 0
  },
  "summary": {
    "total_edits": 1,
    "sources_used": ["filesystem"],
    "confidence_distribution": {"low": 1}
  }
}
```

### Full Version (With PyPDF2)
If you implement the full extractor with PyPDF2:

```bash
# First install dependency
pip install PyPDF2

# Then run (with full extract.py that includes PDF extractor)
python extract.py samples4/metadata.pdf --output results/metadata_full.json
```

### Expected Output (Full)
```json
{
  "extraction_metadata": {
    "file": "samples4/metadata.pdf",
    "timestamp": "2026-10-05T16:05:00Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": 15678,
      "created_time": "2026-10-05T15:55:00Z",
      "modified_time": "2026-10-05T15:55:00Z",
      "accessed_time": "2026-10-05T16:00:00Z"
    },
    "file_type": "application/pdf",
    "pdf_pypdf2": {
      "page_count": 1,
      "author": "PDF Test User",
      "title": "Metadata Test Document",
      "subject": "Testing PDF metadata extraction",
      "creator": "Microsoft Word",
      "producer": "Microsoft Word",
      "creation_date": "D:20240201080000Z",
      "modification_date": "D:20240202090000Z"
    }
  },
  "version_history": {
    "edits": [
      {
        "node_id": "pdf_metadata",
        "node_type": "edit",
        "timestamp": "2024-02-02T09:00:00Z",
        "author": "PDF Test User",
        "edit_type": "create",
        "description": "PDF document created",
        "source": "pdf_pypdf2",
        "evaluation_band": "high"
      }
    ],
    "edit_count": 1
  },
  "knowledge_graph": {
    "nodes": 1,
    "edges": 0,
    "total_nodes": 1,
    "total_edges": 0
  },
  "summary": {
    "total_edits": 1,
    "sources_used": ["pdf_pypdf2"],
    "confidence_distribution": {"high": 1}
  }
}
```

---

## 📊 Validation Commands

```bash
# Check PDF metadata was extracted
python -c "
import json
d = json.load(open('results/metadata.json'))
print('File metadata keys:', list(d['file_metadata'].keys()))
print('Has PDF metadata:', 'pdf' in d['file_metadata'])
"

# Check knowledge graph
python -c "
import json
d = json.load(open('results/metadata.json'))
kg = d['knowledge_graph']
print(f'Nodes: {kg[\"total_nodes\"]}')
print(f'Edges: {kg[\"total_edges\"]}')
print(f'Source: {d[\"summary\"][\"sources_used\"]}')
"
```

---

## 🎓 Key Concepts Demonstrated

1. **PDF metadata extraction** - Reading document properties
2. **Timestamp handling** - Parsing PDF date format
3. **Author extraction** - Getting creator/author info
4. **Binary file handling** - Reading complex file format
5. **Knowledge graph node** - Single node for document creation
6. **Evaluation band assignment** - High confidence for structured metadata

---

## 💡 Tips

1. **Use Word or LibreOffice** for easiest metadata setting
2. **Set all properties** to test extraction thoroughly
3. **Use meaningful timestamps** for easier validation
4. **Keep it simple** - One page is enough for testing
5. **Verify with pdfinfo** before extraction

---

## 🔗 Related

- **Previous**: [Text File with Embedded Markers](multi_edit_text.md)
- **Next**: [Image with EXIF](exif_image.md)
- **Full Specs**: [../../artifacts/specs.md](../../artifacts/specs.md)
- **Extraction Code**: [../../artifacts/extraction_engine.md](../../artifacts/extraction_engine.md)

---

**PDF files are excellent for testing metadata extraction. Even the basic version should recognize the file type and extract filesystem metadata.**
