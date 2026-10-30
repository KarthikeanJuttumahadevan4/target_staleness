---
format: html
---

# PDF File Samples (3 files)

Use these commands to create the 3 PDF sample files for testing.

---

## Important Note

You **cannot** create actual PDF files with text commands alone. You need one of these:

### **Option A: Use LibreOffice (Free)**
Convert text files to PDF:
```bash
libreoffice --headless --convert-to pdf samples/pdf1.txt
mv samples/pdf1.pdf samples/pdf1.pdf
```

### **Option B: Use Python**
```bash
pip install reportlab
python3 -c "from reportlab.pdfgen import canvas; c = canvas.Canvas('samples/pdf1.pdf'); c.drawString(100,750,'Sample PDF'); c.save()"
```

### **Option C: Manual**
Create the PDFs manually with your PDF editor and save them as:
- `samples/pdf1.pdf`
- `samples/pdf2.pdf`
- `samples/pdf3.pdf`

---

## File 1: pdf1.pdf - Basic PDF with metadata

### Content Template (for manual creation):
- Title: "Sample Report Q1"
- Author: "alice"
- Subject: "Quarterly financial report"
- Created: January 1, 2024
- Content: Some sample text

### Create via ReportLab:
```bash
cd /home/karthikean.juttumaha/mini-extract/prototype
python3 << 'ENDOFSCRIPT'
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime

c = canvas.Canvas("samples/pdf1.pdf", pagesize=letter)
c.setTitle("Sample Report Q1")
c.setAuthor("alice")
c.setSubject("Quarterly financial report")

c.drawString(100, 750, "Sample Report Q1")
c.drawString(100, 730, "Author: alice")
c.drawString(100, 710, "Date: 2024-01-01")
c.drawString(100, 690, "This is a sample PDF for testing metadata extraction.")
c.save()
print("pdf1.pdf created")
ENDOFSCRIPT
```

### Expected Results:
- **Nodes**: 1-2 (creation + modification if timestamps differ)
- **Authors**: alice
- **Source**: pdf_metadata (PyPDF2 or pdfplumber)
- **Confidence**: High
- **File Node**: Yes

---

## File 2: pdf2.pdf - PDF with multiple pages

### Create via ReportLab:
```bash
cd /home/karthikean.juttumaha/mini-extract/prototype
python3 << 'ENDOFSCRIPT'
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas("samples/pdf2.pdf", pagesize=letter)
c.setTitle("Technical Manual")
c.setAuthor("bob")
c.setSubject("Technical documentation")

c.drawString(100, 750, "Technical Manual")
c.drawString(100, 730, "Author: bob")
c.drawString(100, 710, "Page 1 content")

c.showPage()
c.drawString(100, 750, "Page 2 content")
c.drawString(100, 730, "Additional information")

c.showPage()
c.drawString(100, 750, "Page 3 content")
c.drawString(100, 730, "Final page")

c.save()
print("pdf2.pdf created with 3 pages")
ENDOFSCRIPT
```

### Expected Results:
- **Metadata**: Title, Author, Subject, Page Count = 3
- **Nodes**: 1-2
- **File Node**: Yes
- **Confidence**: High

---

## File 3: pdf3.pdf - Simple PDF

### Create via ReportLab:
```bash
cd /home/karthikean.juttumaha/mini-extract/prototype
python3 << 'ENDOFSCRIPT'
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas("samples/pdf3.pdf", pagesize=letter)
c.setTitle("Simple Document")
c.setAuthor("charlie")

c.drawString(100, 750, "Simple PDF Document")
c.drawString(100, 730, "Basic content for testing")
c.save()
print("pdf3.pdf created")
ENDOFSCRIPT
```

### Expected Results:
- **Nodes**: 1-2
- **Author**: charlie
- **Source**: pdf_metadata
- **Confidence**: High

---

## Install ReportLab (Required for PDF Creation)

```bash
pip install reportlab
```

If you don't want to use ReportLab, you can create the PDFs manually with any PDF editor.

---

## Testing PDF Files

After creating PDF files and extract.py:

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype

# Install PDF dependencies
pip install PyPDF2 pdfplumber

# Test each PDF
python3 extract.py samples/pdf1.pdf --output results/pdf1.json
python3 extract.py samples/pdf2.pdf --output results/pdf2.json
python3 extract.py samples/pdf3.pdf --output results/pdf3.json

# Quick check
python3 extract.py samples/pdf1.pdf --format simple
```

---

## What Extract.py Does with PDFs

The extractor will extract:
- **Title** (from document metadata)
- **Author** (if available)
- **Creation Date** (converted to ISO format)
- **Modification Date** (if different from creation)
- **Page Count**
- **Producer/Creator** (if available)

Output will include:
- Edit nodes for creation and modification (if timestamps differ)
- File node with PDF type
- Knowledge graph showing file -> edit relationships
- High confidence scores

---

## Troubleshooting PDF Extraction

**"PyPDF2 not installed"**:
```bash
pip install PyPDF2
```

**"pdfplumber not installed"**:
```bash
pip install pdfplumber
```

**No metadata extracted**:
- The PDF was created without metadata
- Try creating with ReportLab as shown above
- Or use a proper PDF editor to add metadata
