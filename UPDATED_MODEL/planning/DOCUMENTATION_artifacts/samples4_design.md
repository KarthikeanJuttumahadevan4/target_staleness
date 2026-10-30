# samples4 Directory Design

## Purpose
The `samples4` directory contains test files with **known edit histories** for validating the Universal File Metadata & Version History Extractor.

Each file has been edited at **different timestamps** with **specific changes** that should be detected and represented as **separate nodes** in the knowledge graph, connected by **edges** showing the type of change (addition, deletion, modification).

## Directory Structure

```
samples4/
├── text_files/
│   ├── multi_edit_text.txt          # Text file with 5+ edits at different times
│   └── multi_edit_text.history.json # Known edit history for validation
├── documents/
│   ├── tracked_changes.docx         # Word doc with track changes history
│   └── tracked_changes.history.json
├── spreadsheets/
│   ├── revision_history.xlsx        # Excel with revision tracking
│   └── revision_history.history.json
├── pdfs/
│   ├── multipage_with_metadata.pdf # PDF with embedded timestamps
│   └── multipage_with_metadata.history.json
├── images/
│   ├── exif_rich_image.jpg          # Image with EXIF timestamps
│   └── exif_rich_image.history.json
└── README.md                        # This file (to be created)
```

## File Creation Strategy

Since we cannot directly create files with real timestamps in the past, we have two approaches:

### Approach 1: Simulated Edit History (Recommended for v1)
Create files with **embedded markers** that indicate when edits occurred, and provide a `.history.json` file with the known edit history. The extraction system will:
1. Read the file content
2. Parse the embedded markers to identify changes
3. Use the `.history.json` for validation

### Approach 2: Git-Based Edit History
Create a separate git repository with actual commits at different times, then use git history as the source of truth.

### Approach 3: File System Timestamp Manipulation
Use `os.utime()` to set file modification times (limited to current time or past times on most systems).

**We'll use Approach 1 for immediate testing and Approach 2 for comprehensive validation.**

---

## File 1: multi_edit_text.txt

### File Content (with embedded markers)
```text
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: user1 | TYPE: create -->
# Project Notes

This is the initial version of the document.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: user2 | TYPE: add -->
## Introduction

This section was added on February 3rd.

<!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: user1 | TYPE: modify -->
# Project Notes

This is the UPDATED version of the document.

## Introduction

This section was added on February 3rd.

<!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: user1 | TYPE: delete -->
This line should be deleted.

<!-- EDIT: 2024-02-05T14:30:00Z | AUTHOR: user3 | TYPE: add -->
## Conclusion

Project completed successfully.
```

### Expected Knowledge Graph Nodes

```json
[
  {
    "node_id": "edit_2024-02-02T20:31:00Z_001",
    "node_type": "edit",
    "timestamp": "2024-02-02T20:31:00Z",
    "author": "user1",
    "edit_type": "create",
    "content_added": "# Project Notes\n\nThis is the initial version of the document.",
    "content_deleted": null,
    "file_version": "1.0",
    "source": "embedded_marker",
    "evaluation_band": "high"
  },
  {
    "node_id": "edit_2024-02-03T19:29:00Z_002",
    "node_type": "edit",
    "timestamp": "2024-02-03T19:29:00Z",
    "author": "user2",
    "edit_type": "add",
    "content_added": "## Introduction\n\nThis section was added on February 3rd.",
    "content_deleted": null,
    "file_version": "1.1",
    "source": "embedded_marker",
    "evaluation_band": "high"
  },
  {
    "node_id": "edit_2024-02-04T10:15:00Z_003",
    "node_type": "edit",
    "timestamp": "2024-02-04T10:15:00Z",
    "author": "user1",
    "edit_type": "modify",
    "content_added": "UPDATED",
    "content_deleted": "initial",
    "file_version": "1.2",
    "source": "embedded_marker",
    "evaluation_band": "high"
  },
  {
    "node_id": "edit_2024-02-04T10:15:00Z_004",
    "node_type": "edit",
    "timestamp": "2024-02-04T10:15:00Z",
    "author": "user1",
    "edit_type": "delete",
    "content_added": null,
    "content_deleted": "This line should be deleted.",
    "file_version": "1.2",
    "source": "embedded_marker",
    "evaluation_band": "high"
  },
  {
    "node_id": "edit_2024-02-05T14:30:00Z_005",
    "node_type": "edit",
    "timestamp": "2024-02-05T14:30:00Z",
    "author": "user3",
    "edit_type": "add",
    "content_added": "## Conclusion\n\nProject completed successfully.",
    "content_deleted": null,
    "file_version": "1.3",
    "source": "embedded_marker",
    "evaluation_band": "high"
  }
]
```

### Expected Knowledge Graph Edges

```json
[
  {
    "edge_id": "edge_001_002",
    "source": "edit_2024-02-02T20:31:00Z_001",
    "target": "edit_2024-02-03T19:29:00Z_002",
    "edge_type": "precursor",
    "relationship": "adds_to",
    "timestamp": "2024-02-03T19:29:00Z",
    "weight": 1.0
  },
  {
    "edge_id": "edge_002_003",
    "source": "edit_2024-02-03T19:29:00Z_002",
    "target": "edit_2024-02-04T10:15:00Z_003",
    "edge_type": "precursor",
    "relationship": "modifies",
    "timestamp": "2024-02-04T10:15:00Z",
    "weight": 1.0
  },
  {
    "edge_id": "edge_002_004",
    "source": "edit_2024-02-03T19:29:00Z_002",
    "target": "edit_2024-02-04T10:15:00Z_004",
    "edge_type": "precursor",
    "relationship": "removes_from",
    "timestamp": "2024-02-04T10:15:00Z",
    "weight": 1.0
  },
  {
    "edge_id": "edge_004_005",
    "source": "edit_2024-02-04T10:15:00Z_004",
    "target": "edit_2024-02-05T14:30:00Z_005",
    "edge_type": "precursor",
    "relationship": "adds_to",
    "timestamp": "2024-02-05T14:30:00Z",
    "weight": 1.0
  }
]
```

### .history.json File

```json
{
  "filename": "multi_edit_text.txt",
  "file_type": "text/plain",
  "description": "Text file with multiple edits at known timestamps",
  "known_edits": [
    {
      "edit_id": "edit_001",
      "timestamp": "2024-02-02T20:31:00Z",
      "author": "user1",
      "edit_type": "create",
      "description": "Initial file creation",
      "content_added": [
        "# Project Notes",
        "",
        "This is the initial version of the document."
      ],
      "content_deleted": [],
      "affected_section": "document_root",
      "file_versionAfter": "1.0",
      "marker_pattern": "<!-- EDIT: {timestamp} | AUTHOR: {author} | TYPE: {type} -->"
    },
    {
      "edit_id": "edit_002",
      "timestamp": "2024-02-03T19:29:00Z",
      "author": "user2",
      "edit_type": "add",
      "description": "Added Introduction section",
      "content_added": [
        "## Introduction",
        "",
        "This section was added on February 3rd."
      ],
      "content_deleted": [],
      "affected_section": "introduction",
      "file_versionAfter": "1.1"
    },
    {
      "edit_id": "edit_003",
      "timestamp": "2024-02-04T10:15:00Z",
      "author": "user1",
      "edit_type": "modify",
      "description": "Updated title from 'initial' to 'UPDATED'",
      "content_added": ["UPDATED"],
      "content_deleted": ["initial"],
      "affected_section": "title",
      "file_versionAfter": "1.2"
    },
    {
      "edit_id": "edit_004",
      "timestamp": "2024-02-04T10:15:00Z",
      "author": "user1",
      "edit_type": "delete",
      "description": "Removed temporary line",
      "content_added": [],
      "content_deleted": ["This line should be deleted."],
      "affected_section": "body",
      "file_versionAfter": "1.2"
    },
    {
      "edit_id": "edit_005",
      "timestamp": "2024-02-05T14:30:00Z",
      "author": "user3",
      "edit_type": "add",
      "description": "Added Conclusion section",
      "content_added": [
        "## Conclusion",
        "",
        "Project completed successfully."
      ],
      "content_deleted": [],
      "affected_section": "conclusion",
      "file_versionAfter": "1.3"
    }
  ],
  "expected_graph": {
    "total_nodes": 5,
    "total_edges": 4,
    "node_types": {
      "edit": 5
    },
    "edge_types": {
      "precursor": 4
    },
    "relationships": {
      "adds_to": 2,
      "modifies": 1,
      "removes_from": 1
    }
  },
  "validation_rules": [
    "All 5 edits must be detected as separate nodes",
    "Edges must correctly connect temporal sequence",
    "Edit types (create/add/modify/delete) must be accurately identified",
    "Timestamps must match known values within 1 second",
    "Content changes must be correctly extracted"
  ]
}
```

---

## File 2: tracked_changes.docx

### File Characteristics
- Microsoft Word document (.docx)
- Track Changes feature enabled
- Multiple authors: AuthorA, AuthorB, AuthorC
- 5+ revision sessions at different timestamps
- Accepted/rejected changes

### Known Edit History (from Word's track changes)

```json
{
  "filename": "tracked_changes.docx",
  "file_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "description": "Word document with track changes enabled",
  "known_edits": [
    {
      "edit_id": "word_edit_001",
      "timestamp": "2024-02-02T09:00:00Z",
      "author": "AuthorA",
      "edit_type": "add",
      "description": "Initial document creation",
      "content_added": ["Document Title", "", "First paragraph content."],
      "content_deleted": [],
      "word_revision_id": 1,
      "file_versionAfter": "1.0"
    },
    {
      "edit_id": "word_edit_002",
      "timestamp": "2024-02-02T15:30:00Z",
      "author": "AuthorB",
      "edit_type": "modify",
      "description": "Updated first paragraph",
      "content_added": ["Revised first paragraph content."],
      "content_deleted": ["First paragraph content."],
      "word_revision_id": 2,
      "file_versionAfter": "1.1"
    },
    {
      "edit_id": "word_edit_003",
      "timestamp": "2024-02-03T10:00:00Z",
      "author": "AuthorA",
      "edit_type": "add",
      "description": "Added second section",
      "content_added": ["## Section 2", "", "Second section content."],
      "content_deleted": [],
      "word_revision_id": 3,
      "file_versionAfter": "1.2"
    },
    {
      "edit_id": "word_edit_004",
      "timestamp": "2024-02-03T14:00:00Z",
      "author": "AuthorC",
      "edit_type": "delete",
      "description": "Removed temporary note",
      "content_added": [],
      "content_deleted": ["TODO: Remove this"],
      "word_revision_id": 4,
      "file_versionAfter": "1.3"
    },
    {
      "edit_id": "word_edit_005",
      "timestamp": "2024-02-04T11:00:00Z",
      "author": "AuthorA",
      "edit_type": "add",
      "description": "Added conclusion",
      "content_added": ["## Conclusion", "", "Final thoughts."],
      "content_deleted": [],
      "word_revision_id": 5,
      "file_versionAfter": "1.4"
    }
  ],
  "expected_graph": {
    "total_nodes": 5,
    "total_edges": 4,
    "source": "word_track_changes"
  },
  "extraction_method": "python-docx with track changes parsing"
}
```

---

## File 3: Git History Example

### Approach
Create a separate git repository with files that have actual commit history.

```bash
# Create samples4_git_repo directory (separate from main project)
mkdir samples4_git_repo
cd samples4_git_repo
git init

# Create initial file
echo "Initial content" > evolution.txt
git add evolution.txt
git commit -m "Initial commit" --date="2024-02-02T20:31:00Z"

# First edit
echo -e "Initial content\n\nAdded section 1" > evolution.txt
git add evolution.txt
git commit -m "Add section 1" --date="2024-02-03T19:29:00Z"

# Second edit
echo -e "Initial content\n\nModified section 1\n\nAdded section 2" > evolution.txt
git add evolution.txt
git commit -m "Modify section 1, add section 2" --date="2024-02-04T10:15:00Z"

# Third edit - deletion
echo -e "Initial content\n\nModified section 1\n\nAdded section 2" > evolution.txt
git add evolution.txt
git commit -m "Remove temporary note" --date="2024-02-04T11:00:00Z"
```

### Expected Knowledge Graph
Same structure as the embedded marker approach, but with:
- `source: "git_history"`
- `commit_hash` included in each edit node
- `author` from git commit
- `commit_message` in description

---

## Validation Plan

For each file in samples4:

1. **Run extraction**: `python extract.py samples4/<file>`
2. **Compare output** with `.history.json`:
   - Number of nodes matches
   - Number of edges matches
   - Timestamps match (within tolerance)
   - Edit types match
   - Content changes match
3. **Validate knowledge graph** structure:
   - All nodes connected correctly
   - Edge types appropriate
   - Temporal ordering correct
4. **Check evaluation bands**:
   - Git/native history = High confidence
   - Embedded markers = Medium confidence
   - Filesystem timestamps = Low confidence

---

## Implementation Notes

### For the Python Extractor
The extractor needs to:
1. Detect file type
2. Apply appropriate extraction methods
3. For text files with embedded markers:
   - Parse markers to extract edit information
   - Generate knowledge graph nodes and edges
4. For Word files:
   - Use python-docx to access track changes
   - Parse revision history
5. For git repositories:
   - Use GitPython to access commit history
   - Extract changes per file

### Marker Format
For text files, use HTML/XML-style comments for markers:
```
<!-- EDIT: {ISO8601_timestamp} | AUTHOR: {author} | TYPE: {create|add|modify|delete} -->
```

Or YAML-style:
```
# EDIT:
#   timestamp: 2024-02-02T20:31:00Z
#   author: user1
#   type: create
```

The second format is more readable and easier to parse.

---

## Next Steps

1. Create the actual file samples in samples4/ directory
2. Implement the Python extraction code
3. Implement the knowledge graph builder
4. Implement the evaluation band system
5. Test with all samples4 files
6. Validate against .history.json files
