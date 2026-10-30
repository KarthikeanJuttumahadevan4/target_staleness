# 02_Intake_Extraction — Document Intake & Multi-Path Extraction

## Problem Statement (from Proposal)

The system must ingest `samples5/` incrementally, accepting "any new or
modified files" regardless of format, and extract structured facts via
**multiple extraction paths** (text, tables, OCR, VLM).

---

## Document Type Coverage

| Category | Formats | Primary Engine | Fallback |
|----------|---------|----------------|----------|
| **Text docs** | PDF, DOCX, TXT, MD, RTF | Docling / Docs2KG | Semantica |
| **Structured** | XLSX, CSV, TSV, JSON, XML | AI-KE tabular bypass / Docs2KG | Pandas |
| **Scanned PDFs** | PDF (image-based) | Docs2KG (OCR via Tesseract) | MinerU |
| **Adobe-compressed PDF** | PDF (compressed streams) | Docling / PDFMiner | PyMuPDF |
| **Spreadsheets** | XLSX (multi-sheet), CSV | AI-KE (3 LLM calls/sheet) | Docs2KG |
| **Presentations** | PPTX | Docling | Semantica |
| **Images** | PNG, JPG, JPEG, TIFF, BMP | Multi-VIE / Qwen2.5-VL | Docling-Graph |
| **Audio** | MP3, WAV, M4A | AI-KE (FFmpeg + Whisper) | AssemblyAI |
| **Video** | MP4, MOV, AVI, WebM | AI-KE (frame extraction) | KIE |
| **Archives** | ZIP, TAR.GZ, 7Z | Python zipfile + recursive intake | Apache commons |
| **Web** | HTML, URL content | WebIngestor (Semantica) | BeautifulSoup |
| **Emails** | EML, MBOX, MSG | Docs2KG | Email parsing libs |

---

## Intake Strategy

### Step 1 — File Watcher
- **Library:** `watchdog` (Python, cross-platform)
- **Behavior:** watches `samples5/` recursively
- **Trigger:** on `created` or `modified` event → enqueue intake job

### Step 2 — Pre-Processing
| Input Type | Pre-Processing |
|-----------|----------------|
| ZIP/TAR | Extract → recurse into files |
| Audio | FFmpeg → Whisper → text + timestamps |
| Video | Frame extraction @ 1fps + metadata; OCR on key frames |
| Scanned PDF | OCR via Tesseract (bundled) |
| Adobe PDF | Decompress via PDFMiner/PyMuPDF (auto) |

### Step 3 — Format Detection
- **Library:** `python-magic` (MIME detection)
- **Output:** `(PipelineKind, format, encoding)` — routes to correct extractor

### Step 4 — Extraction
- **Primary:** Docs2KG (dual-path: programmatic parser + Doc Layout Analysis)
- **Secondary:** Docling (layout-preserving, complex tables)
- **Tertiary:** Semantica (broad format support)
- **Quaternary:** AI-KE (audio/video/multimedia)

---

## Multi-Path Extraction Methods

### Path A — Text Extraction (Fast, deterministic)
- **Method:** Library-based parsers (PDFMiner, python-docx, openpyxl)
- **Libraries:** PyMuPDF, pdfplumber, python-docx, openpyxl
- **Output:** Raw text with position metadata (page, bbox)
- **Performance:** ~100 pages/sec

### Path B — OCR Extraction (slow, visual)
- **Method:** Tesseract 5.x / Tesseract LSTM / EasyOCR / PaddleOCR
- **Use Case:** Scanned documents, image-based PDFs
- **Output:** Text with confidence scores + bounding boxes
- **Performance:** ~10 pages/sec

### Path C — Layout Analysis (medium)
- **Method:** CV-based layout detection (DocLayout, CNN-based)
- **Use Case:** Multi-column, complex layouts
- **Output:** Structured regions (title, paragraph, table, figure)
- **Performance:** ~20 pages/sec

### Path D — VLM Extraction (slowest, most accurate)
- **Method:** Qwen2.5-VL-7B / GPT-4o Vision / Docling-Graph
- **Use Case:** Diagrams, complex tables, charts
- **Output:** Structured data + KG triples
- **Performance:** ~2-5 pages/sec (model-bound)

### Path E — Tabular Bypass (instant, structured)
- **Method:** Direct XLSX/CSV → Neo4j Table nodes (AI-KE)
- **Use Case:** Spreadsheets, database exports
- **Output:** `Table` + `Row` nodes with properties
- **Performance:** ~1000 rows/sec

---

## Extraction Output Schema

Every extraction produces a normalized artifact:

```json
{
  "doc_id": "uuid",
  "source_path": "samples5/report.pdf",
  "timestamp": "2024-01-15T10:30:00Z",
  "as_of": "2024-01-15T10:30:00Z",
  "extraction_path": "text|ocr|layout|vlm|tabular",
  "model_used": "pymupdf|tesseract|qwen2.5-vl-7b",
  "chunks": [
    {
      "chunk_id": "uuid",
      "text": "CEO is Satya Nadella",
      "bbox": [x, y, w, h],
      "page": 1,
      "confidence": 0.98
    }
  ],
  "entities": [...],
  "relations": [...]
}
```

This feeds directly into **Graphiti** for reconstruction.

---

## Gap Analysis: What Could Go Wrong?

| Risk | Mitigation |
|------|-----------|
| OCR quality on scanned docs | Use best OCR (Tesseract 5 LSTM) + confidence threshold (0.8) |
| Table cell recognition errors | Use Docling's table structure model (92% accuracy) |
| Audio transcription noise | Whisper `large-v3` + NLP post-processing |
| Video key-frame selection | Compute scene-change detection (SSIM threshold) |
| ZIP bomb / malicious archives | AI-KE's archive-bomb limits (max size, ratio) |
| PDF stream decompression failures | Fallback from Docling → PyMuPDF → pdfminer |
<|end|> Format mis-detection | Magic library + extension fallback |

---

## Decisions Needed (Human Validation)

1. Should audio/video transcription happen **offline** (batch) or **on-demand**?
2. Max file size limit for intake (currently proposed: 500MB)?
3. Should ZIP extraction be **automatic** or **manual approval**?
4. Which OCR engine priority (Tesseract vs EasyOCR vs PaddleOCR)?
5. Should video frame extraction be at fixed intervals or scene-change?
