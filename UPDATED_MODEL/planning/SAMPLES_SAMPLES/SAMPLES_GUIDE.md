---
format: html
---

# samples4 Directory - Complete Sample File Guide

This directory contains **sample files for testing** the Universal File Metadata & Version History Extractor.

## 📁 Current Structure

```
samples4/
├── README.md                             # This directory overview
├── SAMPLES_GUIDE.md                      # This file - creation guide
├── multi_edit_text.md                    # Text file with embedded markers
├── tracked_changes_docx.md               # Word doc instructions
├── metadata_pdf.md                       # PDF instructions
├── exif_image.md                         # Image instructions  
├── sample_audio.md                       # Audio instructions
├── sample_video.md                       # Video instructions
└── git_history.md                        # Git repo instructions
```

## 🎯 Quick Setup

To create ALL sample files and run the extractor:

```bash
# Step 1: Create samples4 directory
cd samples4

# Step 2: Create text file (directly)
cat > multi_edit_text.txt << 'EOF'
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create | SECTION: header -->
# Project Report
Initial content.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: bob | TYPE: add | SECTION: intro -->
## Introduction
Added introduction.
EOF

# Step 3: Create other files (follow instructions below for each)
# Step 4: Run extractor on all files
# See RUN_SCRIPT.md for extraction commands
```

---

## 📄 Sample Files Index

| File Type | Filename | Extraction Method | Edits/History | Creation Difficulty |
|-----------|----------|-------------------|---------------|-------------------|
| **Text (with markers)** | `multi_edit_text.txt` | Embedded markers | 5 edits | ⭐ Easy |
| **Word (track changes)** | `tracked_changes.docx` | Word XML parsing | 3+ edits | ⭐⭐ Medium |
| **PDF (metadata)** | `metadata.pdf` | PDF metadata | 1 document | ⭐⭐ Medium |
| **Image (EXIF)** | `exif_image.jpg` | EXIF metadata | 1 image | ⭐ Easy |
| **Audio (ID3 tags)** | `sample_audio.mp3` | Audio metadata | 1 audio | ⭐⭐ Medium |
| **Video (metadata)** | `sample_video.mp4` | Video metadata | 1 video | ⭐⭐ Medium |
| **Git (version history)** | `evolution.txt` + git | Git log parsing | 4 commits | ⭐⭐ Medium |

---

## 📝 Detail Pages

Each sample type has its own detailed instruction page:

1. **[Text File with Embedded Markers](multi_edit_text.md)** - Easiest, no special tools needed
2. **[Word Document with Track Changes](tracked_changes_docx.md)** - Use Word's built-in tracking
3. **[PDF with Metadata](metadata_pdf.md)** - Create with any PDF tool
4. **[Image with EXIF](exif_image.md)** - Use your phone or camera
5. **[Audio with ID3 Tags](sample_audio.md)** - Record or use existing audio
6. **[Video with Metadata](sample_video.md)** - Record or use existing video
7. **[Git Version History](git_history.md)** - Create a git repository

---

## 🚀 File Creation Summary

### 1️⃣ Text File (multi_edit_text.txt)
**Creation**: Just copy-paste text with markers  
**Time**: 2 minutes  
**Required**: Text editor  

### 2️⃣ Word Document (tracked_changes.docx)
**Creation**: Use Microsoft Word with Track Changes enabled  
**Time**: 5 minutes  
**Required**: Microsoft Word or LibreOffice  

### 3️⃣ PDF File (metadata.pdf)
**Creation**: Create PDF with embedded metadata  
**Time**: 3 minutes  
**Required**: PDF creator (Word, LibreOffice, etc.)  

### 4️⃣ Image File (exif_image.jpg)
**Creation**: Take photo or use camera app  
**Time**: 1 minute (taking a photo)  
**Required**: Camera/phone  

### 5️⃣ Audio File (sample_audio.mp3)
**Creation**: Record audio or use conversion tool  
**Time**: 2 minutes  
**Required**: Audio recorder or online converter  

### 6️⃣ Video File (sample_video.mp4)
**Creation**: Record video or use existing file  
**Time**: 1 minute (recording)  
**Required**: Camera/phone  

### 7️⃣ Git Repository (evolution.txt)
**Creation**: Create git repo with multiple commits  
**Time**: 5 minutes  
**Required**: Git installed  

---

## 🔧 Required Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| **Text Editor** | Create text files | Pre-installed |
| **Microsoft Word** | Create Word docs with track changes | Office suite |
| **LibreOffice** | Free alternative to Word | `sudo apt install libreoffice` |
| **Any PDF Creator** | Create PDF with metadata | Various |
| **Camera** | Create images with EXIF | Built-in or phone |
| **Audio Recorder** | Create audio files | Various |
| **FFmpeg** | Convert audio/video formats | `sudo apt install ffmpeg` |
| **Git** | Version control | `sudo apt install git` |

---

## ⚙️ Extraction Commands

Once all files are created:

```bash
# Extract all files
for file in samples4/*; do
    echo "=== Extracting: $file ==="
    python extract.py "$file" --output "results/$(basename $file).json"
done

# Or individually
python extract.py samples4/multi_edit_text.txt --output results/text.json
python extract.py samples4/tracked_changes.docx --output results/word.json
python extract.py samples4/metadata.pdf --output results/pdf.json
python extract.py samples4/exif_image.jpg --output results/image.json
python extract.py samples4/sample_audio.mp3 --output results/audio.json
python extract.py samples4/sample_video.mp4 --output results/video.json
python extract.py samples4/evolution.txt --git-repo samples4_git --output results/git.json
```

---

## 📊 Expected Results Summary

| File | Expected Nodes | Expected Edges | Confidence | Key Findings |
|------|---------------|----------------|------------|--------------|
| Text with markers | 5 | 4 | High | Edit history from markers |
| Word with track changes | 3+ | 2+ | High | Word revision history |
| PDF with metadata | 1 | 0 | Medium | Document metadata |
| Image with EXIF | 1 | 0 | High | EXIF timestamps |
| Audio with ID3 | 1 | 0 | Medium | Audio metadata |
| Video with metadata | 1 | 0 | Medium | Video metadata |
| Git version history | 4 | 3 | High | Git commit history |

---

## 🎯 Next Steps

1. **Start with the easiest**: Create `multi_edit_text.txt` (2 minutes)
2. **Test extraction**: `python extract.py samples4/multi_edit_text.txt`
3. **Add one file at a time**: Follow each guide
4. **Verify results**: Check JSON output for expected data

---

## 📖 Documentation

- **Project README**: [../README.md](../README.md) - Full project overview
- **Proposal**: [../artifacts/proposal.md](../artifacts/proposal.md) - Project design
- **Specifications**: [../artifacts/specs.md](../artifacts/specs.md) - Technical details
- **Quick Start**: [../QUICKSTART.md](../QUICKSTART.md) - 2-hour MVP guide

---

**All sample files are designed to test specific aspects of the extractor. Start with text files (easiest), then progress to more complex formats.**
