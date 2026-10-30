# samples4 Directory

## Purpose
This directory contains test files with **known edit histories** for validating the Universal File Metadata & Version History Extractor.

Each file has been edited at **different timestamps** with **specific changes**. The extractor should:
1. Detect each edit as a separate **node** in the knowledge graph
2. Connect nodes with **edges** showing the type of change (addition, deletion, modification)
3. Include **timestamps** for each edit
4. Show **what was changed** (content before/after)

## File Index

### 1. Text Files with Embedded Markers
- [`multi_edit_text.txt`](./text_files/multi_edit_text.txt) - Text file with 5 known edits
- [`multi_edit_text.history.json`](./text_files/multi_edit_text.history.json) - Expected edit history

### 2. Simulated Version History Files
- [`evolution.txt`](./evolution.txt) - File that will be created with multiple git commits
- [`evolution.history.json`](./evolution.history.json) - Expected history from git

## File Formats

### Text File Markers
For text files, edits are marked with special comments:

**Format 1 (Recommended):**
```
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: user1 | TYPE: add | SECTION: introduction -->
This is the first paragraph.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: user2 | TYPE: modify | SECTION: introduction -->
This is the UPDATED first paragraph.

<!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: user1 | TYPE: delete | SECTION: temp -->
This line should be deleted.
```

**Format 2 (YAML-style):**
```
# EDIT:
#   timestamp: 2024-02-02T20:31:00Z
#   author: user1
#   type: add
#   section: introduction
#   description: Initial file creation

This is the first paragraph.
```

### Expected Node Structure
Each edit should create a node with:
```json
{
  "node_id": "unique_id",
  "node_type": "edit",
  "timestamp": "2024-02-02T20:31:00Z",
  "author": "user1",
  "edit_type": "add|delete|modify|create",
  "content_before": null,
  "content_after": "This is the first paragraph.",
  "affected_section": "introduction",
  "description": "Initial file creation",
  "file_version": "1.0",
  "source": "embedded_marker",
  "evaluation_band": "high"
}
```

### Expected Edge Structure
Edges connect edits in temporal sequence:
```json
{
  "edge_id": "edge_001_002",
  "source": "edit_2024-02-02T20:31:00Z_001",
  "target": "edit_2024-02-03T19:29:00Z_002",
  "edge_type": "precursor",
  "relationship": "adds_to|modifies|removes_from",
  "timestamp": "2024-02-03T19:29:00Z",
  "weight": 1.0
}
```

## Validation

To validate the extractor with these files:

```bash
# Test with text file
python extract.py samples4/text_files/multi_edit_text.txt

# Validate against expected history
python validate.py samples4/text_files/multi_edit_text.txt samples4/text_files/multi_edit_text.history.json

# Test with git history (if git repo is set up)
python extract.py --git-repo samples4_git samples4_git/evolution.txt
```

## Creating Test Files

If you need to create additional test files, follow this pattern:

1. **For text files with embedded markers:**
   - Add markers before each edit
   - Use consistent ISO 8601 timestamps
   - Specify author and edit type
   - Create companion .history.json file

2. **For git-based history:**
   - Create a git repository
   - Make commits with `--date` flag to set specific timestamps
   - Each commit = one edit
   - Create .history.json from git log

3. **For Word documents:**
   - Enable Track Changes
   - Make edits with different authors
   - Save after each edit
   - Extract history using python-docx

## Current Status

- [ ] Text files with embedded markers (multi_edit_text.txt)
- [ ] History JSON files for validation
- [ ] Git repository with known commit history
- [ ] Word document with track changes
- [ ] PDF with metadata timestamps
- [ ] Image with EXIF timestamps

## Next Steps

1. Create actual test files in this directory
2. Run extraction on each file
3. Validate knowledge graph output
4. Refine extraction algorithms
5. Add more test cases
