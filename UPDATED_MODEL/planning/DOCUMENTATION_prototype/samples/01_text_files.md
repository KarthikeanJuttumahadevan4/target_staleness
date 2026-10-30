---
format: html
---

# Text File Samples (3 files)

Use these commands to create the 3 text sample files for testing.

---

## File 1: text1.txt - Basic document with 3 edits

### Create Command:
```bash
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
```

### Expected Results:
- **Edits**: 3
- **Nodes**: 3 + 1 file node = 4 total
- **Edges**: 3
- **Authors**: alice (2), bob (1)
- **Confidence**: All high

---

## File 2: text2.txt - Multi-section document with 5 edits

### Create Command:
```bash
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
```

### Expected Results:
- **Edits**: 5
- **Nodes**: 5 + 1 file node = 6 total
- **Edges**: 5
- **Authors**: charlie (3), diana (2)
- **Moving Part**: Includes a delete operation
- **Confidence**: All high

---

## File 3: text3.txt - Document with image reference

### Create Command:
```bash
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
```

### Expected Results:
- **Edits**: 3
- **Nodes**: 3 + 1 file node = 4 total
- **Edges**: 3
- **Authors**: eve (2), frank (1)
- **Features**: Contains image reference
- **Confidence**: All high

---

## All Text Files - Quick Create Command

Run this single command to create all 3 text files:

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype

# Create file 1
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

# Create file 2
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

# Create file 3
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

echo "All 3 text files created successfully in samples/"
```

---

## Testing All Text Files

After creating the files and extract.py, test with:

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype

# Test each text file
python3 extract.py samples/text1.txt --output results/text1.json
python3 extract.py samples/text2.txt --output results/text2.json
python3 extract.py samples/text3.txt --output results/text3.json

# Or test all at once
for file in samples/text*.txt; do
  echo "Processing: $file"
  python3 extract.py "$file" --output "results/$(basename $file .txt).json"
  echo "---"
done
```
