---
format: html
---

# Excel File Samples (3 files)

Use these commands to create the 3 Excel sample files for testing.

---

## Important Note

You **can** create Excel files directly with Python using openpyxl.

---

##File 1: excel1.xlsx - Basic workbook with metadata

### Create Command:
```bash
cd /home/karthikean.juttumaha/mini-extract/prototype
python3 << 'ENDOFSCRIPT'
import openpyxl
from openpyxl import Workbook
from datetime import datetime

# Create workbook
wb = Workbook()
ws = wb.active
ws.title = "Sheet1"

# Add data
ws['A1'] = 'Product'
ws['B1'] = 'Quantity'
ws['C1'] = 'Price'
ws['A2'] = 'Widget A'
ws['B2'] = 100
ws['C2'] = 29.99
ws['A3'] = 'Widget B'
ws['B3'] = 200
ws['C3'] = 49.99

# Add metadata
wb.properties.author = "alice"
wb.properties.title = "Sales Data Q1"
wb.properties.subject = "Quarterly sales report"
wb.properties.created = datetime(2024, 1, 1, 9, 0, 0)
wb.properties.modified = datetime(2024, 1, 1, 9, 0, 0)

# Save
wb.save("samples/excel1.xlsx")
print("excel1.xlsx created successfully")
ENDOFSCRIPT
```

### Expected Results:
- **Nodes**: 1 (creation) + 1 file node = 2 total
- **Author**: alice
- **Title**: Sales Data Q1
- **Sheets**: Sheet1
- **Source**: excel
- **Confidence**: High

---

## File 2: excel2.xlsx - Multi-sheet workbook

### Create Command:
```bash
cd /home/karthikean.juttumaha/mini-extract/prototype
python3 << 'ENDOFSCRIPT'
import openpyxl
from openpyxl import Workbook
from datetime import datetime, timedelta

# Create workbook
wb = Workbook()

# Remove default sheet
wb.remove(wb.active)

# Sheet 1: Data
ws1 = wb.create_sheet("Data")
ws1['A1'] = 'Name'
ws1['B1'] = 'Value'
ws1['A2'] = 'Item 1'
ws1['B2'] = 100
ws1['A3'] = 'Item 2'
ws1['B3'] = 200

# Sheet 2: Summary  
ws2 = wb.create_sheet("Summary")
ws2['A1'] = 'Total'
ws2['B1'] = 300

# Sheet 3: Charts
ws3 = wb.create_sheet("Charts")
ws3['A1'] = 'Will be used for charts'

# Metadata
wb.properties.author = "bob"
wb.properties.title = "Monthly Report"
wb.properties.subject = "Monthly financial data"
wb.properties.created = datetime(2024, 1, 15, 10, 0, 0)
wb.properties.modified = datetime(2024, 1, 15, 10, 0, 0)

# Save
wb.save("samples/excel2.xlsx")
print("excel2.xlsx created with 3 sheets")
ENDOFSCRIPT
```

### Expected Results:
- **Nodes**: 1 + 1 file node = 2 total
- **Sheets**: Data, Summary, Charts (3 sheets)
- **Author**: bob
- **Source**: excel
- **Confidence**: High

---

## File 3: excel3.xlsx - Modified workbook

### Create Command:
```bash
cd /home/karthikean.juttumaha/mini-extract/prototype
python3 << 'ENDOFSCRIPT'
import openpyxl
from openpyxl import Workbook
from datetime import datetime, timedelta

# Create workbook with modification  
wb = Workbook()
ws = wb.active
ws.title = "Data"

ws['A1'] = 'Name'
ws['B1'] = 'Status'
ws['A2'] = 'Project A'
ws['B2'] = 'Complete'

# Set creation date
wb.properties.author = "charlie"
wb.properties.title = "Project Tracker"
wb.properties.subject = "Project status tracking"
wb.properties.created = datetime(2024, 1, 10, 8, 0, 0)
# Set modification to 1 day later
wb.properties.modified = datetime(2024, 1, 11, 10, 30, 0)

wb.save("samples/excel3.xlsx")
print("excel3.xlsx created with different create/modify dates")
ENDOFSCRIPT
```

### Expected Results:
- **Nodes**: 2 (creation + modification) + 1 file node = 3 total
- **Edges**: 1 (creation -> modification)
- **Creation**: 2024-01-10T08:00:00Z
- **Modification**: 2024-01-11T10:30:00Z
- **Author**: charlie
- **Source**: excel
- **Confidence**: High

---

## Install openpyxl (Required)

```bash
pip install openpyxl
```

---

## Testing Excel Files

After creating Excel files and extract.py:

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype

# Test each Excel file
python3 extract.py samples/excel1.xlsx --output results/excel1.json
python3 extract.py samples/excel2.xlsx --output results/excel2.json
python3 extract.py samples/excel3.xlsx --output results/excel3.json

# Quick check
python3 extract.py samples/excel1.xlsx --format simple
```

---

## What Extract.py Does with Excel Files

The extractor will extract:
- **Author** (workbook properties)
- **Title** (if set)
- **Subject** (if set)
- **Creation Date**
- **Modification Date**
- **Sheet Count** (number of sheets)
- **Sheet Names** (list of all sheet names)

Output will include:
- Edit nodes for creation and modification (if timestamps differ)
- File node with Excel type
- Knowledge graph showing file -> edit relationships
- High confidence scores
- Each edit node contains metadata with sheet information

---

## All Excel Files - Quick Create Command

Run this single command to create all 3 Excel files:

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype

# Install dependency
pip install openpyxl 2>/dev/null

# Create excel1.xlsx
python3 << 'ENDOFSCRIPT'
import openpyxl
from openpyxl import Workbook
from datetime import datetime

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
wb.properties.subject = "Quarterly sales report"
wb.properties.created = datetime(2024, 1, 1, 9, 0, 0)
wb.properties.modified = datetime(2024, 1, 1, 9, 0, 0)
wb.save("samples/excel1.xlsx")
print("excel1.xlsx created")
ENDOFSCRIPT

# Create excel2.xlsx
python3 << 'ENDOFSCRIPT'
import openpyxl
from openpyxl import Workbook
from datetime import datetime

wb = Workbook()
wb.remove(wb.active)
ws1 = wb.create_sheet("Data")
ws1['A1'] = 'Name'
ws1['B1'] = 'Value'
ws1['A2'] = 'Item 1'
ws1['B2'] = 100
ws2 = wb.create_sheet("Summary")
ws2['A1'] = 'Total'
ws2['B1'] = 300
ws3 = wb.create_sheet("Charts")
wb.properties.author = "bob"
wb.properties.title = "Monthly Report"
wb.properties.subject = "Monthly financial data"
wb.properties.created = datetime(2024, 1, 15, 10, 0, 0)
wb.properties.modified = datetime(2024, 1, 15, 10, 0, 0)
wb.save("samples/excel2.xlsx")
print("excel2.xlsx created")
ENDOFSCRIPT

# Create excel3.xlsx
python3 << 'ENDOFSCRIPT'
import openpyxl
from openpyxl import Workbook
from datetime import datetime

wb = Workbook()
ws = wb.active
ws.title = "Data"
ws['A1'] = 'Name'
ws['B1'] = 'Status'
ws['A2'] = 'Project A'
ws['B2'] = 'Complete'
wb.properties.author = "charlie"
wb.properties.title = "Project Tracker"
wb.properties.subject = "Project status tracking"
wb.properties.created = datetime(2024, 1, 10, 8, 0, 0)
wb.properties.modified = datetime(2024, 1, 11, 10, 30, 0)
wb.save("samples/excel3.xlsx")
print("excel3.xlsx created")
ENDOFSCRIPT

echo "All 3 Excel files created successfully in samples/"
```

---

## Testing All 3 File Types Together

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype

# Install all dependencies
pip install openpyxl PyPDF2 pdfplumber reportlab

# Create all samples
# (Run all the create commands from this file and 01_text_files.md, 02_pdf_files.md)

# Test all files
for file in samples/text*.txt samples/pdf*.pdf samples/excel*.xlsx; do
  echo "========================================"
  echo "Testing: $file"
  echo "========================================"
  python3 extract.py "$file" --format simple
  echo ""
done
```

---

## Expected Output Summary

| File | Type | Expected Nodes | Expected Edges | Source | Confidence |
|------|------|----------------|----------------|--------|------------|
| text1.txt | Text | 4 | 3 | embedded_marker | High |
| text2.txt | Text | 6 | 5 | embedded_marker | High |
| text3.txt | Text | 4 | 3 | embedded_marker | High |
| pdf1.pdf | PDF | 2 | 1 | pdf_metadata | High |
| pdf2.pdf | PDF | 2 | 1 | pdf_metadata | High |
| pdf3.pdf | PDF | 2 | 1 | pdf_metadata | High |
| excel1.xlsx | Excel | 2 | 1 | excel | High |
| excel2.xlsx | Excel | 2 | 1 | excel | High |
| excel3.xlsx | Excel | 3 | 1 | excel | High |

Total: **22-24 nodes**, **16-17 edges**
