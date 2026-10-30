# Sample Files

This directory should contain **9 sample files** for testing the extractor:
- 3 Text files (`.txt`)
- 3 PDF files (`.pdf`)
- 3 Excel files (`.xlsx`)

---

## File Structure

```
samples/
├── text1.txt      # Basic text with 3 edits
├── text2.txt      # Text with 5 edits (includes delete)
├── text3.txt      # Text with image reference
├── pdf1.pdf       # PDF with metadata
├── pdf2.pdf       # PDF with multiple pages
├── pdf3.pdf       # Simple PDF
├── excel1.xlsx    # Excel with one sheet
├── excel2.xlsx    # Excel with multiple sheets
└── excel3.xlsx    # Excel with different create/apply dates
```

---

## Quick Setup

Run this **single command** to create everything:

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype

# Install all dependencies
pip install openpyxl PyPDF2 pdfplumber reportlab

# Create samples directory
mkdir -p samples results

# ============================================
# CREATE ALL 9 SAMPLE FILES
# ============================================

# -- Text Files (3) --
cat > samples/text1.txt << 'ENDOFFILE'
<!-- EDIT: 2024-01-01T10:00:00Z | AUTHOR: alice | TYPE: create -->
# Quarterly Report
Project Status: Active
Budget: $100,000

<!-- EDIT: 2024-01-02T14:30:00Z | AUTHOR: bob | TYPE: add -->
## Phase 1 Complete
All milestones achieved.

<!-- EDIT: 2024-01-03T09:15:00Z | AUTHOR: alice | TYPE: modify -->
## Phase 1 Complete
All milestones achieved on time.
Timelines updated for Phase 2.
ENDOFFILE

cat > samples/text2.txt << 'ENDOFFILE'
<!-- EDIT: 2024-02-01T08:00:00Z | AUTHOR: charlie | TYPE: create -->
# Technical Specification

## Overview
System requirements for Q2 deployment.

<!-- EDIT: 2024-02-01T10:00:00Z | AUTHOR: charlie | TYPE: add -->
## Hardware Requirements
- CPU: 4 cores
- RAM: 16GB
- Storage: 500GB SSD

<!-- EDIT: 2024-02-02T11:30:00Z | AUTHOR: diana | TYPE: add -->
## Software Requirements
- OS: Ubuntu 22.04
- Python: 3.10+
- Dependencies: openpyxl, PyPDF2

<!-- EDIT: 2024-02-03T09:00:00Z | AUTHOR: charlie | TYPE: modify -->
## Hardware Requirements
- CPU: 8 cores (updated)
- RAM: 32GB (updated)
- Storage: 1TB SSD (updated)

<!-- EDIT: 2024-02-03T14:00:00Z | AUTHOR: diana | TYPE: delete -->
## Software Requirements
- OS: Ubuntu 22.04
- Python: 3.10+
- Dependencies: openpyxl, PyPDF2
ENDOFFILE

cat > samples/text3.txt << 'ENDOFFILE'
<!-- EDIT: 2024-03-01T09:00:00Z | AUTHOR: eve | TYPE: create -->
# Marketing Materials

## Brand Guidelines

<!-- EDIT: 2024-03-01T11:00:00Z | AUTHOR: eve | TYPE: add | SECTION: logo -->
## Logo
Our logo is available in multiple formats.

![Company Logo](logo.png)

<!-- EDIT: 2024-03-02T10:00:00Z | AUTHOR: frank | TYPE: add | SECTION: colors -->
## Color Palette
- Primary: #0066CC
- Secondary: #FF6600
- Accent: #66CC33
ENDOFFILE

# -- PDF Files (3) --
python3 << 'ENDOFSCRIPT'
import reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime

# PDF 1
c = canvas.Canvas("samples/pdf1.pdf", pagesize=letter)
c.setTitle("Sample Report Q1")
c.setAuthor("alice")
c.setSubject("Quarterly financial report")
c.drawString(100, 750, "Sample Report Q1")
c.drawString(100, 730, "Author: alice")
c.drawString(100, 710, "Date: 2024-01-01")
c.drawString(100, 690, "Sample content for testing.")
c.save()
print("pdf1.pdf created")

# PDF 2
c = canvas.Canvas("samples/pdf2.pdf", pagesize=letter)
c.setTitle("Technical Manual")
c.setAuthor("bob")
c.setSubject("Technical documentation")
c.drawString(100, 750, "Technical Manual")
c.drawString(100, 730, "Page 1")
c.showPage()
c.drawString(100, 750, "Page 2")
c.showPage()
c.drawString(100, 750, "Page 3")
c.save()
print("pdf2.pdf created")

# PDF 3
c = canvas.Canvas("samples/pdf3.pdf", pagesize=letter)
c.setTitle("Simple Document")
c.setAuthor("charlie")
c.drawString(100, 750, "Simple PDF")
c.drawString(100, 730, "Basic content")
c.save()
print("pdf3.pdf created")
ENDOFSCRIPT

# -- Excel Files (3) --
python3 << 'ENDOFSCRIPT'
import openpyxl
from openpyxl import Workbook
from datetime import datetime, timedelta

# Excel 1
wb = Workbook()
ws = wb.active
ws.title = "Sheet1"
ws['A1'] = 'Product'
ws['B1'] = 'Quantity'
ws['C1'] = 'Price'
ws['A2'] = 'Widget A'
ws['B2'] = 100
ws['C2'] = 29.99
wb.properties.author = "alice"
wb.properties.title = "Sales Data Q1"
wb.properties.subject = "Quarterly sales"
wb.properties.created = datetime(2024, 1, 1, 9, 0, 0)
wb.properties.modified = datetime(2024, 1, 1, 9, 0, 0)
wb.save("samples/excel1.xlsx")
print("excel1.xlsx created")

# Excel 2
wb = Workbook()
wb.remove(wb.active)
ws1 = wb.create_sheet("Data")
ws1['A1'] = 'Name'; ws1['B1'] = 'Value'; ws1['A2'] = 'Item1'; ws1['B2'] = 100
ws2 = wb.create_sheet("Summary")
ws2['A1'] = 'Total'; ws2['B1'] = 300
wb.properties.author = "bob"
wb.properties.title = "Monthly Report"
wb.properties.created = datetime(2024, 1, 15, 10, 0, 0)
wb.properties.modified = datetime(2024, 1, 15, 10, 0, 0)
wb.save("samples/excel2.xlsx")
print("excel2.xlsx created")

# Excel 3
wb = Workbook()
ws = wb.active
ws.title = "Data"
ws['A1'] = 'Name'; ws['B1'] = 'Status'; ws['A2'] = 'ProjectA'; ws['B2'] = 'Complete'
wb.properties.author = "charlie"
wb.properties.title = "Project Tracker"
wb.properties.created = datetime(2024, 1, 10, 8, 0, 0)
wb.properties.modified = datetime(2024, 1, 11, 10, 30, 0)
wb.save("samples/excel3.xlsx")
print("excel3.xlsx created")
ENDOFSCRIPT

echo "=========================================="
echo "All 9 sample files created successfully!"
echo "=========================================="
```

---

## Verify Files Were Created

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype
ls -lh samples/
```

Expected output:
```
-rw-r--r-- 1 user user  1.2K Jan  1 10:00 excel1.xlsx
-rw-r--r-- 1 user user  2.5K Jan  1 10:00 excel2.xlsx
-rw-r--r-- 1 user user  2.1K Jan  1 10:00 excel3.xlsx
-rw-r--r-- 1 user user  3.5K Jan  1 10:00 pdf1.pdf
-rw-r--r-- 1 user user  4.2K Jan  1 10:00 pdf2.pdf
-rw-r--r-- 1 user user  2.8K Jan  1 10:00 pdf3.pdf
-rw-r--r-- 1 user user   201 Jan  1 10:00 text1.txt
-rw-r--r-- 1 user user   453 Jan  1 10:00 text2.txt
-rw-r--r-- 1 user user   221 Jan  1 10:00 text3.txt
```

---

## Test All Files

After creating all samples, test with:

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype

# Install dependencies (if not already installed)
pip install openpyxl PyPDF2 pdfplumber reportlab

# Create extract.py from template
python3 -c "
import re
with open('EXTRACTION_SCRIPT_FULL.md', 'r') as f:
    content = f.read()
code = re.search(r'```python(.*?)```', content, re.DOTALL)
if code:
    with open('extract.py', 'w') as f:
        f.write(code.group(1))
    print('extract.py created')
else:
    print('ERROR: Code not found')
"

# Test all 9 files
for file in samples/*.txt samples/*.pdf samples/*.xlsx; do
  echo "--- Testing: $(basename $file) ---"
  python3 extract.py "$file" --format simple
  echo ""
done
```

---

## Individual Test Commands

| File | Command |
|------|---------|
| text1.txt | `python3 extract.py samples/text1.txt --output results/text1.json` |
| text2.txt | `python3 extract.py samples/text2.txt --output results/text2.json` |
| text3.txt | `python3 extract.py samples/text3.txt --output results/text3.json` |
| pdf1.pdf | `python3 extract.py samples/pdf1.pdf --output results/pdf1.json` |
| pdf2.pdf | `python3 extract.py samples/pdf2.pdf --output results/pdf2.json` |
| pdf3.pdf | `python3 extract.py samples/pdf3.pdf --output results/pdf3.json` |
| excel1.xlsx | `python3 extract.py samples/excel1.xlsx --output results/excel1.json` |
| excel2.xlsx | `python3 extract.py samples/excel2.xlsx --output results/excel2.json` |
| excel3.xlsx | `python3 extract.py samples/excel3.xlsx --output results/excel3.json` |

---

## Expected Results Summary

| File | Nodes | Edges | Confidence | Key Feature |
|------|-------|-------|------------|-------------|
| text1.txt | 4 | 3 | High | 3 edits, 2 authors |
| text2.txt | 6 | 5 | High | 5 edits, includes delete |
| text3.txt | 4 | 3 | High | Image reference |
| pdf1.pdf | 2 | 1 | High | Metadata extraction |
| pdf2.pdf | 2 | 1 | High | Multiple pages |
| pdf3.pdf | 2 | 1 | High | Simple PDF |
| excel1.xlsx | 2 | 1 | High | Single sheet |
| excel2.xlsx | 2 | 1 | High | Multiple sheets |
| excel3.xlsx | 3 | 1 | High | Different create/modify dates |

**Total**: ~23 nodes, ~16 edges, all high confidence
