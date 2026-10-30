---
format: html
---

# EXACT Commands to Create Everything

This file contains the **exact step-by-step commands** to create the full prototype with PDF + Excel support and all 9 sample files.

---

## STEP 1: Navigate to Prototype Directory

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype
```

---

## STEP 2: Install All Dependencies

**Single command:**
```bash
pip install openpyxl PyPDF2 pdfplumber reportlab python-magic 2>&1 | grep -v "already satisfied" || true
```

**Individual installation (if above fails):**
```bash
pip install openpyxl
pip install PyPDF2
pip install pdfplumber
pip install reportlab
pip install python-magic
```

---

## STEP 3: Create Directory Structure

```bash
mkdir -p samples results
```

---

## STEP 4: Create extract.py from Full Template

**Command:**
```bash
python3 -c "
import re
with open('EXTRACTION_SCRIPT_FULL.md', 'r') as f:
    content = f.read()
code = re.search(r'```python(.*?)```', content, re.DOTALL)
if code:
    with open('extract.py', 'w') as f:
        f.write(code.group(1))
    print('SUCCESS: extract.py created')
else:
    print('ERROR: Python code not found')
"
```

**Verify:**
```bash
ls -lh extract.py
head -5 extract.py
```

---

## STEP 5: Create All 9 Sample Files

**RUN THIS SINGLE COMMAND (RECOMMENDED):**

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype && (
# Text 1
cat > samples/text1.txt << 'EOF'
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
EOF &&

# Text 2
cat > samples/text2.txt << 'EOF'
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

<!-- EDIT: 2024-02-03T09:00:00Z | AUTHOR: charlie | TYPE: modify -->
## Hardware Requirements
- CPU: 8 cores (updated)
- RAM: 32GB (updated)
- Storage: 1TB SSD (updated)

<!-- EDIT: 2024-02-03T14:00:00Z | AUTHOR: diana | TYPE: delete -->
## Software Requirements
- OS: Ubuntu 22.04
- Python: 3.10+
EOF &&

# Text 3
cat > samples/text3.txt << 'EOF'
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
EOF &&

# PDF 1, 2, 3
python3 << 'PYEOF'
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas("samples/pdf1.pdf", pagesize=letter)
c.setTitle("Sample Report Q1")
c.setAuthor("alice")
c.setSubject("Quarterly financial report")
c.drawString(100, 750, "Sample Report Q1")
c.drawString(100, 730, "Author: alice")
c.drawString(100, 710, "Sample content for testing.")
c.save()

c = canvas.Canvas("samples/pdf2.pdf", pagesize=letter)
c.setTitle("Technical Manual")
c.setAuthor("bob")
c.setSubject("Technical documentation")
c.drawString(100, 750, "Technical Manual")
c.showPage()
c.drawString(100, 750, "Page 2")
c.showPage()
c.drawString(100, 750, "Page 3")
c.save()

c = canvas.Canvas("samples/pdf3.pdf", pagesize=letter)
c.setTitle("Simple Document")
c.setAuthor("charlie")
c.drawString(100, 750, "Simple PDF")
c.save()
print("3 PDF files created")
PYEOF &&

# Excel 1, 2, 3
python3 << 'PYEOF'
import openpyxl
from openpyxl import Workbook
from datetime import datetime

# Excel 1
wb = Workbook()
ws = wb.active
ws.title = "Sheet1"
ws['A1'] = 'Product'; ws['B1'] = 'Quantity'; ws['C1'] = 'Price'
ws['A2'] = 'Widget A'; ws['B2'] = 100; ws['C2'] = 29.99
wb.properties.author = "alice"
wb.properties.title = "Sales Data Q1"
wb.properties.created = datetime(2024, 1, 1, 9, 0, 0)
wb.properties.modified = datetime(2024, 1, 1, 9, 0, 0)
wb.save("samples/excel1.xlsx")

# Excel 2
wb = Workbook()
wb.remove(wb.active)
ws1 = wb.create_sheet("Data"); ws1['A1'] = 'Name'; ws1['B1'] = 'Value'; ws1['A2'] = 'Item1'; ws1['B2'] = 100
ws2 = wb.create_sheet("Summary"); ws2['A1'] = 'Total'; ws2['B1'] = 300
wb.properties.author = "bob"
wb.properties.title = "Monthly Report"
wb.properties.created = datetime(2024, 1, 15, 10, 0, 0)
wb.properties.modified = datetime(2024, 1, 15, 10, 0, 0)
wb.save("samples/excel2.xlsx")

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
print("3 Excel files created")
PYEOF &&

# Verify all files exist
echo "=== Verifying 9 sample files ==="
ls -lh samples/
echo ""
echo "SUCCESS: All 9 sample files created!"
)
```

---

## STEP 6: Verify Files

```bash
ls -lh samples/
```

**Expected:**
- 3 .txt files
- 3 .pdf files
- 3 .xlsx files

---

## STEP 7: Run extract.py on All Files

**Option A: Test one by one**
```bash
python3 extract.py samples/text1.txt --output results/text1.json
python3 extract.py samples/text2.txt --output results/text2.json
python3 extract.py samples/text3.txt --output results/text3.json

python3 extract.py samples/pdf1.pdf --output results/pdf1.json
python3 extract.py samples/pdf2.pdf --output results/pdf2.json
python3 extract.py samples/pdf3.pdf --output results/pdf3.json

python3 extract.py samples/excel1.xlsx --output results/excel1.json
python3 extract.py samples/excel2.xlsx --output results/excel2.json
python3 extract.py samples/excel3.xlsx --output results/excel3.json
```

**Option B: Test all at once (faster)**
```bash
cd /home/karthikean.juttumaha/mini-extract/prototype
for f in samples/*.txt samples/*.pdf samples/*.xlsx; do
  echo "--- $(basename $f) ---"
  python3 extract.py "$f" --format simple
  echo ""
done
```

---

## STEP 8: Quick Verification

**Check results summary:**
```bash
cd /home/karthikean.juttumaha/mini-extract/prototype
python3 << 'PYEOF'
import json, os

results = {}
for f in ["text1", "text2", "text3", "pdf1", "pdf2", "pdf3", "excel1", "excel2", "excel3"]:
    for ext in [".json"]:
        path = f"results/{f}{ext}"
        if os.path.exists(path):
            with open(path) as fh:
                data = json.load(fh)
            results[path] = {
                "nodes": data["knowledge_graph"]["total_nodes"],
                "edges": data["knowledge_graph"]["total_edges"],
                "sources": data["summary"]["sources_used"],
                "confidence": data["summary"]["confidence_distribution"]
            }

print("RESULTS SUMMARY:")
print("=" * 60)
for path, info in sorted(results.items()):
    print(f"{os.path.basename(path):20s} | Nodes: {info['nodes']:2d} | Edges: {info['edges']:2d} | Sources: {info['sources']} | Conf: {info['confidence']}")
print("=" * 60)
print(f"Total files processed: {len(results)}")
PYEOF
```

---

## STEP 9: Cleanup (Optional)

**Remove all results:**
```bash
rm -rf results/*
```

**Remove all samples:**
```bash
rm -rf samples/*
```

---

## Complete One-Liner (All Steps)

If you want to do everything in **ONE command**:

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype && mkdir -p samples results && pip install openpyxl PyPDF2 pdfplumber reportlab python-magic 2>&1 | tail -1 && python3 -c "import re; exec(re.search(r'```python(.*?)```', open('EXTRACTION_SCRIPT_FULL.md').read(), re.DOTALL).group(1))" > /dev/null && cat > samples/text1.txt << 'EOF'
<!-- EDIT: 2024-01-01T10:00:00Z | AUTHOR: alice | TYPE: create -->
# Test
Content 1
<!-- EDIT: 2024-01-02T10:00:00Z | AUTHOR: bob | TYPE: add -->
Content 2
EOF && python3 -c "from reportlab.pdfgen import canvas; c=canvas.Canvas('samples/pdf1.pdf'); c.setTitle('Test'); c.setAuthor('alice'); c.drawString(100,750,'Test PDF'); c.save(); print('PDF1')" && python3 -c "import openpyxl; wb=openpyxl.Workbook(); wb.properties.author='alice'; wb.save('samples/excel1.xlsx'); print('XLSX1')" && python3 extract.py samples/text1.txt --format simple && echo "ALL DONE - Check output above"
```

---

## Troubleshooting

**Error: "No module named openpyxl"**
```bash
pip install openpyxl
```

**Error: "No module named reportlab"**
```bash
pip install reportlab
```

**Error: "No module named PyPDF2"**
```bash
pip install PyPDF2
```

**Error: "No such file or directory"**
```bash
cd /home/karthikean.juttumaha/mini-extract/prototype
ls -la
```

**Error: extract.py not found**
```bash
# Re-run the extract.py creation command from STEP 4
```

---

## Success Criteria

You have **successfully completed** the setup when:

1. ✅ Directory `prototype/` exists
2. ✅ Directory `prototype/samples/` has 9 files (3 txt, 3 pdf, 3 xlsx)
3. ✅ Directory `prototype/results/` exists
4. ✅ File `extract.py` exists in prototype/ (not .md)
5. ✅ Running `python3 extract.py samples/text1.txt --format simple` produces output
6. ✅ All 9 files can be processed without errors
7. ✅ Results show knowledge graphs with nodes and edges
