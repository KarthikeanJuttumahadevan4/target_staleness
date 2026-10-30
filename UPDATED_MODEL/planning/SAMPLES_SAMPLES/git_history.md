# Git Version History

**Filename**: `samples4_git/evolution.txt` (file in git repo)  
**Type**: Text file with git commit history  
**Extraction Method**: Git log parsing  
**Expected Nodes**: 4  
**Expected Edges**: 3  
**Confidence**: High (when git integration is enabled)  
**Creation Difficulty**: ⭐⭐ Medium

---

## 📋 Overview

Git repositories store **complete commit history** including:
- Commit messages
- Author names and emails
- Timestamps (author date, commit date)
- Diffs (what changed in each commit)
- Parent commits (for branching)

The extractor can use this to build a **complete knowledge graph** of all changes to the file.

---

## 🎯 Creation Steps

### Step 1: Create Git Repository

```bash
# Navigate to samples4 directory
cd samples4

# Create git repository directory
mkdir samples4_git
cd samples4_git

# Initialize git repository
git init

# Set up author information
git config user.name "Test User"
git config user.email "test@example.com"
```

### Step 2: Create Initial Commit (Feb 1, 8:00 AM)

```bash
# Create initial file
echo "Initial content" > evolution.txt

# Add and commit
git add evolution.txt
git commit -m "Initial commit" --date="2024-02-01T08:00:00Z"
```

### Step 3: Add Section 1 (Feb 2, 9:00 AM, Author: Alice)

```bash
# Append to file
echo -e "Initial content\n\nAdded section 1" > evolution.txt

# Add and commit with specific author and date
git add evolution.txt
git commit -m "Add section 1" \
  --date="2024-02-02T09:00:00Z" \
  --author="Alice <alice@example.com>"
```

### Step 4: Modify Section 1 and Add Section 2 (Feb 3, 10:00 AM, Author: Bob)

```bash
# Modify content
echo -e "Initial content\n\nModified section 1\n\nAdded section 2" > evolution.txt

git add evolution.txt
git commit -m "Modify section 1, add section 2" \
  --date="2024-02-03T10:00:00Z" \
  --author="Bob <bob@example.com>"
```

### Step 5: Remove Temporary Note (Feb 4, 11:00 AM, Author: Alice)

```bash
# Final content (no temp note)
echo -e "Initial content\n\nModified section 1\n\nAdded section 2" > evolution.txt

git add evolution.txt
git commit -m "Remove temp note" \
  --date="2024-02-04T11:00:00Z" \
  --author="Alice <alice@example.com>"
```

### Step 6: Verify Git History

```bash
# View commit history
git log --pretty=format:"%h | %an | %aI | %s" -- evolution.txt
```

**Expected Output**:
```
abc1234 | Alice <alice@example.com> | 2024-02-04T11:00:00Z | Remove temp note
def5678 | Bob <bob@example.com> | 2024-02-03T10:00:00Z | Modify section 1, add section 2
ghi9012 | Alice <alice@example.com> | 2024-02-02T09:00:00Z | Add section 1
jkl3456 | Test User <test@example.com> | 2024-02-01T08:00:00Z | Initial commit
```

### Step 7: Go Back to Project Root

```bash
cd ..
# Now in samples4/
```

---

## 🔍 File Verification

```bash
# Check git repository exists
ls -la samples4/samples4_git/.git

# Check evolution.txt exists
ls -la samples4/samples4_git/evolution.txt

# Count commits
git -C samples4/samples4_git log --oneline evolution.txt | wc -l  # Should be 4

# Verify commit dates
git -C samples4/samples4_git log --pretty=format:"%aI %s" -- evolution.txt
```

---

## 🎯 Extraction Commands

### Basic Version
```bash
python extract.py samples4/samples4_git/evolution.txt --output results/evolution.json
```

**Note**: The basic version doesn't read git history's, so it will only get filesystem metadata.

### Expected Output (Basic - Filesystem Only)
```json
{
  "extraction_metadata": {
    "file": "samples4/samples4_git/evolution.txt",
    "timestamp": "2026-10-05T16:40:00Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": 56,
      "created_time": "2026-10-05T16:35:00Z",
      "modified_time": "2026-10-05T16:35:00Z",
      "accessed_time": "2026-10-05T16:40:00Z"
    },
    "file_type": "text/plain"
  },
  "version_history": {
    "edits": [
      {
        "node_id": "fs_evolution.txt",
        "node_type": "edit",
        "timestamp": "2026-10-05T16:35:00Z",
        "author": null,
        "edit_type": "create",
        "content_after": "Initial content...",
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
    "sources_used": ["filesystem"],
    "confidence_distribution": {"low": 1}
  }
}
```

### Full Version (with GitPython)
```bash
pip install GitPython

# Then run with full extract.py that includes git extractor
python extract.py samples4/samples4_git/evolution.txt --git-repo samples4/samples4_git --output results/evolution_full.json
```

### Expected Output (Full)
```json
{
  "extraction_metadata": {
    "file": "samples4/samples4_git/evolution.txt",
    "git_repo_path": "samples4/samples4_git",
    "timestamp": "2026-10-05T16:45:00Z",
    "extractor_version": "1.0.0"
  },
  "file_metadata": {
    "filesystem": {
      "size_bytes": 56,
      "created_time": "2026-10-05T16:35:00Z",
      "modified_time": "2026-10-05T16:35:00Z",
      "accessed_time": "2026-10-05T16:40:00Z"
    },
    "file_type": "text/plain",
    "text": {
      "character_count": 56,
      "line_count": 4,
      "word_count": 8
    }
  },
  "version_history": {
    "edits": [
      {
        "node_id": "git_jkl3456",
        "timestamp": "2024-02-01T08:00:00Z",
        "author": "Test User <test@example.com>",
        "edit_type": "create",
        "commit_hash": "jkl3456abc789",
        "message": "Initial commit",
        "content_after": "Initial content",
        "source": "git",
        "evaluation_band": "high"
      },
      {
        "node_id": "git_ghi9012",
        "timestamp": "2024-02-02T09:00:00Z",
        "author": "Alice <alice@example.com>",
        "edit_type": "add",
        "commit_hash": "ghi9012def123",
        "message": "Add section 1",
        "content_before": "Initial content",
        "content_after": "Initial content\n\nAdded section 1",
        "source": "git",
        "evaluation_band": "high"
      },
      {
        "node_id": "git_def5678",
        "timestamp": "2024-02-03T10:00:00Z",
        "author": "Bob <bob@example.com>",
        "edit_type": "modify",
        "commit_hash": "def5678ghi456",
        "message": "Modify section 1, add section 2",
        "content_before": "Added section 1",
        "content_after": "Modified section 1\n\nAdded section 2",
        "source": "git",
        "evaluation_band": "high"
      },
      {
        "node_id": "git_abc1234",
        "timestamp": "2024-02-04T11:00:00Z",
        "author": "Alice <alice@example.com>",
        "edit_type": "delete",
        "commit_hash": "abc1234jkl567",
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
    "nodes": [
      {
        "node_id": "git_jkl3456",
        "node_type": "edit",
        "timestamp": "2024-02-01T08:00:00Z",
        "author": "Test User <test@example.com>",
        "edit_type": "create",
        "commit_hash": "jkl3456abc789",
        "message": "Initial commit",
        "source": "git",
        "evaluation_band": "high"
      },
      {
        "node_id": "git_ghi9012",
        "node_type": "edit",
        "timestamp": "2024-02-02T09:00:00Z",
        "author": "Alice <alice@example.com>",
        "edit_type": "add",
        "commit_hash": "ghi9012def123",
        "message": "Add section 1",
        "source": "git",
        "evaluation_band": "high"
      },
      {
        "node_id": "git_def5678",
        "node_type": "edit",
        "timestamp": "2024-02-03T10:00:00Z",
        "author": "Bob <bob@example.com>",
        "edit_type": "modify",
        "commit_hash": "def5678ghi456",
        "message": "Modify section 1, add section 2",
        "source": "git",
        "evaluation_band": "high"
      },
      {
        "node_id": "git_abc1234",
        "node_type": "edit",
        "timestamp": "2024-02-04T11:00:00Z",
        "author": "Alice <alice@example.com>",
        "edit_type": "delete",
        "commit_hash": "abc1234jkl567",
        "message": "Remove temp note",
        "source": "git",
        "evaluation_band": "high"
      }
    ],
    "edges": [
      {
        "edge_id": "edge_git_jkl3456_git_ghi9012",
        "source": "git_jkl3456",
        "target": "git_ghi9012",
        "edge_type": "temporal",
        "relationship": "adds_to",
        "timestamp": "2024-02-02T09:00:00Z",
        "weight": 1.0
      },
      {
        "edge_id": "edge_git_ghi9012_git_def5678",
        "source": "git_ghi9012",
        "target": "git_def5678",
        "edge_type": "temporal",
        "relationship": "modifies",
        "timestamp": "2024-02-03T10:00:00Z",
        "weight": 1.0
      },
      {
        "edge_id": "edge_git_def5678_git_abc1234",
        "source": "git_def5678",
        "target": "git_abc1234",
        "edge_type": "temporal",
        "relationship": "removes_from",
        "timestamp": "2024-02-04T11:00:00Z",
        "weight": 1.0
      }
    ],
    "total_nodes": 4,
    "total_edges": 3
  },
  "summary": {
    "total_edits": 4,
    "total_nodes": 4,
    "total_edges": 3,
    "sources_used": ["git"],
    "confidence_distribution": {
      "high": 4,
      "medium": 0,
      "low": 0
    }
  }
}
```

---

## 📊 Validation Commands

```bash
# Check commit count
git -C samples4/samples4_git log --oneline evolution.txt | wc -l

# Check git extraction (full version only)
python -c "
import json
d = json.load(open('results/evolution_full.json'))
kg = d['knowledge_graph']
print(f'Nodes: {kg[\"total_nodes\"]} (expected: 4)')
print(f'Edges: {kg[\"total_edges\"]} (expected: 3)')
print(f'Source: {d[\"summary\"][\"sources_used\"]}')

# Check timestamps
for node in kg['nodes']:
    print(f'  {node[\"timestamp\"]}: {node[\"edit_type\"]} by {node[\"author\"]}')
"
```

---

## 🎓 Key Concepts Demonstrated

1. **Git history extraction** - Reading commit history from repositories
2. **Commit metadata** - Author, timestamp, message, hash
3. **Diff extraction** - What changed between commits
4. **Multi-author tracking** - Different authors for different commits
5. **Temporal sequence** - Complete chronological history
6. **High confidence data** - Git history is very reliable
7. **Knowledge graph construction** - Full graph with proper edges

---

## 💡 Tips

1. **Use `--date` flag** to set specific commit timestamps
2. **Use `--author` flag** to set different authors
3. **Commit frequently** to create rich history
4. **Don't squash commits** for testing
5. **Use meaningful messages** for easier debugging

---

## ⚠️ Common Issues

### Issue: Git repository not found
**Symptom**: Error that git repo doesn't exist

**Solution**: Use `--git-repo` flag to specify path: `python extract.py file.txt --git-repo /path/to/repo`

### Issue: GitPython not installed
**Symptom**: `ModuleNotFoundError: No module named 'git'`

**Solution**: `pip install GitPython`

### Issue: No commits found
**Symptom**: No edits extracted even with git repo

**Solution**: Check that file is in the git repo and has commit history:
```bash
git -C /path/to/repo log --oneline filename
```

### Issue: Wrong timestamps
**Symptom**: Timestamps are current time, not commit times

**Solution**: Make sure to use `--date` flag when creating commits

---

## 🔗 Related

- **Previous**: [Video with Metadata](sample_video.md)
- **mentation**: ALL SAMPLE FILES COMPLETE!
- **Full Specs**: [../../artifacts/specs.md](../../artifacts/specs.md)
- **Version Extractor**: [../../artifacts/version_history_extractor.md](../../artifacts/version_history_extractor.md)

---

**Git repositories provide the richest version history information. With proper commit timestamps and authors, you can reconstruct a complete timeline of changes to any file.**
