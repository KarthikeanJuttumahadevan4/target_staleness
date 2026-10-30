---
format: html
---

# Invoice Extractor - Specification

## Problem Statement
Users need a local CLI tool to extract structured invoice fields (vendor, invoice_date, total, notes) from heterogeneous files: PDFs, Excel spreadsheets, text, audio, and video. Existing tools are fragmented and require separate pipelines for each format. The tool must integrate with OpenAI-compatible LLM APIs, with clear provenance and error handling for scanned documents and missing dependencies.

## Scope
### In-scope
- CLI `python3 extract.py <file>` supporting .pdf, .xlsx, .txt, audio (.wav/.mp3/.m4a/.ogg), video (.mp4/.mov/.mkv/.webm)
- **Document extraction via docling** for unified handling of all file types
- **LLM structuring via dspy** for reliable JSON extraction
- Output JSON to stdout, INGEST/CHARS metrics to stderr
- .env configuration for OPENAI_API_KEY, OPENAI_BASE_URL, MODEL
- Package management via `uv`

### Out-of-scope
- Custom OCR/VLM pipelines (docling handles this internally)
- Multi-sheet Excel beyond what docling returns
- Streaming or batch processing
- Direct OpenAI client usage (dspy abstracts this)
- Ollama-specific integration

## User Intent
Run a single command on a file and receive structured invoice data as JSON, with ingestion method transparency and graceful degradation when dependencies are missing. The tool uses docling for document extraction and dspy with OpenAI-compatible APIs for structuring into invoice fields.

## Research Findings Summary

| Library | Purpose | Decision | Key Finding |
|---|---|---|---|
| **docling** | Document extraction | Use | Supports all required formats (PDF, XLSX, TXT, audio, video) with unified API. Uses Whisper for ASR, Tesseract for OCR. |
| **dspy** | Structured LLM inference | Use | Configure with `dspy.LM('openai/model-name', api_key='...', api_base='...')`. Structured signatures, built-in error handling. |
| **uv** | Package management | Use | `uv init`, `uv add`, `uv run` workflow. Auto-manages .venv, faster than pip. |

See `artifacts/library_research.md` for detailed Context7 findings.

## Functional Requirements

### FR1: CLI Entry Point
- The CLI accepts exactly one positional argument: filepath.
- If no argument provided, prints usage to stderr and exits with code 1.

### FR2: File Type Detection
- Detect extension case-insensitively for informational logging only.
- All file type detection is delegated to docling's `DocumentConverter.convert()`.
- docling natively supports all required formats via its `InputFormat` enum.
- If docling raises an exception for unsupported format: prints "unsupported" to stderr, prints `INGEST=unknown CHARS=0`, exits with code 2.

### FR3: Document Extraction (docling)
- Use `docling.DocumentConverter().convert(source=filepath)` for all formats.
- Extract text via `result.document.export_to_text()` or `export_to_markdown()`.
- ingest_path = standardized naming based on file extension or docling pipeline.
- For all formats, emit `INGEST=<method> CHARS=<n>` to stderr.
- Character count is based on the exported text length.

#### PDF Specifics
- docling handles both text-based and scanned PDFs via OCR.
- After extraction, if text length < 80 characters:
  - Print warning "This PDF looks scanned. OCR may not have extracted sufficient text." to stderr
  - Exit with code 2
- This preserves the v1 behavior of rejecting likely scanned documents.

#### Excel Specifics
- docling's MsExcelDocumentBackend extracts first sheet by default.
- Convert to text/markdown for LLM input.

#### Audio Specifics
- docling's AsrPipeline uses Whisper models by default.
- Supports: .wav, .mp3, .m4a, .aac, .ogg, .flac
- ingest_path includes "asr" or specific whisper model used.

#### Video Specifics
- docling's VideoPipeline extracts audio, then uses AsrPipeline.
- Supports: .mp4, .avi, .mov, .mkv, .webm
- ingest_path includes "video_asr" or similar.

### FR4: Environment Loading
- Load .env from script directory via python-dotenv.
- Required variables:
  - `OPENAI_API_KEY`: API key for OpenAI-compatible endpoint
  - `OPENAI_BASE_URL`: URL of the OpenAI-compatible API endpoint (e.g., `http://localhost:11434/v1` or `https://api.openai.com/v1`)
  - `MODEL`: Model identifier to use (e.g., `gpt-3.5-turbo`, `llama3.2:latest`)
- has_key true if OPENAI_API_KEY is not None and not empty.

### FR5: LLM Structuring (dspy)
- If no API key: output null fields with notes = "no LLM API key configured", exit normally.
- Configure dspy LM:
  ```python
  import dspy
  lm = dspy.LM(
      f'openai/{model}',
      api_key=OPENAI_API_KEY,
      api_base=OPENAI_BASE_URL
  )
  dspy.configure(lm=lm)
  ```
- Define extraction signature:
  ```python
  from typing import Optional
  
  class ExtractInvoice(dspy.Signature):
      """Extract invoice fields from document text."""
      document_text: str = dspy.InputField(desc="Full text of the document")
      source: str = dspy.InputField(desc="Original filename")
      ingest_method: str = dspy.InputField(desc="Extraction method used")
      
      vendor: Optional[str] = dspy.OutputField(desc="Name of the vendor")
      invoice_date: Optional[str] = dspy.OutputField(desc="Invoice date in YYYY-MM-DD format")
      total: Optional[float] = dspy.OutputField(desc="Total amount")
      notes: Optional[str] = dspy.OutputField(desc="Additional notes or extraction warnings")
  ```
- Use `dspy.Predict(ExtractInvoice)` for extraction.

#### Error Handling
- Wrap dspy call in try/except:
  ```python
  try:
      prediction = extractor(
          document_text=doc_text,
          source=path.name,
          ingest_method=ingest_path
      )
      result = {
          "vendor": prediction.vendor,
          "invoice_date": prediction.invoice_date,
          "total": prediction.total,
          "notes": prediction.notes,
      }
  except dspy.ContextWindowExceededError:
      notes = "Document too large for model context window"
      result = {"vendor": None, "invoice_date": None, "total": None, "notes": notes}
  except dspy.LMRateLimitError as e:
      notes = f"Rate limited by {e.provider}; retry after {e.retry_after} seconds"
      result = {"vendor": None, "invoice_date": None, "total": None, "notes": notes}
  except dspy.LMError as e:
      notes = f"LM failed: code={e.code}, model={e.model}"
      result = {"vendor": None, "invoice_date": None, "total": None, "notes": notes}
  ```

### FR6: Should Call Decision
- If docling extraction fails or returns empty content: do not call LLM, output nulls with extraction error in notes
- For all successful extractions: call dspy
- Special case: PDF with <80 chars exits before LLM call (see FR3)

### FR7: Output Format
**stdout**: JSON with fields:
- vendor: string | null
- invoice_date: string | null (YYYY-MM-DD if possible)
- total: number | null
- notes: string | null (contains extraction method warnings and any dspy/LLM errors)
- extracted_at: UTC ISO timestamp
- ingest_path: string (standardized method identifier)
- source: filename

**stderr**: `INGEST=<method> CHARS=<n>` line

### FR8: Exit Codes
- 1: missing argument
- 2: scanned PDF (insufficient text), unsupported file, or docling extraction failure

## Non-Functional Requirements

### NFR1: Performance
- docling extraction time depends on document size, type, and OCR requirements
- dspy call latency depends on LLM endpoint performance
- docling caches pipelines for repeated calls

### NFR2: Reliability
- Graceful degradation when docling cannot extract text
- Structured error handling from dspy
- No crash on malformed files

### NFR3: Security
- API keys loaded from .env, not logged or exposed in output
- No temp files written by our code (docling may use its own caching)

### NFR4: Observability
- INGEST and CHARS on stderr for each run
- Extraction errors and LLM errors captured in notes field

## Constraints
- Python 3.10+
- Dependencies: docling, dspy, python-dotenv
- Optional system dependencies: libgl1, tesseract-ocr (for OCR), ffmpeg (for audio/video if docling requires it)
- Package management: uv (for venv creation, dependency installation, execution)
- OpenAI-compatible endpoint required for dspy

## Dependencies (uv-managed)

### Core
```toml
[project]
dependencies = [
  "docling[asr,tesserocr]",
  "dspy",
  "python-dotenv",
]
```

### Dev
```toml
[dependency-groups]
dev = ["pytest", "ruff"]
```

### System (Optional)
- `libgl1` - For OpenCV compatibility
- `tesseract-ocr` - For OCR with Tesseract backend
- `tesseract-ocr-eng` - English language data for Tesseract

## Open Questions

### Resolved by Research
1. **docling file type support**: Confirmed - supports all required formats (PDF, XLSX, TXT, WAV, MP3, M4A, OGG, MP4, MOV, MKV, WEBM) via InputFormat enum.
2. **docling OCR/ASR**: Confirmed - uses Tesseract for OCR (with extras) and Whisper for ASR.
3. **dspy OpenAI compatibility**: Confirmed - use `dspy.LM('openai/model-name', api_key='...', api_base='...')`
4. **dspy signature usage**: Confirmed - use `dspy.Signature` with `dspy.InputField`/`dspy.OutputField`
5. **dspy error handling**: Confirmed - structured exceptions (`LMError`, `LMRateLimitError`, `ContextWindowExceededError`)
6. **uv workflow**: Confirmed - `uv venv`, `uv pip install`, `uv run`, `uv init`, `uv add`, `uv sync`, `uv lock`

### Remaining Questions
1. **ingest_path identification**: Should we use docling's pipeline name or map from file extension? Recommendation: Use file extension for simplicity.
2. **PDF threshold**: Keep 80 characters or adjust for docling's OCR quality? Recommendation: Keep 80.
3. **Model default**: What fallback MODEL if not set in .env? Recommendation: `gpt-3.5-turbo`.
4. **Error note precedence**: How to combine docling warnings with dspy errors? Recommendation: concatenate with semicolon separator.
5. **Export format**: `export_to_text()` or `export_to_markdown()`? Recommendation: `export_to_text()` for simplicity.

## Risks
- **docling OCR quality**: Tesseract OCR on scanned PDFs may still have issues; the <80 char threshold catches obvious failures but may miss partial extractions
- **docling dependencies**: System packages (tesseract, libgl1) may be missing on some systems
- **dspy compatibility**: Non-OpenAI-compatible endpoints may have subtle differences that cause errors
- **context window**: Large invoices or spreadsheets may exceed LLM context window; dspy's truncation helps but may lose data
- **Cost**: Using cloud LLM endpoints may incur costs; user must be aware
- **Rate limits**: OpenAI-compatible endpoints may impose rate limits; dspy provides retry info in exceptions
- **docling pipeline load time**: First call for ASR/OCR may be slow due to model loading

## Implementation Notes

### Recommended Project Structure
```
mini-extract/
├── .venv/                   # uv-managed virtual environment
├── pyproject.toml          # Dependencies and project config
├── uv.lock                 # Lockfile
├── extract.py              # Main CLI script
├── .env.example            # Example environment configuration
├── README.md               # Documentation
└── artifacts/              # Specs, proposals, research
    ├── specs.md
    ├── proposal.md
    └── library_research.md
```

### Recommended pyproject.toml
```toml
[project]
name = "mini-extract"
version = "0.1.0"
description = "CLI tool to extract invoice data from files"
requires-python = ">=3.10"
dependencies = [
    "docling[asr,tesserocr]",
    "dspy",
    "python-dotenv",
]

[dependency-groups]
dev = ["pytest", "ruff"]
```

### Recommended .env.example
```bash
# OpenAI-compatible API configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=http://localhost:11434/v1
MODEL=llama3.2:latest
```

### Recommended uv Commands
```bash
# Initialize and setup
uv init
uv add docling dspy python-dotenv
uv add -D pytest ruff
uv sync

# Run
uv run python extract.py samples/invoice_1.pdf

# For development
uv run pytest
uv run ruff check .
```
