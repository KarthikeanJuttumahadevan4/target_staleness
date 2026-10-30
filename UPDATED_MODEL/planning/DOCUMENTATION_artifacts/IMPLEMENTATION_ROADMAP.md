# Implementation Roadmap

## Project: Universal File Metadata & Version History Extractor

This document outlines the implementation plan, current status, and next steps for the project.

---

## 🎯 Current Status (As of 2026-10-05)

### ✅ **Phase 0: Design & Specification (COMPLETE)**

All design documents have been created:

1. **`artifacts/proposal.md`** - Complete project proposal with:
   - Problem statement
   - User intent
   - Proposed solution architecture
   - Scope definition
   - Evaluation band system
   - Flow pipeline definition
   - Success criteria
   - Implementation phases

2. **`artifacts/specs.md`** - Comprehensive technical specification with:
   - Functional requirements (FR1-FR7)
   - Non-functional requirements (NFR1-NFR5)
   - Constraints
   - Dependencies
   - Open questions
   - Risks
   - Project structure
   - Implementation plan

3. **`artifacts/samples4_design.md`** - Detailed test file specifications:
   - File types and formats
   - Embedded marker syntax
   - Expected knowledge graph structures
   - Validation rules
   - Creation instructions

4. **Updated `README.md`** - Project documentation with:
   - Overview
   - Installation instructions
   - Usage examples
   - Project structure
   - Flow pipeline diagram
   - Evaluation bands
   - knowledge graph structure

---

### 📝 **Phase 1: Documentation & Templates (COMPLETE)**

Python code templates have been created as markdown files:

1. **`artifacts/extraction_engine.md`** - Core extraction engine with:
   - FileMetadata class
   - KnowledgeGraph class
   - FlowPipeline class with all stages
   - 20+ extractor implementations
   - File type detection
   - Multi-model extraction framework

2. **`artifacts/version_history_extractor.md`** - Version history extraction with:
   - EditNode class
   - VersionAnalyzer class
   - 4 extraction methods (embedded markers, git, word, filesystem)
   - KnowledgeGraphBuilder class
   - EvaluationBandAssigner class

3. **`artifacts/main_extractor.md`** - Main entry point with:
   - CLI argument parsing
   - Output format handling
   - JSON, GraphML, GEXF export
   - Integration with all components

4. **`artifacts/validation_script.md`** - Validation framework with:
   - Validator class
   - 8 validation rules
   - JSON output
   - CLI interface

---

### 📁 **Phase 1.5: Test Files (PARTIAL)**

Test file specifications created:

1. **`samples4/README.md`** - Test directory documentation
2. **`samples4/text_files/multi_edit_text.txt.md`** - Test file content template
3. **`samples4/text_files/multi_edit_text.history.json.md`** - Expected results template

**Status**: Templates created, actual files need to be instantiated

---

## 🏗️ Implementation Plan

### Phase 2: Core Infrastructure (Next Priority)

#### Task 2.1: Create Directory Structure
```bash
# Create main directories
mkdir -p extractor/metadata extractor/content extractor/version
mkdir -p graph pipeline evaluation tests
mkdir -p samples4/text_files samples4/documents samples4/images samples4/pdfs
```

#### Task 2.2: Convert .md Templates to .py Files
- [ ] `extract.py` (from artifacts/main_extractor.md)
- [ ] `extractor/__init__.py` (base classes)
- [ ] `extractor/metadata/filesystem.py`
- [ ] `extractor/metadata/pdf.py`
- [ ] `extractor/metadata/word.py`
- [ ] `extractor/version/git.py`
- [ ] `extractor/version/embedded_markers.py`
- [ ] `graph/builder.py`
- [ ] `pipeline/ingestion.py`
- [ ] `tests/validate.py`

**Estimated Time**: 2-4 hours

#### Task 2.3: Create Test Files
- [ ] `samples4/text_files/multi_edit_text.txt` (copy from .md template)
- [ ] `samples4/text_files/multi_edit_text.history.json` (copy from .md template)
- [ ] `samples4/text_files/simple_text.txt` (no markers)
- [ ] Create a git repository with known history for testing

**Estimated Time**: 1 hour

#### Task 2.4: Install Dependencies
```bash
# Install core dependencies
pip install python-magic Pillow PyPDF2 pdfplumber python-docx openpyxl pydub networkx

# Install optional dependencies
pip install pdfminer.six tabula-py gitpython lxml

# Install system dependencies
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr ffmpeg
```

**Estimated Time**: 1-2 hours

---

### Phase 3: Core Functionality (Week 1)

#### Task 3.1: Implement File Ingestion
- [ ] File type detection (extension + magic numbers)
- [ ] File existence validation
- [ ] Git repository detection
- [ ] Basic error handling

**Standalone Test**: 
```bash
python -c "from pipeline.ingestion import ingest_file; result = ingest_file('samples4/text_files/multi_edit_text.txt'); print(result)"
```

#### Task 3.2: Implement Embedded Marker Extraction
- [ ] HTML-style marker parsing
- [ ] YAML-style marker parsing
- [ ] Edit node creation
- [ ] Content extraction between markers

**Standalone Test**:
```bash
python -c "from extractor.version.embedded_markers import extract_from_markers; edits = extract_from_markers(Path('samples4/text_files/multi_edit_text.txt')); print(f'Found {len(edits)} edits')"
```

#### Task 3.3: Implement Knowledge Graph Builder
- [ ] Node creation from edits
- [ ] Edge creation (temporal + content)
- [ ] GraphML export
- [ ] GEXF export

**Standalone Test**:
```bash
python -c "from graph.builder import KnowledgeGraphBuilder; builder = KnowledgeGraphBuilder(); graph = builder.build(edits); print(graph)"
```

#### Task 3.4: Connect Flow Pipeline
- [ ] Stage 1: Ingestion
- [ ] Stage 3: Version Analysis (embedded markers only)
- [ ] Stage 4: Knowledge Graph Construction
- [ ] Stage 6: Output

**Full Test**:
```bash
python extract.py samples4/text_files/multi_edit_text.txt --output result.json
```

**Estimated Time**: 1-2 days

---

### Phase 4: Additional Extractors (Week 2)

#### Task 4.1: Filesystem Metadata Extractor
- [ ] Basic metadata extractors
- [ ] File hashes (MD5, SHA1, SHA256)
- [ ] Magic numbers

#### Task 4.2: Git Version Extractor
- [ ] Git log parsing
- [ ] Patch parsing
- [ ] Edit node creation from commits

#### Task 4.3: PDF Metadata Extractor
- [ ] pdfplumber integration
- [ ] PyPDF2 integration
- [ ] Metadata extraction
- [ ] Text extraction

#### Task 4.4: Word Document Extractor
- [ ] python-docx integration
- [ ] Metadata extraction
- [ ] Content extraction
- [ ] Track changes parsing (basic)

**Standalone Tests**:
```bash
# Test each extractor individually
python -c "from extractor.metadata.filesystem import extract; print(extract('file.txt'))"
python -c "from extractor.version.git import extract; print(extract('file.txt'))"
python -c "from extractor.metadata.pdf import extract; print(extract('file.pdf'))"
```

**Estimated Time**: 2-3 days

---

### Phase 5: Evaluation Band System (Week 2)

#### Task 5.1: Implement Evaluation Band Assignment
- [ ] BandAssigner class
- [ ] Confidence scoring rules
- [ ] Source-based classification

#### Task 5.2: Apply Bands to All Data
- [ ] Metadata confidence
- [ ] Version history confidence
- [ ] Knowledge graph confidence

**Standalone Test**:
```bash
python -c "from evaluation.bands import EvaluationBandAssigner; assigner = EvaluationBandAssigner(); band = assigner.assign_to_edit(edit); print(f'Band: {band}')"
```

**Estimated Time**: 1 day

---

### Phase 6: Multi-Model Extraction (Week 3)

#### Task 6.1: Create Extractor Registry
- [ ] Dynamic extractor discovery
- [ ] Extractor prioritization
- [ ] Fallback mechanisms

#### Task 6.2: Implement All Metadata Extractors
- [ ] Generic extractors (filesystem, magic)
- [ ] PDF extractors (pdfplumber, PyPDF2)
- [ ] Word extractors (python-docx)
- [ ] Excel extractors (openpyxl)
- [ ] Image extractors (Pillow, EXIF)
- [ ] Audio extractors (pydub, mutagen)
- [ ] Video extractors (OpenCV, FFmpeg)
- [ ] Archive extractors (zipfile, tarfile)

#### Task 6.3: Implement Content Extractors
- [ ] Text content extraction
- [ ] PDF text extraction
- [ ] Word content extraction
- [ ] Excel content extraction
- [ ] OCR for images (Tesseract)
- [ ] Audio transcription (Whisper)
- [ ] Video frame extraction

**Full Test**:
```bash
python extract.py samples4/text_files/multi_edit_text.txt --output-format json
# Verify all extractors ran and produced results
```

**Estimated Time**: 3-5 days

---

### Phase 7: Validation & Testing (Week 4)

#### Task 7.1: Complete Test Files
- [ ] Create all test files in samples4/
- [ ] Create expected history JSON files
- [ ] Create git repository with known history

#### Task 7.2: Run Validation Tests
- [ ] Validate multi_edit_text.txt
- [ ] Validate all samples4 files
- [ ] Test edge cases (empty files, binary files, etc.)

#### Task 7.3: Fix Issues
- [ ] Resolve validation failures
- [ ] Improve extraction accuracy
- [ ] Handle edge cases

**Validation Test**:
```bash
python tests/validate.py samples4/text_files/multi_edit_text.txt --strict
# Exit code 0 = pass, 1 = fail
```

**Estimated Time**: 2 days

---

### Phase 8: Additional File Types (Week 4)

#### Task 8.1: Spreadsheet Support
- [ ] Excel .xlsx (openpyxl)
- [ ] Excel .xls (xlrd)
- [ ] CSV files

#### Task 8.2: Presentation Support
- [ ] PowerPoint .pptx
- [ ] PowerPoint .ppt

#### Task 8.3: Archive Support
- [ ] ZIP files
- [ ] TAR files
- [ ] GZ files

#### Task 8.4: Email Support
- [ ] .eml files
- [ ] .msg files (Outlook)

**Estimated Time**: 2 days

---

### Phase 9: Polish & Optimization (Week 5)

#### Task 9.1: Performance Optimization
- [ ] Caching for repeated extractions
- [ ] Parallel extraction for large files
- [ ] Lazy loading for big files
- [ ] Memory optimization

#### Task 9.2: Error Handling
- [ ] Graceful degradation
- [ ] Clear error messages
- [ ] Logging improvements
- [ ] User-friendly warnings

#### Task 9.3: Documentation
- [ ] Code documentation (docstrings)
- [ ] Examples in README
- [ ] API documentation
- [ ] Contributing guide

#### Task 9.4: Testing Improvements
- [ ] Unit tests for all extractors
- [ ] Integration tests
- [ ] Performance tests
- [ ] Edge case tests

**Estimated Time**: 3 days

---

## 📊 Success Metrics

### Phase 2 (Core Infrastructure)
- [ ] Directory structure created
- [ ] Basic extraction working
- [ ] 1+ test file passes validation

### Phase 3 (Core Functionality)
- [ ] Embedded marker extraction working
- [ ] Knowledge graph generation working
- [ ] Flow pipeline operational
- [ ] multi_edit_text.txt passes validation

### Phase 4 (Additional Extractors)
- [ ] 5+ metadata extractors implemented
- [ ] Git history extraction working
- [ ] PDF extraction working
- [ ] 3+ test files pass validation

### Phase 5 (Evaluation Bands)
- [ ] All data has confidence scoring
- [ ] Bands correctly assigned
- [ ] Validation includes band checks

### Phase 6 (Multi-Model Extraction)
- [ ] 10+ file types supported
- [ ] 3+ extractors per file type
- [ ] All extractors produce valid output
- [ ] 5+ test files pass validation

### Phase 7 (Validation & Testing)
- [ ] All samples4 files pass validation
- [ ] Edge cases handled
- [ ] No critical errors

### Phase 8 (Additional File Types)
- [ ] 20+ file types supported
- [ ] All common formats covered
- [ ] Specific extractors for each format

### Phase 9 (Polish & Optimization)
- [ ] Performance acceptable (<10s for <10MB files)
- [ ] Code quality high (type hints, docstrings)
- [ ] Tests comprehensive (80%+ coverage)
- [ ] Documentation complete

---

## 🎯 Milestones

| Milestone | Date | Description | Status |
|-----------|------|-------------|--------|
| M0: Design | 2026-10-05 | All design documents complete | ✅ DONE |
| M1: Core Working | 2026-10-08 | Basic extraction + knowledge graph | ⏳ TODO |
| M2: Full Extraction | 2026-10-12 | All extractors implemented | ⏳ TODO |
| M3: Validated | 2026-10-15 | All test files pass | ⏳ TODO |
| M4: Production Ready | 2026-10-19 | Performance + documentation | ⏳ TODO |

---

## 📋 Next Immediate Steps

### Priority 1: Create Actual Python Files (Do This First)

```bash
# Create directory structure
mkdir -p extractor/metadata extractor/content extractor/version
mkdir -p graph pipeline evaluation tests
mkdir -p samples4/text_files samples4/documents samples4/images samples4/pdfs

# Convert templates to actual files
cp artifacts/extraction_engine.md extractor/extraction_engine.md
cp artifacts/version_history_extractor.md extractor/version/version_history_extractor.md

# Then convert .md to .py by removing markdown formatting
```

### Priority 2: Create Test Files

```bash
# Create multi_edit_text.txt
cat > samples4/text_files/multi_edit_text.txt << 'EOF'
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: user1 | TYPE: create | SECTION: document_root | DESCRIPTION: Initial file creation -->
# Project Documentation

This is the initial version.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: user2 | TYPE: add | SECTION: intro | DESCRIPTION: Added intro -->
## Introduction

Added content.
EOF

# Create history JSON
cat > samples4/text_files/multi_edit_text.history.json << 'EOF'
{
  "filename": "multi_edit_text.txt",
  "total_expected_edits": 2,
  "total_expected_edges": 1
}
EOF
```

### Priority 3: Install and Test

```bash
# Install core dependencies
pip install python-magic Pillow PyPDF2 pdfplumber python-docx openpyxl pydub networkx

# Convert one template to Python and test
python extract.py samples4/text_files/multi_edit_text.txt
```

---

## 🔧 Implementation Order Recommendation

Based on dependencies and complexity:

1. **Directory Structure** (5 min)
2. **Base Classes** (`extractor/base.py`) (1 hour)
3. **Embedded Marker Extractor** (1-2 hours)
4. **VersionAnalyzer** (1 hour)
5. **KnowledgeGraphBuilder** (1 hour)
6. **Main extract.py** (2 hours)
7. **Test with samples4** (1 hour)
8. **Filesystem Metadata Extractor** (1 hour)
9. **Git Extractor** (2 hours)
10. **PDF Extractor** (2 hours)
11. **Evaluation Bands** (1 hour)
12. **Additional Extractors** (Iterative)

---

## ⏱️ Estimated Timeline

| Phase | Duration | Start Date | End Date |
|-------|----------|------------|----------|
| Phase 0 (Design) | Done | - | 2026-10-05 |
| Phase 1 (Templates) | Done | - | 2026-10-05 |
| Phase 2 (Infrastructure) | 1 day | 2026-10-05 | 2026-10-06 |
| Phase 3 (Core Functionality) | 2 days | 2026-10-06 | 2026-10-08 |
| Phase 4 (Extractors) | 3 days | 2026-10-08 | 2026-10-11 |
| Phase 5 (Evaluation Bands) | 1 day | 2026-10-11 | 2026-10-12 |
| Phase 6 (Multi-Model) | 4 days | 2026-10-12 | 2026-10-16 |
| Phase 7 (Validation) | 2 days | 2026-10-16 | 2026-10-18 |
| Phase 8 (Additional Types) | 2 days | 2026-10-18 | 2026-10-20 |
| Phase 9 (Polish) | 3 days | 2026-10-20 | 2026-10-23 |

**Total**: ~18 days for full implementation
**MVP (Phases 0-3)**: ~3 days (core functionality with embedded markers)

---

## 🏆 MVP Definition

**Minimum Viable Product** includes:
- ✅ File ingestion
- ✅ Embedded marker extraction
- ✅ Knowledge graph generation
- ✅ Flow pipeline
- ✅ One test file passing validation
- ✅ CLI interface
- ✅ JSON output

**MVP can be achieved in 2-3 days of focused work.**

---

## 📞 Getting Help

If you get stuck during implementation:

1. **Check the design documents** in `artifacts/`
2. **Review the templates** - they contain working code
3. **Test incrementally** - validate each component individually
4. **Start simple** - implement one extractor, make it work, then add more
5. **Use samples4** - the test files have known expected outputs

---

## 📝 Tracking Progress

Use this checklist to track implementation:

```markdown
## ✅ Phase 2: Core Infrastructure
- [ ] Directory structure created
- [ ] __init__.py files created
- [ ] artifacts folder organized
- [ ] requirements.txt created
- [ ] pyproject.toml created

## ⏳ Phase 3: Core Functionality
- [ ] File ingestion working
- [ ] Embedded marker parsing working
- [ ] EditNode class implemented
- [ ] VersionAnalyzer implemented
- [ ] KnowledgeGraphBuilder implemented
- [ ] FlowPipeline implemented
- [ ] CLI working
- [ ] multi_edit_text.txt passes validation

## ⏳ Phase 4: Additional Extractors
- [ ] filesystem_metadata extractor
- [ ] git_history extractor
- [ ] pdf_metadata extractor
- [ ] word_metadata extractor
- [ ] At least 3 test files passing

## ⏳ Phase 5: Evaluation Bands
- [ ] EvaluationBandAssigner implemented
- [ ] Bands assigned to all data
- [ ] Validation includes band checks

## ⏳ Phase 6: Multi-Model Extraction
- [ ] Extractor registry
- [ ] Dynamic extraction
- [ ] 10+ file types supported
- [ ] 5+ test files passing

## ⏳ Phase 7: Validation & Testing
- [ ] All samples4 files created
- [ ] All expected history JSON created
- [ ] Validation script working
- [ ] All tests passing
- [ ] Edge cases handled

## ⏳ Phase 8: Additional File Types
- [ ] Excel support
- [ ] PowerPoint support
- [ ] Archive support
- [ ] Email support
- [ ] 20+ file types

## ⏳ Phase 9: Polish & Optimization
- [ ] Performance optimization
- [ ] Error handling improvements
- [ ] Code documentation
- [ ] Unit tests
- [ ] README updates
```

---

## 🎉 Let's Get Started!

The project is **ready for implementation**. All design and planning is complete.

**To begin**:
1. Create the directory structure
2. Convert the .md templates to .py files
3. Create the test files in samples4/
4. Install dependencies
5. Start with the embedded marker extractor and flow pipeline
6. Test with samples4/text_files/multi_edit_text.txt

**Expected outcome**: You should be able to run `python extract.py samples4/text_files/multi_edit_text.txt` and get a knowledge graph with 2-6 nodes showing the edits extracted from the embedded markers.

Once that works, add more extractors one by one and expand the test coverage.

---

**Good luck!** The design is solid and the templates contain most of the code you need. Just need to bring it to life as actual Python files.
