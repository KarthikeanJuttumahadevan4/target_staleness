---
format: html
---

# multi_edit_text.txt - Test File Content

This file contains the content for `samples4/text_files/multi_edit_text.txt`.
Copy this content (excluding the markdown formatting) to create the actual text file.

**Important**: When creating the actual file, ensure it uses plain text format with the embedded markers exactly as shown below.

---

## File Content (multi_edit_text.txt)

```text
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: user1 | TYPE: create | SECTION: document_root | DESCRIPTION: Initial file creation -->
# Project Documentation

This is the initial version of the project documentation.
The project aims to create a universal file extractor.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: user2 | TYPE: add | SECTION: introduction | DESCRIPTION: Added introduction section -->
## Introduction

This section provides an overview of the project.
The extractor can handle multiple file formats simultaneously.

## Features

- Multi-format support
- Version history tracking
- Knowledge graph generation

<!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: user1 | TYPE: modify | SECTION: title | DESCRIPTION: Updated title to include version -->
# Project Documentation v1.0

This is the UPDATED version of the project documentation.
The project aims to create a universal file extractor.

## Introduction

This section provides an overview of the project.
The extractor can handle multiple file formats simultaneously.

## Features

- Multi-format support
- Version history tracking
- Knowledge graph generation

<!-- EDIT: 2024-02-04T14:20:00Z | AUTHOR: user1 | TYPE: delete | SECTION: temp_notes | DESCRIPTION: Removed temporary notes -->
# TEMPORARY NOTES - REMOVE THIS
This is temporary content that should be deleted.
The project aims to create a universal file extractor.

<!-- EDIT: 2024-02-04T14:20:00Z | AUTHOR: user1 | TYPE: add | SECTION: features | DESCRIPTION: Added performance features -->
## Performance Features

The extractor is optimized for:
- Fast processing of small files
- Parallel extraction for large files
- Memory-efficient streaming

<!-- EDIT: 2024-02-05T16:45:00Z | AUTHOR: user3 | TYPE: add | SECTION: conclusion | DESCRIPTION: Added conclusion section -->
## Conclusion

This documentation covers the main features of the extractor.
For more information, please refer to the technical specifications.
The project is actively maintained and updated regularly.
```

---

## Expected Knowledge Graph Structure

This file should produce **6 edit nodes** connected by **5 edges**:

### Nodes:

1. **edit_20240202T203100Z_0** (create)
   - Timestamp: 2024-02-02T20:31:00Z
   - Author: user1
   - Type: create
   - Content After: Initial file content
   - Section: document_root

2. **edit_20240203T192900Z_1** (add)
   - Timestamp: 2024-02-03T19:29:00Z
   - Author: user2
   - Type: add
   - Content After: Introduction section
   - Section: introduction

3. **edit_20240204T101500Z_2** (modify)
   - Timestamp: 2024-02-04T10:15:00Z
   - Author: user1
   - Type: modify
   - Content Before: "# Project Documentation"
   - Content After: "# Project Documentation v1.0"
   - Section: title

4. **edit_20240204T142000Z_3** (delete)
   - Timestamp: 2024-02-04T14:20:00Z
   - Author: user1
   - Type: delete
   - Content Before: Temporary notes section
   - Content After: null
   - Section: temp_notes

5. **edit_20240204T142000Z_4** (add)
   - Timestamp: 2024-02-04T14:20:00Z
   - Author: user1
   - Type: add
   - Content After: Performance Features section
   - Section: features

6. **edit_20240205T164500Z_5** (add)
   - Timestamp: 2024-02-05T16:45:00Z
   - Author: user3
   - Type: add
   - Content After: Conclusion section
   - Section: conclusion

### Edges:

1. edit_20240202T203100Z_0 → edit_20240203T192900Z_1 (relationship: adds_to)
2. edit_20240203T192900Z_1 → edit_20240204T101500Z_2 (relationship: successor)
3. edit_20240204T101500Z_2 → edit_20240204T142000Z_3 (relationship: successor)
4. edit_20240204T101500Z_2 → edit_20240204T142000Z_4 (relationship: adds_to)
5. edit_20240204T142000Z_4 → edit_20240205T164500Z_5 (relationship: adds_to)

---

## Validation Steps

After creating the actual `multi_edit_text.txt` file, run:

```bash
# Extract version history
python extract.py samples4/text_files/multi_edit_text.txt

# Expected output:
# - 6 edit nodes
# - 5 edges
# - All timestamps match the markers
# - All content changes correctly identified
```

---

## Creation Instructions

To create the actual test file:

```bash
# 1. Create the directory
mkdir -p samples4/text_files

# 2. Create the file (copy only the content between the ```text ``` markers above)
cat > samples4/text_files/multi_edit_text.txt << 'EOF'
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: user1 | TYPE: create | SECTION: document_root | DESCRIPTION: Initial file creation -->
# Project Documentation

This is the initial version of the project documentation.
The project aims to create a universal file extractor.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: user2 | TYPE: add | SECTION: introduction | DESCRIPTION: Added introduction section -->
## Introduction

This section provides an overview of the project.
The extractor can handle multiple file formats simultaneously.

## Features

- Multi-format support
- Version history tracking
- Knowledge graph generation

<!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: user1 | TYPE: modify | SECTION: title | DESCRIPTION: Updated title to include version -->
# Project Documentation v1.0

This is the UPDATED version of the project documentation.
The project aims to create a universal file extractor.

## Introduction

This section provides an overview of the project.
The extractor can handle multiple file formats simultaneously.

## Features

- Multi-format support
- Version history tracking
- Knowledge graph generation

<!-- EDIT: 2024-02-04T14:20:00Z | AUTHOR: user1 | TYPE: delete | SECTION: temp_notes | DESCRIPTION: Removed temporary notes -->
# TEMPORARY NOTES - REMOVE THIS
This is temporary content that should be deleted.
The project aims to create a universal file extractor.

<!-- EDIT: 2024-02-04T14:20:00Z | AUTHOR: user1 | TYPE: add | SECTION: features | DESCRIPTION: Added performance features -->
## Performance Features

The extractor is optimized for:
- Fast processing of small files
- Parallel extraction for large files
- Memory-efficient streaming

<!-- EDIT: 2024-02-05T16:45:00Z | AUTHOR: user3 | TYPE: add | SECTION: conclusion | DESCRIPTION: Added conclusion section -->
## Conclusion

This documentation covers the main features of the extractor.
For more information, please refer to the technical specifications.
The project is actively maintained and updated regularly.
EOF

# 3. Verify the file
wc -l samples4/text_files/multi_edit_text.txt
grep -c "EDIT:" samples4/text_files/multi_edit_text.txt  # Should return 6
```
