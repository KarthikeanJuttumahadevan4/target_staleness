---
format: html
---

# Word Document with Track Changes

**Filename**: `tracked_changes.docx`  
**Type**: Microsoft Word Document  
**Extraction Method**: Word track changes XML parsing  
**Expected Edits**: 3+  
**Expected Nodes**: 3+  
**Expected Edges**: 2+  
**Confidence**: High  
**Creation Difficulty**: ⭐⭐ Medium (requires Word)

---

## 📋 Overview

Microsoft Word documents can track **every change** made to the document using the **Track Changes** feature. This allows us to:
- ✅ Track individual image insertions and deletions
- ✅ Get exact timestamps for each change
- ✅ Get the author of each change
- ✅ Reconstruct the complete edit history

---

## 🎯 Creation Steps

### Step 1: Create a New Word Document

1. Open **Microsoft Word** (or LibreOffice Writer)
2. Create a new blank document

### Step 2: Enable Track Changes

**Microsoft Word:**
1. Go to the **Review** tab
2. Click **Track Changes** to enable it
3. Ensure it shows "Track Changes: On"

**LibreOffice Writer:**
1. Go to **Edit** → **Track Changes** → **Record**
2. Ensure changes are being tracked

### Step 3: Make Initial Edit (Create Document)

Type the following and **SAVE** the document (Ctrl+S):

```
Project Report

This is the initial document.
```

**Note**: Don't close the document, just save it.

### Step 4: Add First Image (Edit 1)

1. Place cursor after "This is the initial document."
2. Go to **Insert** → **Pictures** → **This Device**
3. Select any image file (e.g., a screenshot or photo)
4. Click **Insert**
5. Below the image, add text: "Added first image."
6. **SAVE** the document

### Step 5: Add Second Image (Edit 2)

1. Place cursor at the end of the document
2. Go to **Insert** → **Pictures** → **This Device**
3. Select a **different** image file
4. Click **Insert**
5. Below the image, add text: "Added second image."
6. **SAVE** the document

### Step 6: Modify Text (Edit 3)

1. Change "Project Report" to "Project Report v1.0"
2. **SAVE** the document

### Step 7: Delete First Image (Edit 4)

1. Select the first image you inserted
2. Press **Delete** key
3. **SAVE** the document

### Step 8: Accept All Changes (Optional)

**IMPORTANT**: For best extraction results, **DO NOT** accept changes. Keep them as tracked changes.

If you accidentally accept changes, you can:
1. Go to **Review** → **Track Changes** → **Show Markup**
2. Make sure all changes are visible

### Step 9: Save Final Document

1. Go to **File** → **Save As**
2. Choose location: `min Samples4/` folder
3. Filename: `tracked_changes.docx`
4. Format: **Word Document (.docx)**
5. Click **Save**

---

## ✅ Verification

After creating the file, verify it:

```bash
# Check file exists
ls -la samples4/tracked_changes.docx

# Check file size (should be > 20KB)
ls -lh samples4/tracked_changes.docx

# Check it's a valid Word document
file samples4/tracked_changes.docx  # Should say: "Microsoft Word 2007+"
```

---

## 📋 Manual Creation (Alternative)

If you don't have Word, you can create a simple DOCX file manually. A `.docx` file is just a ZIP archive with XML files inside.

```bash
# Navigate to samples4
cd samples4

# Create a directory for the docx
mkdir -p tracked_changes_temp/word

# Create document.xml with track changes
cat > tracked_changes_temp/word/document.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r>
        <w:t>Project Report v1.0</w:t>
      </w:r>
    </w:p>
    <w:p>
      <w:r>
        <w:t>This is the initial document.</w:t>
      </w:r>
    </w:p>
    <w:p>
      <w:r>
        <w:t>Added first image.</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>
EOF

# Create [Content_Types].xml
cat > tracked_changes_temp/[Content_Types].xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="docx" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
EOF

# Create _rels/.rels
mkdir -p tracked_changes_temp/_rels
cat > tracked_changes_temp/_rels/.rels << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
EOF

# Create the actual docx file
cd tracked_changes_temp
zip -r ../tracked_changes.docx *
cd ..
rm -rf tracked_changes_temp

# Verify
file tracked_changes.docx
```

**Note**: This creates a basic DOCX but without actual track changes. For real track changes, use Word.

---

## 🔍 Expected Extraction Results

### Command to Run

```bash
python extract.py samples4/tracked_changes.docx --output results/tracked_changes.json
```

### Expected Output Structure

```json
{
  "extraction_metadata": {
    "file": "samples4/tracked_changes.docx",
    "timestamp": "2026-10-05T...",
    "extractor_version": "1.0.0"
  },
  "version_history": {
    "edits": [
      {
        "node_id": "edit_001",
        "timestamp": "2024-02-02T10:00:00Z",  // Approximate time
        "author": "Your Name",
        "edit_type": "create",
        "description": "Initial document creation",
        "source": "word_track_changes",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_002",
        "timestamp": "2024-02-02T10:05:00Z",
        "author": "Your Name",
        "edit_type": "add",
        "description": "Inserted image 1",
        "content_after": "[Image]",
        "source": "word_track_changes",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_003",
        "timestamp": "2024-02-02T10:10:00Z",
        "author": "Your Name",
        "edit_type": "add",
        "description": "Inserted image 2",
        "content_after": "[Image]",
        "source": "word_track_changes",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_004",
        "timestamp": "2024-02-02T10:15:00Z",
        "author": "Your Name",
        "edit_type": "modify",
        "description": "Modified title",
        "content_before": "Project Report",
        "content_after": "Project Report v1.0",
        "source": "word_track_changes",
        "evaluation_band": "high"
      },
      {
        "node_id": "edit_005",
        "timestamp": "2024-02-02T10:20:00Z",
        "author": "Your Name",
        "edit_type": "delete",
        "description": "Deleted image 1",
        "content_before": "[Image]",
        "source": "word_track_changes",
        "evaluation_band": "high"
      }
    ]
  },
  "knowledge_graph": {
    "nodes": 5,
    "edges": 4,
    "total_nodes": 5,
    "total_edges": 4
  },
  "summary": {
    "total_edits": 5,
    "sources_used": ["word_track_changes"],
    "confidence_distribution": {"high": 5}
  }
}
```

---

## 📊 Validation Rules

| Check | Expected | Notes |
|-------|----------|-------|
| Number of edits | 3-5 | Depends on changes made |
| Number of nodes | Same as edits | | |
| Number of edges | edits - 1 | | |
| Timestamps present | ✅ | From Word track changes |
| Authors present | ✅ | From Word track changes |
| All confidence high | ✅ | Word track changes = high confidence |
| Source is word_track_changes | ✅ | | |

---

## 🔧 Troubleshooting

### Issue: python-docx not installed
**Error**: `ModuleNotFoundError: No module named 'docx'`

**Solution**:
```bash
pip install python-docx
```

### Issue: No track changes found
**Error**: No edits extracted, or source is "filesystem"

**Solution**:
1. Make sure Track Changes was **enabled** when making edits
2. Make sure changes were **NOT accepted**
3. Try creating a new document with fresh track changes
4. In Word, check that you can see the track changes (red/green markings)

### Issue: Can't parse Word XML
**Error**: `lxml not found` or XML parsing errors

**Solution**:
```bash
pip install lxml
```

### Issue: Word file not detected
**Error**: File type not recognized as Word

**Solution**:
```bash
# Check file type
file samples4/tracked_changes.docx

# Should be: Microsoft Word 2007+
# If not, the file was not saved correctly
```

---

## 🎓 Key Concepts Demonstrated

This test file demonstrates:

1. **Word document parsing** - Reading .docx ZIP structure
2. **Track changes extraction** - Parsing Word's XML markup
3. **Image insertion tracking** - Detecting embedded images
4. **Author extraction** - Getting author from revision history
5. **Timestamp extraction** - Getting exact change times
6. **Multi-edit tracking** - Tracking multiple types of changes
7. **Change type classification** - create, add, modify, delete
8. **Binary file handling** - Reading complex file format
9. **High confidence extraction** - Word track changes are very reliable
10. **Knowledge graph construction** - Nodes and edges from Word history

---

## 📚 Technical Details

### Word Document Structure

A `.docx` file is a **ZIP archive** containing:
```
tracked_changes.docx
├── [Content_Types].xml
├── _rels/
│   └── .rels
├── word/
│   ├── document.xml        # ← Main content + track changes
│   ├── footer1.xml
│   ├── header1.xml
│   ├── settings.xml
│   └── _rels/
│       └── document.xml.rels
└── docProps/
    ├── app.xml
    ├── core.xml            # ← Document metadata (author, dates)
    └── thumbnail.jpeg
```

### Track Changes in document.xml

Word stores track changes using special XML elements:
```xml
<!-- Inserted text -->
<w:ins w:id="1" w:author="John Doe" w:date="2024-02-02T10:00:00Z">
  <w:t>inserted text</w:t>
</w:ins>

<!-- Deleted text -->
<w:del w:id="2" w:author="John Doe" w:date="2024-02-02T10:05:00Z">
  <w:t>deleted text</w:t>
</w:del>

<!-- Modified text (delete old + insert new) -->
<w:del w:id="3" ...>old</w:del>
<w:ins w:id="4" ...>new</w:ins>

<!-- Inserted image -->
<w:drawing>
  <w:inline>
    <w:extent cx="1000000" cy="1000000"/>
    <w:docPr id="2" name="Picture 1"/>
    ...
  </w:inline>
</w:drawing>
```

---

## 🚀 Next Steps

After this file works:

1. ✅ **Current**: Word document with track changes
2. **Previous**: [Text File with Embedded Markers](multi_edit_text.md)
3. **Next**: [PDF with Metadata](metadata_pdf.md)
4. **Then**: [Image with EXIF](exif_image.md)
5. **Then**: [Audio with ID3 Tags](sample_audio.md)
6. **Then**: [Video with Metadata](sample_video.md)
7. **Then**: [Git Version History](git_history.md)

---

## 💡 Tips

1. **Always enable Track Changes** before making edits
2. **Save frequently** to preserve change history
3. **Don't accept changes** until you've extracted
4. **Use meaningful text** so changes are clear
5. **Test with different authors** (if multiple users available)

---

**Word documents with Track Changes provide the richest edit history information. This is one of the most valuable test cases.**
