# Run Instructions

## Quick Start (30 Seconds)

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype

# Create samples directory and test file
mkdir -p samples results
cat > samples/test.txt << 'EOF'
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create -->
# Document
Initial content

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: bob | TYPE: add -->
Content added
EOF

# Create extract.py from template
python3 -c "
import re
with open('EXTRACTION_SCRIPT.md', 'r') as f:
    content = f.read()
code = re.search(r'```python(.*?)```', content, re.DOTALL)
if code:
    with open('extract.py', 'w') as f:
        f.write(code.group(1))
"

# Run extraction
python3 extract.py samples/test.txt --output results/output.json

# View results
cat results/output.json
```

---

## Detailed Instructions

### Step 1: Create extract.py

Extract the Python code from the EXTRACTION_SCRIPT.md template:

**Method A: Using Python (recommended)**
```bash
python3 -c "
import re
with open('EXTRACTION_SCRIPT.md', 'r') as f:
    content = f.read()
code = re.search(r'```python(.*?)```', content, re.DOTALL)
if code:
    with open('extract.py', 'w') as f:
        f.write(code.group(1))
print('extract.py created successfully')
"
```

**Method B: Manual copy (if Python fails)**
1. Open `EXTRACTION_SCRIPT.md` in a text editor
2. Find the section starting with ` ```python ` and ending with ` ``` `
3. Copy everything between those markers
4. Paste into a new file named `extract.py`
5. Save the file

**Verify it was created:**
```bash
ls -la extract.py
diff <(head -n 1 EXTRACTION_SCRIPT.md | grep -oP '(?<=```python).*' | head -c 100) <(head -n 1 extract.py | head -c 100)
```

---

### Step 2: Create Sample Files

You need at least one sample file to test with.

**Option 1: Minimal test file**
```bash
cat > samples/test.txt << 'EOF'
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create -->
# Test Document
First line

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: bob | TYPE: add -->
Second line added
EOF
```

**Option 2: Full test file (from samples/README.md)**
```bash
cat > samples/test.txt << 'EOF'
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create -->
# Report
Initial content.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: bob | TYPE: add -->
## Introduction
Added introduction section.

<!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: alice | TYPE: modify -->
## Revised Introduction
Updated the introduction with more details.
EOF
```

---

### Step 3: Create Results Directory

The extractor needs a place to save output:

```bash
mkdir -p results
```

---

### Step 4: Run the Extractor

**Basic usage:**
```bash
python3 extract.py samples/test.txt
```

**With output file:**
```bash
python3 extract.py samples/test.txt --output results/output.json
```

**With all options:**
```bash
python3 extract.py samples/test.txt \
  --git-repo . \
  --output-format json \
  --output results/output.json \
  --verbose
```

---

### Step 5: View Results

```bash
cat results/output.json
```

Or pretty print:
```bash
python3 -m json.tool results/output.json
```

---

## Command Reference

### Basic Commands

| Command | Description |
|---------|-------------|
| `python3 extract.py <file>` | Extract and print to stdout |
| `python3 extract.py <file> --output results/output.json` | Save to JSON file |
| `python3 extract.py <file> --output-format graphml > output.graphml` | Get GraphML output |
| `python3 extract.py <file> --output-format gexf > output.gexf` | Get GEXF output |

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-h, --help` | Show help message | |
| `--git-repo GIT_REPO` | Git repository path | None |
| `--output-format {json,graphml,gexf}` | Output format | json |
| `--output O` | Output file path | stdout |
| `--verbose, -v` | Verbose logging | Off |

---

## Testing Different File Types

### Text Files (Recommended for First Test)

```bash
# Text with embedded markers
python3 extract.py samples/test.txt --output results/text.json

# Plain text without markers
python3 extract.py samples/plain.txt --output results/plain.json
```

### Word Documents (requires python-docx)

```bash
# Install dependency
pip install python-docx

# Create a Word document with track changes
# Save as samples/test.docx

# Process it
python3 extract.py samples/test.docx --output results/word.json
```

**Note:** The extraction script needs the Word track changes XML to extract version history from .docx files.

### PDF Files (requires PyPDF2)

```bash
# Install dependency
pip install PyPDF2

# Process a PDF
python3 extract.py samples/test.pdf --output results/pdf.json
```

**Note:** PDF extraction gets document metadata, not version history.

### Image Files (requires Pillow)

```bash
# Install dependency
pip install Pillow

# Process an image
python3 extract.py samples/test.png --output results/image.json
```

**Note:** Image extraction gets EXIF metadata including timestamps.

### Multiple Files

Process multiple files with a simple loop:

```bash
for file in samples/*.txt; do
  python3 extract.py "$file" --output "results/$(basename $file .txt).json"
done
```

---

## Troubleshooting

### "No module named..." Errors

Install missing dependencies:

```bash
pip install Pillow PyPDF2 python-docx openpyxl networkx python-magic
```

### extract.py not found

Make sure you're in the right directory:
```bash
cd /home/karthikean.juttumaha/mini-extract/prototype
ls -la extract.py  # Should see the file
```

### File not found

Check the file exists and path is correct:
```bash
ls -la samples/test.txt  # Should see the file
python3 extract.py samples/test.txt  # Use relative path
# OR
python3 extract.py /home/karthikean.juttumaha/mini-extract/prototype/samples/test.txt  # Full path
```

### JSON parsing errors

The output might be too large for your terminal. Use:
```bash
python3 extract.py samples/test.txt > results/output.json
# Then view with
cat results/output.json | python3 -m json.tool
```

---

## Verifying Results

Check the JSON output for these key elements:

```bash
# Count edits
python3 -c "import json; data = json.load(open('results/output.json')); print(f'Edit count: {len(data[\"version_history\"][\"edits\"])}')"

# Count knowledge graph nodes and edges
python3 -c "import json; data = json.load(open('results/output.json')); kg = data['knowledge_graph']; print(f'Nodes: {kg[\"total_nodes\"]}, Edges: {kg[\"total_edges\"]}')"

# Check confidence distribution
python3 -c "import json; data = json.load(open('results/output.json')); print(data['summary']['confidence_distribution'])"
```

---

## Expected vs Actual Results

| Test File | Expected Nodes | Expected Edges | Expected Confidence |
|-----------|----------------|----------------|---------------------|
| samples/test.txt | 3 | 2 | All high |
| samples/plain.txt | 1 | 0 | Low |
| samples/multi.txt | 5 | 4 | All high |

If your results don't match expected values, check:
1. File content is correct
2. File path is correct
3. extract.py was created correctly from template
4. No typos in marker syntax
