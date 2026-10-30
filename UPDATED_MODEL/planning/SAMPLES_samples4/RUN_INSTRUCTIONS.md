# Complete Run Instructions

## How to Create All Sample Files, Run Extraction, and Reproduce Results

This guide provides **step-by-step instructions** to:
1. Create all 7 sample file types
2. Run the extractor on each file
3. Reproduce the expected output
4. Verify the results

---

## ⚡ Quick Start (5 Minutes)

If you're in a hurry, start with just the **text file** which requires NO special tools:

```bash
# 1. Create the samples4 directory
mkdir -p samples4

# 2. Create a simple text file with embedded markers
cat > samples4/multi_edit_text.txt << 'EOF'
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create | SECTION: header -->
# Report
Initial content.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: bob | TYPE: add | SECTION: intro -->
## Introduction
Added intro.

<!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: alice | TYPE: modify | SECTION: title -->
# Report v1.0
Updated.
EOF

# 3. Save the extraction script
# Copy from EXTRACTION_SCRIPT.md to extract.py

# 4. Run extraction
python extract.py samples4/multi_edit_text.txt

# 5. See results in JSON format
```

---

## 📁 Complete File Creation Guide

### File 1: Text File with Embedded Markers ✅ (Easiest)

**Filename**: `samples4/multi_edit_text.txt`

**Creation** (30 seconds):
```bash
cat > samples4/multi_edit_text.txt << 'EOF'
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create | SECTION: header | DESCRIPTION: Initial document creation -->
# Project Report

This is the initial version of the project documentation.

The project aims to create a universal file metadata extractor.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: bob | TYPE: add | SECTION: introduction | DESCRIPTION: Added introduction section -->
## Introduction

This section provides an overview of the extractor.
The extractor can handle multiple file types.

## Features

- Multi-format support
- Version history tracking

<!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: alice | TYPE: modify | SECTION: title | DESCRIPTION: Updated title to include version -->
# Project Report v1.0

This is the UPDATED version of the project documentation.

## Introduction

This section provides an overview of the extractor.
The extractor can handle multiple file types.

## Features

- Multi-format support
- Version history tracking

<!-- EDIT: 2024-02-04T14:29:00Z | AUTHOR: alice | TYPE: add | SECTION: media | DESCRIPTION: Added media asset references -->
## Media Assets

- Image: logo.png - Added 2024-02-04
- Audio: intro.mp3 - Added 2024-02-04
- Video: tutorial.mp4 - Added 2024-02-04

<!-- EDIT: 2024-02-05T09:00:00Z | AUTHOR: bob | TYPE: add | SECTION: conclusion | DESCRIPTION: Added conclusion section -->
## Conclusion

This documentation covers all project assets and features.
EOF
```

**Verification**:
```bash
# Should show 5 markers
grep -c "EDIT:" samples4/multi_edit_text.txt
```

**Extraction Command**:
```bash
python extract.py samples4/multi_edit_text.txt --output results/multi_edit_text.json
```

**Expected Results**:
- 5 edit nodes
- 4 edges connecting them
- All timestamps present (2024-02-02 to 2024-02-05)
- Authors: alice, bob
- Edit types: create, add, modify, add
- All confidence: high

---

### File 2: Word Document with Track Changes

**Filename**: `samples4/tracked_changes.docx`

**Prerequisite**: Microsoft Word or LibreOffice Writer

**Creation Steps** (5 minutes):

1. **Open Word** and create a new document

2. **Enable Track Changes**:
   - Go to **Review** tab
   - Click **Track Changes** (ensure it's ON)

3. **Make edits with timestamps**:
   ```
   # Step 1: Initial content
   Type: "Project Report"
   Type: "This is the initial content."
   SAVE the document
   
   # Step 2: Add image reference (simulating image insertion)
   After "initial content.", add: "Image 1 inserted here."
   SAVE
   
   # Step 3: Add another image
   At the end, add: "Image 2 inserted here."
   SAVE
   
   # Step 4: Modify title
   Change "Project Report" to "Project Report v1.0"
   SAVE
   ```

4. **Save as DOCX**:
   - File → Save As
   - Filename: `tracked_changes.docx`
   - Location: `samples4/`
   - Format: Word Document (.docx)

**Extraction Command**:
```bash
python extract.py samples4/tracked_changes.docx --output results/tracked_changes.json
```

**Expected Results**:
- 4 edit nodes (initial, add image1, add image2, modify title)
- 3 edges
- Timestamps from Word's revision history
- Author names from Word
- Source: word_track_changes (when implemented) or filesystem (basic version)

**Note**: The basic extraction script in EXTRACTION_SCRIPT.md uses filesystem fallback for Word docs. For full Word track changes support, additional code is needed (see artifacts/version_history_extractor.md).

---

### File 3: PDF with Metadata

**Filename**: `samples4/metadata.pdf`

**Prerequisite**: Any PDF creator (Word, LibreOffice, online tool)

**Creation Steps** (3 minutes):

1. **Create a Word document** with content:
   ```
   PDF Test Document
   
   This PDF has embedded metadata.
   Created: 2024-02-01
   Modified: 2024-02-02
   Author: Test User
   ```

2. **Add document properties**:
   - File → Info (or File → Properties)
   - Title: "Metadata Test Document"
   - Author: "PDF Test User"
   - Subject: "Testing PDF metadata extraction"
   - Created: 2024-02-01T08:00:00Z
   - Modified: 2024-02-02T09:00:00Z

3. **Export as PDF**:
   - File → Export → Create PDF/XPS
   - Filename: `metadata.pdf`
   - Location: `samples4/`

**Extraction Command**:
```bash
python extract.py samples4/metadata.pdf --output results/metadata.json
```

**Expected Results** (Basic version):
- 1 node (filesystem metadata)
- 0 edges
- Timestamp: Last modified time
- Source: filesystem
- Confidence: low

**Expected Results** (Full version with PyPDF2):
- 1 node with PDF author, creator, timestamps
- Source: pdf_metadata
- Confidence: high

---

### File 4: Image with EXIF Metadata

**Filename**: `samples4/exif_image.jpg`

**Prerequisite**: Digital camera or phone

**Creation Steps** (Easiest - 1 minute):

**Option A: Use your phone**
1. Open your phone's camera
2. Take a photo
3. Transfer to computer (email, cable, cloud)
4. Rename to `exif_image.jpg`
5. Place in `samples4/`

**Option B: Use a phone camera app**
- Most camera apps automatically embed EXIF data with timestamps

**Option C: Use online EXIF editor**
1. Go to https://exif.tools/
2. Upload any image
3. Edit EXIF data:
   - DateTimeOriginal: 2024-02-03T10:00:00Z
   - DateTimeDigitized: 2024-02-03T10:00:00Z
   - Artist: Test Photographer
   - Copyright: Test Image
4. Download and save as `exif_image.jpg`

**Extraction Command**:
```bash
python extract.py samples4/exif_image.jpg --output results/exif_image.json
```

**Expected Results** (Basic version):
- 1 node (filesystem metadata)
- 0 edges
- Timestamp: Last modified time
- Source: filesystem
- Confidence: low

**Expected Results** (Full version with Pillow):
- 1 node with EXIF timestamps (DateTimeOriginal, DateTimeDigitized)
- Source: exif_metadata
- Confidence: high

---

### File 5: Audio File with ID3 Tags

**Filename**: `samples4/sample_audio.mp3`

**Prerequisite**: Audio recording device or converter

**Creation Steps** (2 minutes):

**Option A: Record on phone**
1. Use voice recorder app
2. Record 10-30 seconds of audio
3. Transfer to computer
4. Rename to `sample_audio.mp3`
5. Place in `samples4/`

**Option B: Use online audio recorder**
1. Go to https://vocaroo.com/
2. Click "Click to Record"
3. Record a short message
4. Click "Save" → Download
5. Rename to `sample_audio.mp3`
6. Place in `samples4/`

**Option C: Convert existing audio**
```bash
# If you have any audio file (WAV, M4A, etc.)
ffmpeg -i input.wav -c:a libmp3lame -q:a 2 samples4/sample_audio.mp3
```

**Extraction Command**:
```bash
python extract.py samples4/sample_audio.mp3 --output results/sample_audio.json
```

**Expected Results** (Basic version):
- 1 node (filesystem metadata)
- 0 edges
- Timestamp: Last modified time
- Source: filesystem
- Confidence: low

**Expected Results** (Full version with pydub/mutagen):
- 1 node with audio metadata (duration, bitrate, channels)
- Source: audio_metadata
- Confidence: medium

---

### File 6: Video File with Metadata

**Filename**: `samples4/sample_video.mp4`

**Prerequisite**: Video recording device or converter

**Creation Steps** (1 minute):

**Option A: Record on phone**
1. Use phone's video camera
2. Record 5-10 seconds
3. Transfer to computer
4. Rename to `sample_video.mp4`
5. Place in `samples4/`

**Option B: Use online video recorder**
1. Go to https://record screen.io/
2. Record a short video
3. Download
4. Rename to `sample_video.mp4`
5. Place in `samples4/`

**Option C: Convert existing video**
```bash
# If you have any video file
ffmpeg -i input.avi -c:v libx264 -c:a aac samples4/sample_video.mp4
```

**Extraction Command**:
```bash
python extract.py samples4/sample_video.mp4 --output results/sample_video.json
```

**Expected Results** (Basic version):
- 1 node (filesystem metadata)
- 0 edges
- Timestamp: Last modified time
- Source: filesystem
- Confidence: low

**Expected Results** (Full version with OpenCV):
- 1 node with video metadata (duration, resolution, frames, fps)
- Source: video_metadata
- Confidence: medium

---

### File 7: Git Repository with Version History

**Filename**: `samples4/evolution.txt` in a git repo at `samples4_git/`

**Prerequisite**: Git installed

**Creation Steps** (5 minutes):

```bash
# Navigate to samples4
cd samples4

# Create a git repository for version history
mkdir samples4_git
cd samples4_git
git init

# Set up author info
git config user.name "Test User"
git config user.email "test@example.com"

# Create initial file with first commit (2024-02-01 08:00)
echo "Initial content" > evolution.txt
git add evolution.txt
git commit -m "Initial commit" --date="2024-02-01T08:00:00Z"

# Second commit (2024-02-02 09:00) - Add section 1
echo -e "Initial content\n\nAdded section 1" > evolution.txt
git add evolution.txt
git commit -m "Add section 1" --date="2024-02-02T09:00:00Z" --author="Alice <alice@example.com>"

# Third commit (2024-02-03 10:00) - Modify section 1
echo -e "Initial content\n\nModified section 1\n\nAdded section 2" > evolution.txt
git add evolution.txt
git commit -m "Modify section 1, add section 2" --date="2024-02-03T10:00:00Z" --author="Bob <bob@example.com>"

# Fourth commit (2024-02-04 11:00) - Delete section 1
 echo -e "Initial content\n\nModified section 1\n\nAdded section 2" > evolution.txt
git add evolution.txt
git commit -m "Remove temp note" --date="2024-02-04T11:00:00Z" --author="Alice <alice@example.com>"

# Go back to project root
cd ..
```

**Extraction Command**:
```bash
python extract.py samples4/evolution.txt --git-repo samples4/samples4_git --output results/evolution.json
```

**Expected Results** (Basic version):
- 1 node (filesystem metadata only - git integration not in basic version)
- 0 edges
- Source: filesystem

**Expected Results** (Full version with GitPython):
- 4 nodes (one per commit)
- 3 edges
- Timestamps: 2024-02-01T08:00:00Z to 2024-02-04T11:00:00Z
- Authors: Test User, Alice, Bob
- Edit types: create, add, modify, delete
- Source: git
- Confidence: high

---

## 📊 Expected Results Summary Table

| File | Edits/Nodes | Edges | Timestamps | Author | Confidence | Source (Basic) | Source (Full) |
|------|-------------|-------|------------|--------|------------|----------------|---------------|
| Text with markers | 5 | 4 | ✅ Exact | ✅ Multi | High | embedded_marker | embedded_marker |
| Word with track changes | 4 | 3 | ⚠️ File-level | ⚠️ Limited | Low | filesystem | word_track_changes |
| PDF with metadata | 1 | 0 | ✅ File-level | ⚠️ Limited | Low | filesystem | pdf_metadata |
| Image with EXIF | 1 | 0 | ✅ File-level | ❌ No | Low | filesystem | exif_metadata |
| Audio MP3 | 1 | 0 | ✅ File-level | ❌ No | Low | filesystem | audio_metadata |
| Video MP4 | 1 | 0 | ✅ File-level | ❌ No | Low | filesystem | video_metadata |
| Git version history | 4 | 3 | ✅ Commit | ✅ Multi | High | filesystem | git |

---

## 🎯 Complete Workflow

### Step 1: Create Directory Structure

```bash
# From project root
mkdir -p samples4 results
```

### Step 2: Create Sample Files

Follow the instructions above for each file type you want to create.

**Minimum recommended**: Start with just `multi_edit_text.txt`

**For full testing**: Create all 7 files

### Step 3: Save Extraction Script

Copy the content from `EXTRACTION_SCRIPT.md` to `extract.py`:

```bash
cp samples4/EXTRACTION_SCRIPT.md extract.py.short
# Then manually copy the Python code from EXTRACTION_SCRIPT.md to extract.py
```

Or use sed to extract just the code:
```bash
# Extract Python code from markdown (partial solution)
# Then manually clean up
```

### Step 4: Install Dependencies

```bash
# Minimum for basic functionality
pip install python-magic

# For full functionality (if implementing all extractors)
pip install Pillow PyPDF2 pdfplumber python-docx openpyxl pydub networkx gitpython
```

### Step 5: Run Extraction on All Files

```bash
# Create a run script
cat > run_extraction.sh << 'EOF'
#!/bin/bash

# Create results directory
mkdir -p results

# Run on all sample files
echo "=== Extracting: multi_edit_text.txt ==="
python extract.py samples4/multi_edit_text.txt --output results/multi_edit_text.json

echo ""
echo "=== Extracting: tracked_changes.docx ==="
python extract.py samples4/tracked_changes.docx --output results/tracked_changes.json

echo ""
echo "=== Extracting: metadata.pdf ==="
python extract.py samples4/metadata.pdf --output results/metadata.json

echo ""
echo "=== Extracting: exif_image.jpg ==="
python extract.py samples4/exif_image.jpg --output results/exif_image.json

echo ""
echo "=== Extracting: sample_audio.mp3 ==="
python extract.py samples4/sample_audio.mp3 --output results/sample_audio.json

echo ""
echo "=== Extracting: sample_video.mp4 ==="
python extract.py samples4/sample_video.mp4 --output results/sample_video.json

echo ""
echo "=== Extracting: evolution.txt (git) ==="
python extract.py samples4_git/evolution.txt --git-repo samples4_git --output results/evolution.json

echo ""
echo "All extractions complete!"
EOF

chmod +x run_extraction.sh

# Run it
./run_extraction.sh
```

### Step 6: Review Results

```bash
# List all result files
ls -lh results/

# View a specific result
echo "=== Text File Results ==="
cat results/multi_edit_text.json | python -m json.tool | head -50

echo ""
echo "=== Summary for all files ==="
for file in results/*.json; do
    echo "File: $file"
    python -c "import json; d=json.load(open('$file')); print(f'  Nodes: {d[\"knowledge_graph\"][\"total_nodes\"]}, Edges: {d[\"knowledge_graph\"][\"total_edges\"]}')"
done
```

---

## 📋 Sample Output (Text File)

For `multi_edit_text.txt`, expected output:

```json
{
  "extraction_metadata": {
    "file": "samples4/multi_edit_text.txt",
    "timestamp": "2026-10-05T12:34:56Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": 1234,
      "created_time": "2026-10-05T12:30:00Z",
      "modified_time": "2026-10-05T12:30:00Z",
      "accessed_time": "2026-10-05T12:34:56Z"
    },
    "file_type": "text/plain",
    "text": {
      "character_count": 1234,
      "line_count": 45,
      "word_count": 200
    }
  },
  "version_history": {
    "edits": [
      {
        "node_id": "edit_20240202T203100Z_0",
        "node_type": "edit",
        "timestamp": "2024-02-02T20:31:00Z",
        "author": "alice",
        "edit_type": "create",
        "content_after": "# Project Report\n\nThis is the initial version...",
        "source": "embedded_marker",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_20240203T192900Z_1",
        "node_type": "edit",
        "timestamp": "2024-02-03T19:29:00Z",
        "author": "bob",
        "edit_type": "add",
        "content_after": "## Introduction\n\nThis section provides...",
        "source": "embedded_marker",
        "evaluation_band": "high"
      }
    ],
    "edit_count": 5
  },
  "knowledge_graph": {
    "nodes": 5,
    "edges": 4,
    "total_nodes": 5,
    "total_edges": 4
  },
  "summary": {
    "total_edits": 5,
    "total_nodes": 5,
    "total_edges": 4,
    "sources_used": ["embedded_marker"],
    "confidence_distribution": {"high": 5, "medium": 0, "low": 0}
  }
}
```

---

## ⚠️ Known Limitations (Basic Version)

The basic extraction script from `EXTRACTION_SCRIPT.md` has these limitations:

1. **Only text files with markers** get full edit history
2. **Binary files** (Word, PDF, images, audio, video) only get filesystem metadata
3. **No git integration** in basic version
4. **No Word track changes** parsing in basic version

### How to Fix:

For **full functionality**, you need to:

1. **Install additional dependencies**:
   ```bash
   pip install Pillow PyPDF2 pdfplumber python-docx openpyxl pydub networkx gitpython lxml
   ```

2. **Implement additional extractors** (code is templated in):
   - `artifacts/extraction_engine.md` - Full extraction engine
   - `artifacts/version_history_extractor.md` - Version history extractor
   - `artifacts/main_extractor.md` - Complete main extractor

3. **Merge the full code** into `extract.py`

---

## 🎉 Success Criteria

You've successfully reproduced the results when:

| File | Success Criteria |
|------|------------------|
| Text | 5 nodes, 4 edges, all timestamps correct |
| Word | File exists and can be read (even if basic) |
| PDF | File exists and can be read |
| Image | File exists and can be read |
| Audio | File exists and can be read |
| Video | File exists and can be read |
| Git | File exists and git repo has history |

---

## 📚 Full Documentation

For complete details on each component:

- **Project Overview**: [../README.md](../README.md)
- **Proposal**: [../artifacts/proposal.md](../artifacts/proposal.md)
- **Specifications**: [../artifacts/specs.md](../artifacts/specs.md)
- **Quick Start**: [../QUICKSTART.md](../QUICKSTART.md)
- **Implementation Roadmap**: [../artifacts/IMPLEMENTATION_ROADMAP.md](../artifacts/IMPLEMENTATION_ROADMAP.md)
- **Full Extraction Engine**: [../artifacts/extraction_engine.md](../artifacts/extraction_engine.md)

---

## 🚀 Reproduction Instructions Summary

1. **Create directory**: `mkdir -p samples4 results`
2. **Create text file**: `cat > samples4/multi_edit_text.txt << 'EOF'...`
3. **Save extract.py**: Copy from `EXTRACTION_SCRIPT.md`
4. **Install dependencies**: `pip install python-magic`
5. **Run**: `python extract.py samples4/multi_edit_text.txt`
6. **Verify**: Check JSON output has 5 nodes, 4 edges
7. **Expand**: Add more file types as needed

---

## 🎯 Final Notes

- **Start simple**: Text file with embedded markers is the easiest
- **Build gradually**: Add one file type at a time
- **Verify at each step**: Make sure each file works before adding more
- **Use the templates**: The full code is in `artifacts/` directory

**The text file example should work immediately with the basic script. This gives you a working proof of concept.**
