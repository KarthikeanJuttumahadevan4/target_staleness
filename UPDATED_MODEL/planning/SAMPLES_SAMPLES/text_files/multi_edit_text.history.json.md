---
format: html
---

# multi_edit_text.history.json - Expected Edit History

This file contains the **expected knowledge graph structure** for `multi_edit_text.txt`.
Copy this content and save it as `samples4/text_files/multi_edit_text.history.json` (remove the markdown formatting).

---

```json
{
  "filename": "multi_edit_text.txt",
  "file_type": "text/plain",
  "file_path": "samples4/text_files/multi_edit_text.txt",
  "description": "Text file with 6 embedded edit markers at different timestamps",
  "total_expected_edits": 6,
  "total_expected_edges": 5,
  "extraction_method": "embedded_marker",
  "marker_format": "html_style",
  "known_edits": [
    {
      "edit_id": "edit_20240202T203100Z_001",
      "timestamp": "2024-02-02T20:31:00Z",
      "author": "user1",
      "edit_type": "create",
      "description": "Initial file creation",
      "file_version": "1.0",
      "source": "embedded_marker",
      "confidence": "high",
      "affected_sections": ["document_root"],
      "content_before": null,
      "content_after": "# Project Documentation\n\nThis is the initial version of the project documentation.\nThe project aims to create a universal file extractor.\n\n",
      "line_numbers": [1, 2, 3],
      "marker_text": "<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: user1 | TYPE: create | SECTION: document_root | DESCRIPTION: Initial file creation -->"
    },
    {
      "edit_id": "edit_20240203T192900Z_002",
      "timestamp": "2024-02-03T19:29:00Z",
      "author": "user2",
      "edit_type": "add",
      "description": "Added introduction section",
      "file_version": "1.1",
      "source": "embedded_marker",
      "confidence": "high",
      "affected_sections": ["introduction"],
      "content_before": null,
      "content_after": "## Introduction\n\nThis section provides an overview of the project.\nThe extractor can handle multiple file formats simultaneously.\n\n## Features\n\n- Multi-format support\n- Version history tracking\n- Knowledge graph generation\n",
      "line_numbers": [5, 6, 7, 8, 9, 10, 11, 12, 13],
      "marker_text": "<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: user2 | TYPE: add | SECTION: introduction | DESCRIPTION: Added introduction section -->"
    },
    {
      "edit_id": "edit_20240204T101500Z_003",
      "timestamp": "2024-02-04T10:15:00Z",
      "author": "user1",
      "edit_type": "modify",
      "description": "Updated title to include version",
      "file_version": "1.2",
      "source": "embedded_marker",
      "confidence": "high",
      "affected_sections": ["title"],
      "content_before": "# Project Documentation",
      "content_after": "# Project Documentation v1.0",
      "line_numbers": [15],
      "marker_text": "<!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: user1 | TYPE: modify | SECTION: title | DESCRIPTION: Updated title to include version -->",
      "change_details": {
        "old_text": "# Project Documentation",
        "new_text": "# Project Documentation v1.0",
        "diff_type": "character_replace",
        "position": 0,
        "added": " v1.0",
        "removed": ""
      }
    },
    {
      "edit_id": "edit_20240204T142000Z_004",
      "timestamp": "2024-02-04T14:20:00Z",
      "author": "user1",
      "edit_type": "delete",
      "description": "Removed temporary notes",
      "file_version": "1.3",
      "source": "embedded_marker",
      "confidence": "high",
      "affected_sections": ["temp_notes"],
      "content_before": "# TEMPORARY NOTES - REMOVE THIS\nThis is temporary content that should be deleted.\nThe project aims to create a universal file extractor.",
      "content_after": null,
      "line_numbers": [23, 24, 25],
      "marker_text": "<!-- EDIT: 2024-02-04T14:20:00Z | AUTHOR: user1 | TYPE: delete | SECTION: temp_notes | DESCRIPTION: Removed temporary notes -->"
    },
    {
      "edit_id": "edit_20240204T142000Z_005",
      "timestamp": "2024-02-04T14:20:00Z",
      "author": "user1",
      "edit_type": "add",
      "description": "Added performance features",
      "file_version": "1.3",
      "source": "embedded_marker",
      "confidence": "high",
      "affected_sections": ["features"],
      "content_before": null,
      "content_after": "## Performance Features\n\nThe extractor is optimized for:\n- Fast processing of small files\n- Parallel extraction for large files\n- Memory-efficient streaming\n",
      "line_numbers": [27, 28, 29, 30, 31],
      "marker_text": "<!-- EDIT: 2024-02-04T14:20:00Z | AUTHOR: user1 | TYPE: add | SECTION: features | DESCRIPTION: Added performance features -->"
    },
    {
      "edit_id": "edit_20240205T164500Z_006",
      "timestamp": "2024-02-05T16:45:00Z",
      "author": "user3",
      "edit_type": "add",
      "description": "Added conclusion section",
      "file_version": "1.4",
      "source": "embedded_marker",
      "confidence": "high",
      "affected_sections": ["conclusion"],
      "content_before": null,
      "content_after": "## Conclusion\n\nThis documentation covers the main features of the extractor.\nFor more information, please refer to the technical specifications.\nThe project is actively maintained and updated regularly.",
      "line_numbers": [33, 34, 35, 36, 37],
      "marker_text": "<!-- EDIT: 2024-02-05T16:45:00Z | AUTHOR: user3 | TYPE: add | SECTION: conclusion | DESCRIPTION: Added conclusion section -->"
    }
  ],
  "expected_edges": [
    {
      "edge_id": "edge_001_002",
      "source": "edit_20240202T203100Z_001",
      "target": "edit_20240203T192900Z_002",
      "edge_type": "temporal",
      "relationship": "adds_to",
      "timestamp": "2024-02-03T19:29:00Z",
      "weight": 1.0,
      "time_diff_seconds": 82800.0,
      "description": "User2 adds introduction section after initial creation by user1"
    },
    {
      "edge_id": "edge_002_003",
      "source": "edit_20240203T192900Z_002",
      "target": "edit_20240204T101500Z_003",
      "edge_type": "temporal",
      "relationship": "modifies",
      "timestamp": "2024-02-04T10:15:00Z",
      "weight": 1.0,
      "time_diff_seconds": 50400.0,
      "description": "User1 modifies the title to include version number"
    },
    {
      "edge_id": "edge_003_004",
      "source": "edit_20240204T101500Z_003",
      "target": "edit_20240204T142000Z_004",
      "edge_type": "temporal",
      "relationship": "removes_from",
      "timestamp": "2024-02-04T14:20:00Z",
      "weight": 1.0,
      "time_diff_seconds": 15300.0,
      "description": "User1 removes temporary notes section"
    },
    {
      "edge_id": "edge_003_005",
      "source": "edit_20240204T101500Z_003",
      "target": "edit_20240204T142000Z_005",
      "edge_type": "temporal",
      "relationship": "adds_to",
      "timestamp": "2024-02-04T14:20:00Z",
      "weight": 1.0,
      "time_diff_seconds": 15300.0,
      "description": "User1 adds performance features section"
    },
    {
      "edge_id": "edge_005_006",
      "source": "edit_20240204T142000Z_005",
      "target": "edit_20240205T164500Z_006",
      "edge_type": "temporal",
      "relationship": "adds_to",
      "timestamp": "2024-02-05T16:45:00Z",
      "weight": 1.0,
      "time_diff_seconds": 94500.0,
      "description": "User3 adds conclusion section"
    }
  ],
  "expected_knowledge_graph": {
    "nodes": 6,
    "edges": 5,
    "node_types": {
      "edit": 6
    },
    "edge_types": {
      "temporal": 5
    },
    "relationships": {
      "adds_to": 3,
      "modifies": 1,
      "removes_from": 1
    },
    "confidence_distribution": {
      "high": 6,
      "medium": 0,
      "low": 0
    }
  },
  "validation_rules": [
    {
      "rule": "node_count",
      "expected": 6,
      "description": "There should be exactly 6 edit nodes",
      "severity": "critical"
    },
    {
      "rule": "edge_count",
      "expected": 5,
      "description": "There should be exactly 5 edges connecting the nodes",
      "severity": "critical"
    },
    {
      "rule": "timestamp_order",
      "expected": true,
      "description": "Nodes should be ordered chronologically",
      "severity": "critical"
    },
    {
      "rule": "all_authors_present",
      "expected": ["user1", "user2", "user3"],
      "description": "All three authors should be present in the edits",
      "severity": "medium"
    },
    {
      "rule": "edit_types",
      "expected": {"create": 1, "add": 3, "modify": 1, "delete": 1},
      "description": "Edit types should match expected distribution",
      "severity": "medium"
    },
    {
      "rule": "content_extraction",
      "expected": true,
      "description": "Content before/after should be correctly extracted",
      "severity": "medium"
    },
    {
      "rule": "timestamp_accuracy",
      "expected": "exact",
      "description": "Timestamps should exactly match the markers",
      "severity": "low"
    }
  ],
  "metadata": {
    "created": "2024-10-05T00:00:00Z",
    "version": "1.0.0",
    "extractor_version": "1.0.0",
    "notes": "This file should be used for automated validation of the extractor."
  }
}
```

---

## Usage

### Save as JSON file:
```bash
# Copy content to JSON file (without markdown formatting)
cat > samples4/text_files/multi_edit_text.history.json << 'EOF'
{
  "filename": "multi_edit_text.txt",
  "file_type": "text/plain",
  "file_path": "samples4/text_files/multi_edit_text.txt",
  "description": "Text file with 6 embedded edit markers at different timestamps",
  "total_expected_edits": 6,
  "total_expected_edges": 5,
  "extraction_method": "embedded_marker",
  "marker_format": "html_style",
  "known_edits": [
    {
      "edit_id": "edit_20240202T203100Z_001",
      "timestamp": "2024-02-02T20:31:00Z",
      "author": "user1",
      "edit_type": "create",
      "description": "Initial file creation",
      "file_version": "1.0",
      "source": "embedded_marker",
      "confidence": "high",
      "affected_sections": ["document_root"],
      "content_before": null,
      "content_after": "# Project Documentation\n\nThis is the initial version of the project documentation.\nThe project aims to create a universal file extractor.\n\n",
      "line_numbers": [1, 2, 3]
    }
  ]
}
EOF
```

### Validate Extraction:
```python
import json

def validate_extraction(extracted, expected):
    """Simple validation function."""
    errors = []
    
    # Check node count
    extracted_nodes = extracted.get("knowledge_graph", {}).get("nodes", [])
    expected_nodes = expected.get("total_expected_edits", 0)
    if len(extracted_nodes) != expected_nodes:
        errors.append(f"Node count mismatch: expected {expected_nodes}, got {len(extracted_nodes)}")
    
    # Check edge count
    extracted_edges = extracted.get("knowledge_graph", {}).get("edges", [])
    expected_edges = expected.get("total_expected_edges", 0)
    if len(extracted_edges) != expected_edges:
        errors.append(f"Edge count mismatch: expected {expected_edges}, got {len(extracted_edges)}")
    
    # Check timestamps
    extracted_timestamps = [n.get("timestamp") for n in extracted_nodes]
    expected_timestamps = [e.get("timestamp") for e in expected.get("known_edits", [])]
    
    for expected_ts in expected_timestamps:
        if expected_ts not in extracted_timestamps:
            errors.append(f"Missing expected timestamp: {expected_ts}")
    
    if errors:
        print("VALIDATION FAILED:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("VALIDATION PASSED")
        return True

# Run validation
with open("result.json") as f:
    extracted = json.load(f)
with open("samples4/text_files/multi_edit_text.history.json") as f:
    expected = json.load(f)

validate_extraction(extracted, expected)
```

---

## Key Validation Points

1. **Node Count**: Must be exactly 6
2. **Edge Count**: Must be exactly 5
3. **Timestamps**: All 6 timestamps must be present
4. **Authors**: user1, user2, user3 must all be present
5. **Edit Types**: 1 create, 3 add, 1 modify, 1 delete
6. **Content**: Content before/after should be correctly extracted from markers
7. **Confirmation Bands**: All should be "high" for embedded markers

---

## Notes

- This is a **validation reference file**, not the actual history data
- The actual extractor will extract this information automatically from the text file markers
- The IDs used here (edit_20240202T203100Z_001, etc.) are generated by the extractor and may differ
- The exact format of the extracted nodes may vary slightly from this reference
- Use the validation rules for automated testing, not exact JSON matching
