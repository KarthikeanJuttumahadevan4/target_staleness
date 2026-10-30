# Library Research - Context7 Findings

This document contains research findings from Context7 for docling, dspy, and uv libraries.

---

## 1. Docling (Document Extraction)

### Library Identification
- **ID**: `/docling-project/docling`
- **Description**: Simplifies document processing by parsing diverse formats, including advanced PDF understanding, with seamless integration with generative AI.
- **Source Reputation**: High | **Benchmark Score**: 77.12 | **Code Snippets**: 2093

### Supported File Formats

Docling supports all required file types through its `InputFormat` enum and `FormatToExtensions` mapping:

#### Document Formats
| Format | Extensions | Backend |
|---|---|---|
| PDF | `.pdf` | PDF backend with OCR support |
| DOCX | `.docx`, `.dotx`, `.docm`, `.dotm` | MsWord backend |
| DOC | `.doc`, `.dot` | MsWord backend |
| XLSX | `.xlsx`, `.xlsm`, `.xltx`, `.xltm` | MsExcel backend |
| XLS | `.xls`, `.xlt` | MsExcel backend |
| ODS | `.ods`, `.ots` | OpenDocument backend |
| TXT | `.txt`, `.text` (via MD) | Text backend |
| MD | `.md`, `.txt`, `.text`, `.qmd`, `.rmd`, `.Rmd` | Markdown backend |
| CSV | `.csv` | CSV backend |

#### Media Formats
| Format | Extensions | Pipeline |
|---|---|---|
| AUDIO | `.wav`, `.mp3`, `.m4a`, `.aac`, `.ogg`, `.flac` | AsrPipeline (Whisper-based) |
| VIDEO | `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm` | VideoPipeline (extracts audio, then ASR) |

#### Additional Supported Formats
- PPTX, PPT, HTML, MHTML, RTF, ASCIIDOC, EPUB, EMAIL, LATEX, XML variants, and more.

### Installation

```bash
# Basic installation
pip install -qU docling

# With extras for specific functionality
pip install "docling[asr]"          # Audio transcription dependencies
pip install "docling[tesserocr]"    # Tesseract OCR engine
pip install "docling[easyocr]"      # EasyOCR engine
pip install "docling[rapidocr]"     # RapidOCR engine
pip install "docling[htmlrender]"   # HTML rendering dependencies
```

### System Dependencies

#### Required for OCR (Tesseract)
```bash
# Debian/Ubuntu
apt-get install libgl1 tesseract-ocr

# Fedora/RHEL
dnf install libgl1 tesseract-ocr

# macOS (Homebrew)
brew install tesseract
```

#### OpenCV Compatibility
If encountering `libGL.so.1` errors:
```bash
pip uninstall -y opencv-python opencv-python-headless
pip install --no-cache-dir opencv-python-headless
```

### API Usage

#### Basic Document Conversion
```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert(source="path/to/file.pdf")
doc = result.document

# Export options
markdown = doc.export_to_markdown()
text = doc.export_to_text()
json = doc.export_to_json()
```

#### CSV Conversion
```python
from pathlib import Path
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert(Path("data.csv"))
markdown = result.document.export_to_markdown()
```

#### String Conversion
```python
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat

converter = DocumentConverter()
result = converter.convert_string(html_content, InputFormat.HTML)
md = result.document.export_to_markdown()
```

### Pipeline Architecture
- Each format maps to a `FormatOption` with `pipeline_cls` and `backend`
- Audio: `AsrPipeline` with `NoOpBackend`
- Video: `VideoPipeline` with `NoOpBackend`
- PDF: PDF backend with OCR support
- Excel: `MsExcelDocumentBackend` with `SimplePipeline`
- Pipelines are **cached** and reused for performance

### OCR Configuration
Docling supports multiple OCR engines via extras:
- `tesserocr`: Tesseract bindings
- `easyocr`: EasyOCR engine
- `rapidocr`: RapidOCR with ONNX runtime
- Default ASR uses Whisper models

### Output Formats
- MARKDOWN
- TEXT
- JSON
- HTML
- HTML_SPLIT_PAGE
- DOCTAGS
- VTT (subtitles)
- DOCLANG
- DCLX
- CHUNKS
- LATEX

### Key Implications for Invoice Extractor
1. ✅ **Covers all required formats**: PDF, XLSX, TXT, WAV, MP3, M4A, OGG, MP4, MOV, MKV, WEBM
2. ✅ **Unified API**: Single `DocumentConverter().convert()` call for all formats
3. ✅ **Audio/Video built-in**: ASR pipeline handles audio; Video pipeline extracts audio then uses ASR
4. ⚠️ **OCR dependencies**: System packages (tesseract, poppler) may be needed for scanned PDFs
5. ⚠️ **Large dependencies**: docling may pull in heavy ML models for OCR/ASR
6. ❓ **Ingestion method tracking**: Need to check if we can identify which pipeline/backend was used

---

## 2. DSPy (Structured LLM Inference)

### Library Identification
- **ID**: `/stanfordnlp/dspy`
- **Description**: Framework for programming language models, enabling modular AI systems and optimizing prompts and weights.
- **Source Reputation**: Low | **Benchmark Score**: 80.38 | **Code Snippets**: 1397
- **Latest Version**: 3.1.3

### OpenAI-Compatible Endpoint Configuration

#### Method 1: Environment Variables
```bash
export OPENAI_API_KEY="your-api-key"
```

#### Method 2: Direct Configuration
```python
import dspy

lm = dspy.LM(
    'openai/your-model-name',  # Prefix with openai/
    api_key='YOUR_API_KEY',
    api_base='http://127.0.0.1:11434/v1'  # Custom endpoint
)
dspy.configure(lm=lm)
```

#### Method 3: Provider-specific
For non-OpenAI endpoints that are OpenAI-compatible:
```python
lm = dspy.LM('openai/model-name', api_key='...', api_base='YOUR_PROVIDER_URL')
```

### Signature Definition

#### Inline Signature
```python
toxicity = dspy.Predict(
    dspy.Signature(
        "comment -> toxic: bool",
        instructions="Mark as 'toxic' if the comment includes insults, harassment, or sarcastic derogatory remarks.",
    )
)
result = toxicity(comment="you are beautiful.")
print(result.toxic)  # False
```

#### Class-based Signature
```python
from typing import Optional, Literal

class ExtractContact(dspy.Signature):
    """Extract contact info."""
    message: str = dspy.InputField()
    name: str = dspy.OutputField()
    email: Optional[str] = dspy.OutputField()
    intent: Literal["meeting", "intro", "follow-up"] = dspy.OutputField()

extract = dspy.Predict(ExtractContact)
result = extract(message="I'm Sarah (sarah@acme.co). Meet Thursday?")
# Prediction(name="Sarah", email="sarah@acme.co", intent="meeting")
```

### For Invoice Extraction
```python
from typing import Optional

class ExtractInvoice(dspy.Signature):
    """Extract invoice fields from document text."""
    document_text: str = dspy.InputField(desc="Full text of the invoice document")
    source: str = dspy.InputField(desc="Original filename")
    ingest_method: str = dspy.InputField(desc="How the document was ingested")
    
    vendor: Optional[str] = dspy.OutputField(desc="Name of the vendor")
    invoice_date: Optional[str] = dspy.OutputField(desc="Invoice date in YYYY-MM-DD format")
    total: Optional[float] = dspy.OutputField(desc="Total amount")
    notes: Optional[str] = dspy.OutputField(desc="Additional notes or warnings")

invoice_extractor = dspy.Predict(ExtractInvoice)
```

### Error Handling
DSPy provides structured exceptions:

```python
try:
    result = qa(question="...")
except dspy.ContextWindowExceededError:
    # Reduce prompt size, retrieved passages, or demos
    raise
except dspy.LMRateLimitError as e:
    print(f"Rate limited by {e.provider}; retry after {e.retry_after} seconds")
except dspy.LMError as e:
    print(f"LM failed: code={e.code}, model={e.model}, request_id={e.request_id}")
```

All DSPy LM errors expose:
- `code`: Error code
- `model`: Model identifier
- `provider`: Provider name
- `status`: HTTP status (if applicable)
- `request_id`: Request identifier
- `retry_after`: Rate limit retry time

### Retry Logic
Built-in retry for context window issues:
- Up to 3 attempts automatically
- Truncates trajectory (oldest tool calls) on `ContextWindowExceededError`
- Raises after all retries exhausted

### Modules
- **`dspy.Predict`**: Basic prediction module
- **`dspy.ChainOfThought`**: Adds reasoning before output
- **`dspy.BestOfN`**: Runs module N times, selects best result

### Key Implications for Invoice Extractor
1. ✅ **OpenAI-compatible**: Use `openai/` prefix for any OpenAI-compatible endpoint
2. ✅ **Structured output**: Clean signature-based approach for JSON extraction
3. ✅ **Error handling**: Structured exceptions with retry logic
4. ✅ **Environment variables**: Supports `OPENAI_API_KEY` env var
5. ⚠️ **Model naming**: Need to use `openai/model-name` format for non-OpenAI endpoints
6. ❓ **Base URL**: Need to verify `api_base` parameter works for localhost/Ollama

---

## 3. uv (Package Management)

### Library Identification
- **ID**: `/astral-sh/uv`
- **Description**: Extremely fast Python package and project manager written in Rust, designed to replace pip, poetry, pipx, etc.
- **Source Reputation**: High | **Benchmark Score**: 79.28 | **Code Snippets**: 1379

### Core Commands

#### Virtual Environment Management
```bash
# Create virtual environment in .venv
uv venv

# Or in a specific directory
uv venv /path/to/venv

# Activate (traditional)
source .venv/bin/activate
```

#### Package Management
```bash
# Install packages
uv pip install flask
uv pip install -r requirements.txt

# Install with extras
uv pip install "docling[asr,tesserocr]"

# List installed packages
uv pip list

# Show package details
uv pip show flask

# Uninstall
uv pip uninstall flask

# Freeze to requirements.txt
uv pip freeze > requirements.txt
```

#### Project Management
```bash
# Initialize a new project
uv init my-project

# Add dependency to project
uv add flask

# Runs: creates .venv if needed, adds flask to pyproject.toml, installs

# Lock dependencies
uv lock

# Sync environment with lockfile
uv sync

# Export lockfile to requirements.txt
uv export --format requirements.txt

# Export to PEP 751 pylock.toml format
uv export --format pylock.toml
```

### Project Structure

#### pyproject.toml
```toml
[project]
name = "invoice-extractor"
version = "0.1.0"
dependencies = [
  "docling[asr,tesserocr]",
  "dspy",
  "python-dotenv",
]

[dependency-groups]
dev = ["pytest", "ruff"]
```

#### Environment Discovery
uv searches for environments in this order:
1. Activated virtual environment (`VIRTUAL_ENV` env var)
2. Activated Conda environment (`CONDA_PREFIX` env var)
3. `.venv` in current directory or nearest parent
4. Prompts to create `.venv` if none found

#### Running Scripts
```bash
# Run with auto environment
uv run python extract.py invoice.pdf

# uv will: find/create .venv, install deps from pyproject.toml, run script
```

### Key Implications for Invoice Extractor
1. ✅ **Fast**: 10-100x faster than pip
2. ✅ **Single tool**: Replaces pip, virtualenv, poetry, pipx
3. ✅ **Project integration**: `uv init`, `uv add`, `uv run` for full workflow
4. ✅ **Lockfile support**: `uv lock`, `uv sync`, `uv export`
5. ✅ **Auto environment**: Finds or creates `.venv` automatically
6. ⚠️ **Python discovery**: Uses system Python by default; needs Python installed
7. ❓ **Cross-platform**: Rust-based, should work on Linux, macOS, Windows

---

## Summary of Technical Decisions

### Document Extraction: docling ✅
- **Pros**: Unified API, supports all formats, built-in OCR/ASR, cached pipelines
- **Cons**: Large dependencies, system packages required for OCR
- **Action**: Use `DocumentConverter().convert(source).document.export_to_text()` or `.export_to_markdown()`

### LLM Inference: dspy ✅
- **Pros**: Clean signatures, structured output, error handling, OpenAI-compatible
- **Cons**: Additional dependency, learning curve
- **Action**: Configure with `dspy.LM('openai/model', api_key='...', api_base='...')`

### Package Management: uv ✅
- **Pros**: Fast, modern, single tool, good integration
- **Cons**: Newer tool, less widespread
- **Action**: Use `uv init`, `uv add`, `uv run` workflow

---

## Recommended pyproject.toml

```toml
[project]
name = "mini-extract"
version = "0.1.0"
description = "Invoice data extractor from PDFs, Excel, text, audio, and video files"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "docling[asr,tesserocr]",
    "dspy",
    "python-dotenv",
]

[dependency-groups]
dev = [
    "pytest>=7.0",
    "ruff",
]

[tool.uv]
extras = ["asr", "tesserocr"]
```

## Recommended uv Commands

```bash
# Initialize project
uv init mini-extract

# Add core dependencies
uv add docling
yv add dspy python-dotenv

# Add dev dependencies
uv add -D pytest ruff

# Create lockfile
uv lock

# Sync environment
uv sync

# Run the tool
uv run python extract.py samples/invoice_1.pdf

# Export requirements.txt if needed
uv export --format requirements.txt > requirements.txt
```

## Installation Script

```bash
#!/bin/bash
# Install system dependencies for docling OCR
if command -v apt-get &> /dev/null; then
    sudo apt-get install -y libgl1 tesseract-ocr
elif command -v dnf &> /dev/null; then
    sudo dnf install -y libgl1 tesseract-ocr
elif command -v brew &> /dev/null; then
    brew install tesseract
fi

# Install uv if not present
curl -LsSf https://astral-sh.github.io/uv/install.sh | sh

# Initialize project
uv init

# Add dependencies
uv add docling dspy python-dotenv
uv add -D pytest ruff

# Sync
uv sync
```
