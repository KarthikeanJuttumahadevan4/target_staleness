---
format: html
---

# Expected Results for All Sample Files

This document shows the **expected extraction output** for each sample file type. Use this to verify your implementation is working correctly.

---

## 📊 Test File Matrix

| File | Event | Timestamp | Author | Type | Nodes | Edges | Confidence | Status |
|------|-------|-----------|--------|------|-------|-------|------------|--------|
| **Text** | Edit 1: Create | 2024-02-02T20:31:00Z | alice | create | 5 | 4 | High | ✅ |
| | Edit 2: Add intro | 2024-02-03T19:29:00Z | bob | add | | | High | ✅ |
| | Edit 3: Modify title | 2024-02-04T10:15:00Z | alice | modify | | | High | ✅ |
| | Edit 4: Add media | 2024-02-04T14:29:00Z | alice | add | | | High | ✅ |
| | Edit 5: Add conclusion | 2024-02-05T09:00:00Z | bob | add | | | High | ✅ |
| **Word** | Initial | 2024-02-02T10:00:00Z | You | create | 4 | 3 | High | ⚠️ |
| | Add Image 1 | 2024-02-02T10:05:00Z | You | add | | | High | ⚠️ |
| | Add Image 2 | 2024-02-02T10:10:00Z | You | add | | | High | ⚠️ |
| | Modify title | 2024-02-02T10:15:00Z | You | modify | | | High | ⚠️ |
| **PDF** | Creation | 2024-02-01T08:00:00Z | PDF User | metadata | 1 | 0 | High | ⚠️ |
| **Image** | Photo taken | 2024-02-03T10:00:00Z | Photographer | exif | 1 | 0 | High | ⚠️ |
| **Audio** | Recording | 2024-02-04T11:00:00Z | Recorder | id3 | 1 | 0 | Medium | ⚠️ |
| **Video** | Recording | 2024-02-05T12:00:00Z | Recorder | metadata | 1 | 0 | Medium | ⚠️ |
| **Git** | Commit 1 | 2024-02-01T08:00:00Z | Test User | create | 4 | 3 | High | ⚠️ |
| | Commit 2 | 2024-02-02T09:00:00Z | Alice | add | | | High | ⚠️ |
| | Commit 3 | 2024-02-03T10:00:00Z | Bob | modify | | | High | ⚠️ |
| | Commit 4 | 2024-02-04T11:00:00Z | Alice | delete | | | High | ⚠️ |

✅ = Fully supported in basic version  
⚠️ = Requires full implementation

---

## 📄 File 1: Text with Embedded Markers (`multi_edit_text.txt`)

### Input File
```text
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create | SECTION: header -->
# Project Report
This is the initial version.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: bob | TYPE: add | SECTION: introduction -->
## Introduction
This section provides an overview.

<!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: alice | TYPE: modify | SECTION: title -->
# Project Report v1.0
This is the UPDATED version.

<!-- EDIT: 2024-02-04T14:29:00Z | AUTHOR: alice | TYPE: add | SECTION: media -->
## Media
- Image: logo.png
- Audio: intro.mp3

<!-- EDIT: 2024-02-05T09:00:00Z | AUTHOR: bob | TYPE: add | SECTION: conclusion -->
## Conclusion
Final section.
```

### Extraction Command
```bash
python extract.py samples4/multi_edit_text.txt --output results/multi_edit_text.json
```

### Expected Output (JSON)
```json
{
  "extraction_metadata": {
    "file": "samples4/multi_edit_text.txt",
    "timestamp": "2026-10-05T15:30:45Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": 1456,
      "created_time": "2026-10-05T15:25:00Z",
      "modified_time": "2026-10-05T15:25:00Z",
      "accessed_time": "2026-10-05T15:30:45Z"
    },
    "file_type": "text/plain",
    "text": {
      "character_count": 1456,
      "line_count": 20,
      "word_count": 80
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
        "content_before": null,
        "content_after": "# Project Report\nThis is the initial version.",
        "affected_sections": [],
        "description": "",
        "file_version": "1.0",
        "source": "embedded_marker",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_20240203T192900Z_1",
        "node_type": "edit",
        "timestamp": "2024-02-03T19:29:00Z",
        "author": "bob",
        "edit_type": "add",
        "content_before": null,
        "content_after": "## Introduction\nThis section provides an overview.",
        "affected_sections": [],
        "description": "",
        "file_version": "2.0",
        "source": "embedded_marker",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_20240204T101500Z_2",
        "node_type": "edit",
        "timestamp": "2024-02-04T10:15:00Z",
        "author": "alice",
        "edit_type": "modify",
        "content_before": null,
        "content_after": "# Project Report v1.0\nThis is the UPDATED version.",
        "affected_sections": [],
        "description": "",
        "file_version": "3.0",
        "source": "embedded_marker",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_20240204T142900Z_3",
        "node_type": "edit",
        "timestamp": "2024-02-04T14:29:00Z",
        "author": "alice",
        "edit_type": "add",
        "content_before": null,
        "content_after": "## Media\n- Image: logo.png\n- Audio: intro.mp3",
        "affected_sections": [],
        "description": "",
        "file_version": "4.0",
        "source": "embedded_marker",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_20240205T090000Z_4",
        "node_type": "edit",
        "timestamp": "2024-02-05T09:00:00Z",
        "author": "bob",
        "edit_type": "add",
        "content_before": null,
        "content_after": "## Conclusion\nFinal section.",
        "affected_sections": [],
        "description": "",
        "file_version": "5.0",
        "source": "embedded_marker",
        "evaluation_band": "high"
      }
    ],
    "edit_count": 5
  },
  "knowledge_graph": {
    "nodes": [
      {
        "node_id": "edit_20240202T203100Z_0",
        "node_type": "edit",
        "timestamp": "2024-02-02T20:31:00Z",
        "author": "alice",
        "edit_type": "create",
        "content_before": null,
        "content_after": "# Project Report\nThis is the initial version.",
        "affected_sections": [],
        "description": "",
        "file_version": "1.0",
        "source": "embedded_marker",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_20240203T192900Z_1",
        "node_type": "edit",
        "timestamp": "2024-02-03T19:29:00Z",
        "author": "bob",
        "edit_type": "add",
        "content_before": null,
        "content_after": "## Introduction\nThis section provides an overview.",
        "affected_sections": [],
        "description": "",
        "file_version": "2.0",
        "source": "embedded_marker",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_20240204T101500Z_2",
        "node_type": "edit",
        "timestamp": "2024-02-04T10:15:00Z",
        "author": "alice",
        "edit_type": "modify",
        "content_before": null,
        "content_after": "# Project Report v1.0\nThis is the UPDATED version.",
        "affected_sections": [],
        "description": "",
        "file_version": "3.0",
        "source": "embedded_marker",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_20240204T142900Z_3",
        "node_type": "edit",
        "timestamp": "2024-02-04T14:29:00Z",
        "author": "alice",
        "edit_type": "add",
        "content_before": null,
        "content_after": "## Media\n- Image: logo.png\n- Audio: intro.mp3",
        "affected_sections": [],
        "description": "",
        "file_version": "4.0",
        "source": "embedded_marker",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_20240205T090000Z_4",
        "node_type": "edit",
        "timestamp": "2024-02-05T09:00:00Z",
        "author": "bob",
        "edit_type": "add",
        "content_before": null,
        "content_after": "## Conclusion\nFinal section.",
        "affected_sections": [],
        "description": "",
        "file_version": "5.0",
        "source": "embedded_marker",
        "evaluation_band": "high"
      }
    ],
    "edges": [
      {
        "edge_id": "edge_edit_20240202T203100Z_0_edit_20240203T192900Z_1",
        "source": "edit_20240202T203100Z_0",
        "target": "edit_20240203T192900Z_1",
        "edge_type": "temporal",
        "relationship": "adds_to",
        "timestamp": "2024-02-03T19:29:00Z",
        "weight": 1.0
      },
      {
        "edge_id": "edge_edit_20240203T192900Z_1_edit_20240204T101500Z_2",
        "source": "edit_20240203T192900Z_1",
        "target": "edit_20240204T101500Z_2",
        "edge_type": "temporal",
        "relationship": "adds_to",
        "timestamp": "2024-02-04T10:15:00Z",
        "weight": 1.0
      },
      {
        "edge_id": "edge_edit_20240204T101500Z_2_edit_20240204T142900Z_3",
        "source": "edit_20240204T101500Z_2",
        "target": "edit_20240204T142900Z_3",
        "edge_type": "temporal",
        "relationship": "adds_to",
        "timestamp": "2024-02-04T14:29:00Z",
        "weight": 1.0
      },
      {
        "edge_id": "edge_edit_20240204T142900Z_3_edit_20240205T090000Z_4",
        "source": "edit_20240204T142900Z_3",
        "target": "edit_20240205T090000Z_4",
        "edge_type": "temporal",
        "relationship": "adds_to",
        "timestamp": "2024-02-05T09:00:00Z",
        "weight": 1.0
      }
    ],
    "total_nodes": 5,
    "total_edges": 4
  },
  "summary": {
    "total_edits": 5,
    "total_nodes": 5,
    "total_edges": 4,
    "sources_used": ["embedded_marker"],
    "confidence_distribution": {
      "high": 5,
      "medium": 0,
      "low": 0
    }
  }
}
```

### Validation Commands
```bash
# Check node count
python -c "import json; d=json.load(open('results/multi_edit_text.json')); print(f'Nodes: {d[\"knowledge_graph\"][\"total_nodes\"]} (expected: 5)')"

# Check edge count
python -c "import json; d=json.load(open('results/multi_edit_text.json')); print(f'Edges: {d[\"knowledge_graph\"][\"total_edges\"]} (expected: 4)')"

# Check all timestamps present
python -c "
import json
d = json.load(open('results/multi_edit_text.json'))
timestamps = [n['timestamp'] for n in d['knowledge_graph']['nodes']]
expected = ['2024-02-02T20:31:00Z', '2024-02-03T19:29:00Z', '2024-02-04T10:15:00Z', '2024-02-04T14:29:00Z', '2024-02-05T09:00:00Z']
for ts in expected:
    if ts in timestamps:
        print(f'✅ {ts} found')
    else:
        print(f'❌ {ts} NOT FOUND')
"

# Check all authors present
python -c "
import json
d = json.load(open('results/multi_edit_text.json'))
authors = {n['author'] for n in d['knowledge_graph']['nodes']}
expected = {'alice', 'bob'}
for a in expected:
    if a in authors:
        print(f'✅ Author {a} found')
    else:
        print(f'❌ Author {a} NOT FOUND')
"
```

---

## 📄 File 2: Word Document (`tracked_changes.docx`)

### Expected Output (Basic Version - Filesystem Only)
```json
{
  "extraction_metadata": {
    "file": "samples4/tracked_changes.docx",
    "timestamp": "2026-10-05T15:35:00Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": 25000,
      "created_time": "2026-10-05T15:30:00Z",
      "modified_time": "2026-10-05T15:30:00Z",
      "accessed_time": "2026-10-05T15:35:00Z"
    },
    "file_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  },
  "version_history": {
    "edits": [
      {
        "node_id": "fs_tracked_changes.docx",
        "node_type": "edit",
        "timestamp": "2026-10-05T15:30:00Z",
        "author": null,
        "edit_type": "create",
        "content_after": "[Binary file: tracked_changes.docx]",
        "source": "filesystem",
        "evaluation_band": "low"
      }
    ],
    "edit_count": 1
  },
  "knowledge_graph": {
    "nodes": 1,
    "edges": 0,
    "total_nodes": 1,
    "total_edges": 0
  },
  "summary": {
    "total_edits": 1,
    "total_nodes": 1,
    "total_edges": 0,
    "sources_used": ["filesystem"],
    "confidence_distribution": {
      "high": 0,
      "medium": 0,
      "low": 1
    }
  }
}
```

### Expected Output (Full Version with Word Track Changes)
```json
{
  "version_history": {
    "edits": [
      {
        "timestamp": "2024-02-02T10:00:00Z",
        "author": "Your Name",
        "edit_type": "create",
        "source": "word_track_changes"
      },
      {
        "timestamp": "2024-02-02T10:05:00Z",
        "author": "Your Name",
        "edit_type": "add",
        "description": "Added: Image 1 inserted here.",
        "source": "word_track_changes"
      },
      {
        "timestamp": "2024-02-02T10:10:00Z",
        "author": "Your Name",
        "edit_type": "add",
        "description": "Added: Image 2 inserted here.",
        "source": "word_track_changes"
      },
      {
        "timestamp": "2024-02-02T10:15:00Z",
        "author": "Your Name",
        "edit_type": "modify",
        "content_before": "Project Report",
        "content_after": "Project Report v1.0",
        "source": "word_track_changes"
      }
    ]
  },
  "knowledge_graph": {
    "total_nodes": 4,
    "total_edges": 3
  }
}
```

---

## 📄 File 3: PDF (`metadata.pdf`)

### Expected Output (Basic Version)
```json
{
  "extraction_metadata": {
    "file": "samples4/metadata.pdf",
    "timestamp": "2026-10-05T15:40:00Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": 15000,
      "created_time": "2026-10-05T15:35:00Z",
      "modified_time": "2026-10-05T15:35:00Z",
      "accessed_time": "2026-10-05T15:40:00Z"
    },
    "file_type": "application/pdf"
  },
  "version_history": {
    "edits": [
      {
        "node_id": "fs_metadata.pdf",
        "timestamp": "2026-10-05T15:35:00Z",
        "author": null,
        "edit_type": "create",
        "source": "filesystem",
        "evaluation_band": "low"
      }
    ],
    "edit_count": 1
  },
  "knowledge_graph": {
    "total_nodes": 1,
    "total_edges": 0
  },
  "summary": {
    "total_edits": 1,
    "sources_used": ["filesystem"],
    "confidence_distribution": {"low": 1}
  }
}
```

### Expected Output (Full Version with PyPDF2)
```json
{
  "file_metadata": {
    "pdf": {
      "page_count": 1,
      "author": "PDF Test User",
      "title": "Metadata Test Document",
      "subject": "Testing PDF metadata extraction",
      "creator": "Microsoft Word",
      "creation_date": "2024-02-01T08:00:00Z",
      "modification_date": "2024-02-02T09:00:00Z"
    }
  },
  "version_history": {
    "edits": [
      {
        "node_id": "pdf_metadata",
        "timestamp": "2024-02-02T09:00:00Z",
        "author": "PDF Test User",
        "edit_type": "create",
        "source": "pdf_metadata",
        "evaluation_band": "high"
      }
    ]
  }
}
```

---

## 📄 Files 4-6: Binary Files (Image, Audio, Video)

These will all have similar basic output (filesystem metadata) until the full extractors are implemented.

### Expected Output (Basic Version - All Binary Files)
```json
{
  "extraction_metadata": {
    "file": "samples4/[filename]",
    "timestamp": "2026-10-05T15:45:00Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": [varies],
      "created_time": "2026-10-05T15:40:00Z",
      "modified_time": "2026-10-05T15:40:00Z",
      "accessed_time": "2026-10-05T15:45:00Z"
    },
    "file_type": "[mime-type]"
  },
  "version_history": {
    "edits": [
      {
        "node_id": "fs_[filename]",
        "timestamp": "2026-10-05T15:40:00Z",
        "author": null,
        "edit_type": "create",
        "content_after": "[Binary file: [filename]]",
        "source": "filesystem",
        "evaluation_band": "low"
      }
    ],
    "edit_count": 1
  },
  "knowledge_graph": {
    "total_nodes": 1,
    "total_edges": 0
  },
  "summary": {
    "total_edits": 1,
    "sources_used": ["filesystem"],
    "confidence_distribution": {"low": 1}
  }
}
```

### Expected Output (Full Version)

**Image (EXIF)**:
```json
{
  "file_metadata": {
    "exif": {
      "DateTimeOriginal": "2024-02-03T10:00:00Z",
      "DateTimeDigitized": "2024-02-03T10:00:00Z",
      "Make": "Apple",
      "Model": "iPhone 13",
      "Orientation": 1,
      "Width": 4032,
      "Height": 3024
    }
  },
  "version_history": {
    "edits": [
      {
        "timestamp": "2024-02-03T10:00:00Z",
        "edit_type": "create",
        "source": "exif_metadata",
        "evaluation_band": "high"
      }
    ]
  }
}
```

**Audio (ID3)**:
```json
{
  "file_metadata": {
    "audio": {
      "duration_seconds": 15.5,
      "bit_rate": 128000,
      "channels": 2,
      "sample_rate": 44100,
      "tags": {
        "title": "Test Audio",
        "artist": "Test Artist"
      }
    }
  }
}
```

**Video (Metadata)**:
```json
{
  "file_metadata": {
    "video": {
      "duration_seconds": 30.0,
      "resolution": {"width": 1920, "height": 1080},
      "frame_rate": 30,
      "codec": "h264"
    }
  }
}
```

---

## 📄 File 7: Git Version History

### Expected Output (Basic Version)
Same as other binary files - filesystem metadata only.

### Expected Output (Full Version with GitPython)
```json
{
  "extraction_metadata": {
    "file": "samples4_git/evolution.txt",
    "git_repo_path": "samples4_git"
  },
  "version_history": {
    "edits": [
      {
        "node_id": "git_abc123",
        "timestamp": "2024-02-01T08:00:00Z",
        "author": "Test User <test@example.com>",
        "edit_type": "create",
        "commit_hash": "abc123def456...",
        "message": "Initial commit",
        "content_after": "Initial content",
        "source": "git",
        "evaluation_band": "high"
      },
      {
        "node_id": "git_def456",
        "timestamp": "2024-02-02T09:00:00Z",
        "author": "Alice <alice@example.com>",
        "edit_type": "add",
        "commit_hash": "def456ghi789...",
        "message": "Add section 1",
        "content_before": "Initial content",
        "content_after": "Initial content\n\nAdded section 1",
        "source": "git",
        "evaluation_band": "high"
      },
      {
        "node_id": "git_ghi789",
        "timestamp": "2024-02-03T10:00:00Z",
        "author": "Bob <bob@example.com>",
        "edit_type": "modify",
        "commit_hash": "ghi789jkl012...",
        "message": "Modify section 1, add section 2",
        "content_before": "Added section 1",
        "content_after": "Modified section 1\n\nAdded section 2",
        "source": "git",
        "evaluation_band": "high"
      },
      {
        "node_id": "git_jkl012",
        "timestamp": "2024-02-04T11:00:00Z",
        "author": "Alice <alice@example.com>",
        "edit_type": "delete",
        "commit_hash": "jkl012mno345...",
        "message": "Remove temp note",
        "content_before": "temp note",
        "content_after": null,
        "source": "git",
        "evaluation_band": "high"
      }
    ],
    "edit_count": 4
  },
  "knowledge_graph": {
    "nodes": 4,
    "edges": 3,
    "edges": [
      {
        "source": "git_abc123",
        "target": "git_def456",
        "relationship": "adds_to",
        "timestamp": "2024-02-02T09:00:00Z"
      },
      {
        "source": "git_def456",
        "target": "git_ghi789",
        "relationship": "modifies",
        "timestamp": "2024-02-03T10:00:00Z"
      },
      {
        "source": "git_ghi789",
        "target": "git_jkl012",
        "relationship": "removes_from",
        "timestamp": "2024-02-04T11:00:00Z"
      }
    ]
  },
  "summary": {
    "total_edits": 4,
    "sources_used": ["git"],
    "confidence_distribution": {"high": 4}
  }
}
```

---

## 📊 Validation Summary Script

Run this to validate all files at once:

```bash
cat > validate_all.sh << 'EOF'
#!/bin/bash

echo "=========================================="
echo "VALIDATION SUMMARY"
echo "=========================================="
echo ""

for file in results/*.json; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .json)
        echo "File: $filename"
        
        # Extract counts
        nodes=$(python -c "import json; d=json.load(open('$file')); print(d['knowledge_graph']['total_nodes'])")
        edges=$(python -c "import json; d=json.load(open('$file')); print(d['knowledge_graph']['total_edges'])")
        sources=$(python -c "import json; d=json.load(open('$file')); print(', '.join(d['summary']['sources_used']))")
        
        echo "  Nodes: $nodes"
        echo "  Edges: $edges"
        echo "  Sources: $sources"
        echo ""
    fi
done

echo "=========================================="
echo "DETAILED VALIDATION"
echo "=========================================="
echo ""

# Text file specific
echo "--- multi_edit_text.txt ---"
python -c "
import json
d = json.load(open('results/multi_edit_text.json'))
kg = d['knowledge_graph']
print(f'Nodes: {kg[\"total_nodes\"]} (expected: 5) - {\"✅\" if kg[\"total_nodes\"] == 5 else \"❌\"}')
print(f'Edges: {kg[\"total_edges\"]} (expected: 4) - {\"✅\" if kg[\"total_edges\"] == 4 else \"❌\"}')
timestamps = [n['timestamp'] for n in kg['nodes']]
expected_ts = ['2024-02-02T20:31:00Z', '2024-02-03T19:29:00Z', '2024-02-04T10:15:00Z', '2024-02-04T14:29:00Z', '2024-02-05T09:00:00Z']
for ts in expected_ts:
    status = '✅' if ts in timestamps else '❌'
    print(f'Timestamp {ts}: {status}')
"

echo ""
echo "Validation complete!"
EOF

chmod +x validate_all.sh
./validate_all.sh
```

---

## 🎯 Success Checklist

- [ ] Text file: 5 nodes, 4 edges, all timestamps correct
- [ ] Word file: File readable, basic metadata extracted
- [ ] PDF file: File readable, basic metadata extracted
- [ ] Image file: File readable, basic metadata extracted
- [ ] Audio file: File readable, basic metadata extracted
- [ ] Video file: File readable, basic metadata extracted
- [ ] Git file: File readable, basic metadata extracted

---

## 🚀 Next Steps

1. **Start with text file** - This should work perfectly with basic script
2. **Verify basic extraction** - Check JSON output for expected structure
3. **Add full extractors** - Implement PDF, Word, EXIF, etc. for richer results
4. **Compare with expected** - Use validation commands above

---

**The text file example provides the most complete demonstration of the knowledge graph functionality. All other file types show basic extraction that can be enhanced with additional extractors.**
