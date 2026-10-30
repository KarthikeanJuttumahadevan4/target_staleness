"""
Routing module for determining extraction path based on file type.

This module analyzes files and routes them to the appropriate
extraction handler based on file extension and MIME type.

Usage:
    from src.intake.router import route

    handler = route("/path/to/document.pdf")
    # handler is one of: "text", "ocr", "tables", "audio", "video", "vlm", "archive", "unsupported"
"""

import mimetypes
from pathlib import Path
from typing import Literal

# File type categories
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".7z", ".tar.gz", ".tgz"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".wmv"}
PDF_EXTENSIONS = {".pdf"}
OFFICE_EXTENSIONS = {".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt"}
TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".xml", ".html", ".rtf"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"}

# Type alias for handler names
HandlerType = Literal[
    "text", "ocr", "tables", "audio", "video", "vlm", "archive", "unsupported"
]


def route(file_path: str) -> HandlerType:
    """
    Determine the extraction handler for a file.

    This function examines the file extension and MIME type to
    determine the most appropriate extraction path.

    Priority order:
    1. Archives (extract and recurse)
    2. Audio/Video (ASR path)
    3. Images (VLM path)
    4. PDFs (OCR/text)
    5. Office docs (text)
    6. Text formats (text)

    Args:
        file_path: Path to the file to route

    Returns:
        Handler type string indicating which extraction path to use

    Example:
        >>> route("invoice.pdf")
        'text'
        >>> route("recording.mp3")
        'audio'
        >>> route("chart.png")
        'vlm'
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    # Check for compound extensions like .tar.gz
    name_lower = path.name.lower()
    if name_lower.endswith(".tar.gz"):
        return "archive"

    # Priority 1: Archives
    if suffix in ARCHIVE_EXTENSIONS:
        return "archive"

    # Priority 2: Audio
    if suffix in AUDIO_EXTENSIONS:
        return "audio"

    # Priority 3: Video
    if suffix in VIDEO_EXTENSIONS:
        return "video"

    # Priority 4: Images -> VLM
    if suffix in IMAGE_EXTENSIONS:
        return "vlm"

    # Priority 5: PDF (check if scanned via MIME)
    if suffix in PDF_EXTENSIONS:
        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type and "pdf" in mime_type:
                # PDF could be text-based or scanned
                # For now, default to text; OCR fallback handled by extraction
                return "text"
        except Exception:
            pass
        return "text"

    # Priority 6: Office documents
    if suffix in OFFICE_EXTENSIONS:
        return "text"

    # Priority 7: Text formats
    if suffix in TEXT_EXTENSIONS:
        return "text"

    # Default: unsupported
    return "unsupported"


def get_ingest_method(file_path: str) -> str:
    """
    Get a standardized ingest method name for logging/metrics.

    Args:
        file_path: Path to the file

    Returns:
        Standardized method name (e.g., "pdf_text", "audio_asr", "vlm")
    """
    handler = route(file_path)
    suffix = Path(file_path).suffix.lower()
    # Remove leading dot from suffix for method name
    suffix_clean = suffix.lstrip(".") if suffix else ""

    method_map = {
        "archive": "archive",
        "audio": "audio_asr",
        "video": "video_asr",
        "vlm": "vlm",
        "text": f"{suffix_clean}_text" if suffix_clean else "text",
        "ocr": "ocr",
        "tables": "tables",
        "unsupported": "unsupported",
    }

    return method_map.get(handler, "unknown")
