# Expected Results

This document describes the expected output for each sample file when processed by the extractor.

---

## Result Format

The extractor produces JSON output with this structure:

```json
{
  "extraction_metadata": {
    "file": "path/to/file",
    "timestamp": "2024-XX-XXTXX:XX:XX.XXXXXXZ",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": X,
      "created_time": "2024-XX-XXTXX:XX:XXZ",
      "modified_time": "2024-XX-XXTXX:XX:XXZ",
      "accessed_time": "2024-XX-XXTXX:XX:XXZ"
    },
    "text": {
      "character_count": X,
      "line_count": X,
      "word_count": X
    }
  },
  "version_history": {
    "edits": [
      {
        "node_id": "edit_...",
        "node_type": "edit",
        "timestamp": "2024-XX-XXTXX:XX:XXZ",
        "author": "name",
        "edit_type": "create|add|modify|delete",
        "content_before": "text (for deletes)",
        "content_after": "text",
        "affected_sections": [],
        "description": "",
        "file_version": "N.0",
        "source": "embedded_marker|filesystem|git",
        "evaluation_band": "high|medium|low"
      }
    ],
    "edit_count": N
  },
  "knowledge_graph": {
    "nodes": [...],
    "edges": [
      {
        "edge_id": "edge_...",
        "source": "edit_X",
        "target": "edit_Y",
        "edge_type": "directed",
        "relationship": "adds_to|replaces|modifies",
        "timestamp": "2024-XX-XXTXX:XX:XXZ",
        "weight": 1.0
      }
    ],
    "total_nodes": N,
    "total_edges": M
  },
  "summary": {
    "total_edits": N,
    "total_nodes": N,
    "total_edges": M,
    "sources_used": ["embedded_marker"],
    "confidence_distribution": {
      "high": X,
      "medium": Y,
      "low": Z
    }
  }
}
```

---

## Sample File Expected Results

### 1. samples/test.txt (3 edits)

**File content:**
```
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create -->
# Report
Initial content.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: bob | TYPE: add -->
## Introduction
Added introduction section.

<!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: alice | TYPE: modify -->
## Revised Introduction
Updated the introduction with more details.
```

**Expected JSON structure:**

```json
{
  "extraction_metadata": {
    "file": "samples/test.txt",
    "extractor_version": "1.0.0"
  },
  "version_history": {
    "edit_count": 3,
    "edits": [
      {
        "node_id": "edit_20240202T203100Z_0",
        "author": "alice",
        "edit_type": "create",
        "timestamp": "2024-02-02T20:31:00Z",
        "content_after": "# Report\nInitial content.",
        "source": "embedded_marker",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_20240203T192900Z_0",
        "author": "bob",
        "edit_type": "add",
        "timestamp": "2024-02-03T19:29:00Z",
        "content_after": "## Introduction\nAdded introduction section.",
        "source": "embedded_marker",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_20240204T101500Z_0",
        "author": "alice",
        "edit_type": "modify",
        "timestamp": "2024-02-04T10:15:00Z",
        "content_after": "## Revised Introduction\nUpdated the introduction with more details.",
        "source": "embedded_marker",
        "evaluation_band": "high"
      }
    ]
  },
  "knowledge_graph": {
    "total_nodes": 3,
    "total_edges": 2,
    "nodes": [...array of 3 edit nodes...],
    "edges": [
      {
        "source": "edit_20240202T203100Z_0",
        "target": "edit_20240203T192900Z_0",
        "relationship": "adds_to",
        "timestamp": "2024-02-03T19:29:00Z"
      },
      {
        "source": "edit_20240203T192900Z_0",
        "target": "edit_20240204T101500Z_0",
        "relationship": "adds_to",
        "timestamp": "2024-02-04T10:15:00Z"
      }
    ]
  },
  "summary": {
    "total_edits": 3,
    "total_nodes": 3,
    "total_edges": 2,
    "sources_used": ["embedded_marker"],
    "confidence_distribution": {
      "high": 3,
      "medium": 0,
      "low": 0
    }
  }
}
```

---

### 2. samples/plain.txt (no markers)

**File content:**
```
This is a plain text file
It has no embedded markers
```

**Expected JSON structure:**

```json
{
  "extraction_metadata": {
    "file": "samples/plain.txt"  
  },
  "version_history": {
    "edit_count": 1,
    "edits": [
      {
        "node_id": "fs_plain.txt",
        "author": null,
        "edit_type": "create",
        "timestamp": "[current filesystem modify timestamp]",
        "content_after": "This is a plain text file\nIt has no embedded markers",
        "source": "filesystem",
        "evaluation_band": "low"
      }
    ]
  },
  "knowledge_graph": {
    "total_nodes": 1,
    "total_edges": 0,
    "nodes": [...array of 1 node...],
    "edges": []
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

**Key difference:** Falls back to filesystem metadata only, low confidence, no edges.

---

### 3. samples/multi.txt (5 edits, multiple authors)

**File content:**
```
<!-- EDIT: 2024-01-01T00:00:00Z | AUTHOR: user1 | TYPE: create -->
Project kickoff

<!-- EDIT: 2024-01-02T12:00:00Z | AUTHOR: user2 | TYPE: add -->
Detailed planning phase

<!-- EDIT: 2024-01-03T08:30:00Z | AUTHOR: user1 | TYPE: modify -->
Updated planning with new requirements

<!-- EDIT: 2024-01-04T15:45:00Z | AUTHOR: user3 | TYPE: add -->
Development begins

<!-- EDIT: 2024-01-05T09:15:00Z | AUTHOR: user2 | TYPE: add -->
First feature complete
```

**Expected JSON structure:**

```json
{
  "extraction_metadata": {
    "file": "samples/multi.txt"
  },
  "version_history": {
    "edit_count": 5,
    "edits": [
      {
        "node_id": "edit_20240101T000000Z_0",
        "author": "user1",
        "edit_type": "create",
        "timestamp": "2024-01-01T00:00:00Z",
        "content_after": "Project kickoff"
      },
      {
        "node_id": "edit_20240102T120000Z_0",
        "author": "user2", 
        "edit_type": "add",
        "timestamp": "2024-01-02T12:00:00Z",
        "content_after": "Detailed planning phase"
      },
      {
        "node_id": "edit_20240103T083000Z_0",
        "author": "user1",
        "edit_type": "modify",
        "timestamp": "2024-01-03T08:30:00Z",
        "content_after": "Updated planning with new requirements"
      },
      {
        "node_id": "edit_20240104T154500Z_0",
        "author": "user3",
        "edit_type": "add",
        "timestamp": "2024-01-04T15:45:00Z",
        "content_after": "Development begins"
      },
      {
        "node_id": "edit_20240105T091500Z_0",
        "author": "user2",
        "edit_type": "add",
        "timestamp": "2024-01-05T09:15:00Z",
        "content_after": "First feature complete"
      }
    ]
  },
  "knowledge_graph": {
    "total_nodes": 5,
    "total_edges": 4,
    "edges": [
      {"source": "edit_20240101T000000Z_0", "target": "edit_20240102T120000Z_0", "relationship": "adds_to"},
      {"source": "edit_20240102T120000Z_0", "target": "edit_20240103T083000Z_0", "relationship": "adds_to"},
      {"source": "edit_20240103T083000Z_0", "target": "edit_20240104T154500Z_0", "relationship": "adds_to"},
      {"source": "edit_20240104T154500Z_0", "target": "edit_20240105T091500Z_0", "relationship": "adds_to"}
    ]
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

---

### 4. samples/multi_edit_text.txt (from samples4 - 7 edits)

**File content:** (includes creates, adds, deletes, references to images)

**Expected JSON structure:**

- **version_history.edit_count**: 7
- **knowledge_graph.total_nodes**: 7
- **knowledge_graph.total_edges**: 6
- **confidence_distribution.high**: 7

---

## Validation Queries

Verify your results with these one-liners:

```bash
# Validate test.txt
python3 -c "
import json
with open('results/output.json') as f:
    data = json.load(f)
print(f'Edits: {data[\"summary\"][\"total_edits\"]} (expected: 3)')
print(f'Nodes: {data[\"knowledge_graph\"][\"total_nodes\"]} (expected: 3)')
print(f'Edges: {data[\"knowledge_graph\"][\"total_edges\"]} (expected: 2)')
print(f'High confidence: {data[\"summary\"][\"confidence_distribution\"][\"high\"]} (expected: 3)')
print(f'Sources: {data[\"summary\"][\"sources_used\"]} (expected: [\"embedded_marker\"])')
"
```

```bash
# Validate multi.txt
python3 -c "
import json
with open('results/multi.json') as f:
    data = json.load(f)
assert data['summary']['total_edits'] == 5
assert data['knowledge_graph']['total_nodes'] == 5
assert data['knowledge_graph']['total_edges'] == 4
assert data['summary']['confidence_distribution']['high'] == 5
print('multi.txt validation PASSED')
"
```

---

## Common Issues and Fixes

| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| `total_edits = 1` (should be more) | Markers not detected | Check marker syntax: `<!-- EDIT: [timestamp] | AUTHOR: [name] | TYPE: [action] -->` |
| `total_edges = 0` (should be N-1) | Edit detection working but edge creation failed | Check timestamps are in ISO format |
| `confidence = low` for all | Falling back to filesystem only | Add embedded markers |
| `sources_used = ["filesystem"]` only | No markers or git detected | Add markers or enable git |
| `author = null` for all | AUTHOR field missing from markers | Add AUTHOR to each marker |

---

## Graph Structure Verification

The knowledge graph should have:
- **N nodes** for N edits
- **N-1 edges** connecting edits in chronological order
- **source -> target** direction: earlier edits point to later edits
- **relationship**: `adds_to` for most cases, `replaces` for delete+add patterns

Visual verification (prettified JSON):
```bash
python3 -c "
import json
with open('results/output.json') as f:
    data = json.load(f)
print('NODES:')
for node in data['knowledge_graph']['nodes']:
    print(f'  {node[\"node_id\"]}: {node[\"edit_type\"]} by {node[\"author\"]} at {node[\"timestamp\"]}')
print('EDGES:')
for edge in data['knowledge_graph']['edges']:
    print(f'  {edge[\"source\"]} -> {edge[\"target\"]} ({edge[\"relationship\"]})')
"
```

---

## Success Criteria

Your prototype is working correctly when:

1. ✓ `test.txt` produces 3 edits, 3 nodes, 2 edges, all high confidence
2. ✓ `plain.txt` produces 1 edit, 1 node, 0 edges, low confidence  
3. ✓ `multi.txt` produces 5 edits, 5 nodes, 4 edges, all high confidence
4. ✓ No errors when processing any of these files
5. ✓ JSON output is valid and parseable
6. ✓ All timestamps are preserved from markers
7. ✓ All authors are preserved from markers

Once you see these results, the prototype is ready for extension to other file types.
