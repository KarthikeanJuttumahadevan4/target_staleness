# OLD PROJECT: Invoice Extractor

**Status**: ✅ COMPLETED (Original Project)  
**Purpose**: Extract invoice data from PDFs, Excel, text, audio, and video files  
**Do Not Use**: These are for reference only. The NEW project is in `/samples4/` and updated files in `artifacts/`

---

## 📂 Files in This Old Project

These files are part of the **original Invoice Extractor** project and are kept for reference:

### Core Documentation
- **`prototype_plan.md`** - Original Tonight Plan (12 DNS)
- **`proposal.md`** - **NOTE: This has been OVERRIDDEN by new project**
- **`specs.md`** - **NOTE: This has been OVERRIDDEN by new project**
- **`requirements_prototype.md`** - Original requirements
- **`library_research.md`** - Original library research

### Code Templates (Original)
- **`batch_extract.md`** - Batch extraction documentation
- **`batch_extract.py.md`** - Batch extraction code template
- **`build_graph.py.md`** - Graph building code template
- **`run_pipeline.md`** - Pipeline run documentation

### Results & Reports
- **`graph/summary.md`** - Graph summary
- **`tests/TEST_REPORT.md`** - Test report

---

## ⚠️ IMPORTANT NOTES

### Overridden Files
Two files have been **updated** for the NEW Universal File Extractor project:
- `proposal.md` → Now describes Universal File Extractor
- `specs.md` → Now describes Universal File Extractor

**These are NOT part of the old project anymore.**

### Preserved Files
All other files in `artifacts/` are **unchanged** from the original Invoice Extractor project.

---

## 🎯 How This Differs from NEW Project

| Aspect | Invoice Extractor (OLD) | Universal Extractor (NEW) |
|--------|------------------------|---------------------------|
| **Goal** | Extract invoice fields | Extract ALL metadata + version history |
| **Input** | Invoice files | ANY file |
| **Output** | Vendor, date, total | Knowledge graph of changes |
| **Version Tracking** | ❌ No | ✅ Yes (complete history) |
| **Graph Nodes** | Invoices, Vendors | Edits, Changes, Versions |
| **Confidence** | ❌ No | ✅ Yes (Evaluation Bands) |

---

## 📋 Original Project Summary

The Invoice Extractor was designed to:
1. Ingest PDF, XLSX, TXT, audio, video files
2. Extract raw text/transcript
3. Structure into `vendor`, `invoice_date`, `total`, `notes` using LLM
4. Output JSON with ingestion metadata

### Key Features
- Used docling for document extraction
- Used dspy for LLM inference
- Used uv for package management
- Supported OpenAI-compatible endpoints

### Dependencies
- docling
- dspy
- python-dotenv
- uv

---

## 🔄 Migration Notes

If you need to reference the **old** Invoice Extractor design:
- All files are preserved here
- Two files (`proposal.md`, `specs.md`) have been updated for the new project
- The new project files are in `samples4/` directory

---

## 📁 Where to Find NEW Project

The **NEW Universal File Extractor** is in:
- `/samples4/` - All execution files and guides
- `/artifacts/PROJECT_SUMMARY.md` - Complete new project summary
- `/artifacts/IMPLEMENTATION_ROADMAP.md` - Implementation plan
- `/artifacts/proposal.md` - **UPDATED** for new project
- `/artifacts/specs.md` - **UPDATED** for new project

---

## 🎯 Recommendation

**Do NOT use these old files** for new development. Use the NEW project files in `/samples4/` instead.

These old files are kept **only for reference** and historical purposes.
