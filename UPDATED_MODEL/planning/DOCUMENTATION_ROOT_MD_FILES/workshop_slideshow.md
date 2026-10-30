% Universal File Metadata & Version History Extractor
% Workshop Slideshow
%!

---

# Universal File Metadata & Version History Extractor

### The BIG Picture

**Building a system that can:**
- Extract maximum metadata from ANY file type
- Track ALL historical changes to files
- Build knowledge graphs of file evolution
- Assign confidence scores to extracted data

---

# Slide 1: The Problem

## What Problem Does This Solve?

---

**Current State:**
- File metadata is scattered across systems
- Edit history is lost or fragmented
- No unified view of file evolution
- Difficult to track who changed what and when

**The Solution:**
One system to extract, track, and visualize ALL file changes automatically

---

# Slide 2: How It Works

## The Flow Pipeline

```
1. INGESTION
   Detect file type and validate
   
2. MULTI-MODEL EXTRACTION
   Multiple methods per file type:
   - Embedded markers (text)
   - Git history
   - Word track changes XML
   - PDF metadata
   - EXIF (images)
   - Filesystem fallback
   
3. VERSION ANALYSIS
   Extract edit history from all sources
   
4. KNOWLEDGE GRAPH
   Build graph of changes and relationships
   
5. EVALUATION
   Assign confidence bands (high/medium/low)
   
6. OUTPUT
   JSON, GraphML, GEXF formats
```

---

# Slide 3: What We Built

## Prototype Structure

```
mini-extract/
├── prototype/
│   ├── README.md                    # Main documentation
│   ├── EXTRACTION_SCRIPT.md         # Python code template
│   ├── RUN_INSTRUCTIONS.md          # How to run it
│   ├── RESULTS.md                   # Expected outputs
│   └── samples/                    # Test files
│       └── test.txt.md            # Sample template
│
└── workshop_slideshow.md          # This file
```

## Key Features

- **Universal**: Works with ANY file type
- **Version History**: Tracks all edits with timestamps and authors
- **Knowledge Graph**: Builds graph of file evolution
- **Confidence Scoring**: High/Medium/Low evaluation bands

---

# Slide 4: What We Have Now

## Complete in Prototype Folder

---

- Full technical proposal and specifications
- Complete Python extraction script template
- Step-by-step run instructions
- Expected results documentation
- Sample test files with embedded markers

## How to Use It

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype

# Create extract.py from template
python3 -c "import re; print(''.join(re.findall(r'```python\n(.*?)```', open('EXTRACTION_SCRIPT.md').read(), re.DOTALL)))" > extract.py

# Create test file
cat > samples/test.txt << 'EOF'
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create -->
# Document
...
EOF

# Run extraction
python3 extract.py samples/test.txt --output results/output.json
```

---

# Slide 5: Next Steps

## Immediate Actions

---

1. **YOU create** the actual files:
   - `prototype/extract.py` (from template)
   - `prototype/samples/test.txt` (from .md template)

2. **Install dependencies:**
   ```bash
   pip install Pillow PyPDF2 python-docx networkx python-magic
   ```

3. **Run the prototype:**
   ```bash
   cd prototype
   python3 extract.py samples/test.txt
   ```

## Long-Term Vision

- Extend to all file types
- Add more extraction methods per file type
- Build visualization dashboard
- Create automated testing
- Deploy as service

---

## Summary

---

**We designed a system to:**
- Automatically extract metadata from ANY file
- Track complete version history
- Build knowledge graphs
- ascribed with evaluation bands

**You need to:**
1. Run the commands to create `extract.py`
2. Create test files
3. Run the prototype

**Questions?** Check the prototype/README.md for details
