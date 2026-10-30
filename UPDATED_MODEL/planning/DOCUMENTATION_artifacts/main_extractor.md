# Main Extractor Module (extract.py)

## Overview
This is the main entry point for the Universal File Metadata & Version History Extractor.

## File: `extract.py`

```python
#!/usr/bin/env python3
"""
Universal File Metadata & Version History Extractor

Extracts maximum information from any file, tracks all historical changes,
and builds a knowledge graph of the file's evolution.

Usage:
    python extract.py <file_path> [options]

Examples:
    python extract.py samples4/multi_edit_text.txt
    python extract.py samples4/document.docx --output-format json
    python extract.py ~/projects/repo/file.py --git-repo ~/projects/repo
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler('extraction.log')
    ]
)
logger = logging.getLogger(__name__)

# Import our modules
# These will be separate files: version_extractor.py, graph_builder.py, etc.
# For now, we'll include the key interfaces

try:
    # Try importing from package
    from extractor import FlowPipeline
    from version_extractor import (
        extract_version_history, 
        EditNode, 
        VersionAnalyzer,
        KnowledgeGraphBuilder,
        EvaluationBandAssigner
    )
except ImportError:
    # For standalone script, include inline or handle gracefully
    logger.warning("Could not import extraction modules. Using basic functionality.")
    FlowPipeline = None


def get_file_type(file_path: Path) -> str:
    """Detect file type using extension."""
    ext = file_path.suffix.lower()
    type_map = {
        '.txt': 'text/plain',
        '.md': 'text/markdown',
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.doc': 'application/msword',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xls': 'application/vnd.ms-excel',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
        '.zip': 'application/zip',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.csv': 'text/csv',
        '.html': 'text/html',
        '.py': 'text/x-python'
    }
    return type_map.get(ext, 'application/octet-stream')


def extract_metadata(file_path: Path) -> Dict:
    """Extract basic metadata from file system."""
    try:
        stat = file_path.stat()
        return {
            "path": str(file_path),
            "type": get_file_type(file_path),
            "size_bytes": stat.st_size,
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat() + "Z",
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
            "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error getting metadata: {e}")
        return {}


def extract_all_metadata(file_path: Path) -> Dict:
    """
    Extract ALL available metadata using multi-model extraction.
    
    This is the main extraction function that uses:
    - File system metadata
    - Format-specific extractors
    - Content extractors
    """
    metadata = extract_metadata(file_path)
    file_type = metadata.get("type", "")
    
    # Multi-model extraction based on file type
    extraction_results = {"filesystem": metadata}
    
    # Text files
    if file_type.startswith("text/"):
        extraction_results["text"] = extract_text_metadata(file_path)
    
    # PDF files
    elif file_type == "application/pdf":
        extraction_results["pdf"] = extract_pdf_metadata(file_path)
    
    # Word documents
    elif "word" in file_type:
        extraction_results["word"] = extract_word_metadata(file_path)
    
    # Excel files
    elif "excel" in file_type or "spreadsheet" in file_type:
        extraction_results["excel"] = extract_excel_metadata(file_path)
    
    # Images
    elif file_type.startswith("image/"):
        extraction_results["image"] = extract_image_metadata(file_path)
    
    # Audio
    elif file_type.startswith("audio/"):
        extraction_results["audio"] = extract_audio_metadata(file_path)
    
    # Video
    elif file_type.startswith("video/"):
        extraction_results["video"] = extract_video_metadata(file_path)
    
    # Archives
    elif "zip" in file_type or "tar" in file_type or "gzip" in file_type:
        extraction_results["archive"] = extract_archive_metadata(file_path)
    
    return {
        "metadata": extraction_results,
        "extracted_at": datetime.utcnow().isoformat() + "Z"
    }


def extract_text_metadata(file_path: Path) -> Dict:
    """Extract metadata from text files."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        return {
            "format": "text",
            "encoding": "utf-8",
            "line_count": content.count('\n') + 1,
            "word_count": len(content.split()),
            "character_count": len(content),
            "has_bom": content.startswith('\ufeff')
        }
    except Exception as e:
        logger.warning(f"Error extracting text metadata: {e}")
        return {"error": str(e)}


def extract_pdf_metadata(file_path: Path) -> Dict:
    """Extract metadata from PDF files."""
    try:
        # Try pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(str(file_path)) as pdf:
                metadata = pdf.metadata
                page_count = len(pdf.pages)
                
                # Check if scanned
                text_length = 0
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_length += len(text)
                
                return {
                    "format": "pdf",
                    "page_count": page_count,
                    "text_length": text_length,
                    "is_scanned": text_length < 80,
                    "metadata": {
                        "author": metadata.get("author"),
                        "title": metadata.get("title"),
                        "subject": metadata.get("subject"),
                        "creator": metadata.get("creator"),
                        "producer": metadata.get("producer"),
                        "creation_date": metadata.get("creation_date"),
                        "modification_date": metadata.get("modification_date")
                    }
                }
        except ImportError:
            pass
        
        # Try PyPDF2
        try:
            from PyPDF2 import PdfReader
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                metadata = reader.metadata
                
                return {
                    "format": "pdf",
                    "page_count": len(reader.pages),
                    "metadata": {
                        "author": metadata.get("/Author"),
                        "title": metadata.get("/Title"),
                        "subject": metadata.get("/Subject"),
                        "creator": metadata.get("/Creator"),
                        "producer": metadata.get("/Producer"),
                        "creation_date": metadata.get("/CreationDate"),
                        "modification_date": metadata.get("/ModDate")
                    }
                }
        except ImportError:
            pass
        
        return {"format": "pdf", "note": "No PDF library available"}
        
    except Exception as e:
        logger.warning(f"Error extracting PDF metadata: {e}")
        return {"error": str(e)}


def extract_word_metadata(file_path: Path) -> Dict:
    """Extract metadata from Word documents."""
    try:
        from docx import Document
        doc = Document(str(file_path))
        props = doc.core_properties
        
        return {
            "format": "word",
            "paragraph_count": len(doc.paragraphs),
            "table_count": len(doc.tables),
            "metadata": {
                "title": props.title,
                "author": props.author,
                "subject": props.subject,
                "created": props.created.isoformat() if props.created else None,
                "modified": props.modified.isoformat() if props.modified else None,
                "revision": props.revision,
                "version": props.version
            }
        }
    except ImportError:
        logger.warning("python-docx not installed")
        return {"format": "word", "note": "python-docx not available"}
    except Exception as e:
        logger.warning(f"Error extracting Word metadata: {e}")
        return {"error": str(e)}


def extract_excel_metadata(file_path: Path) -> Dict:
    """Extract metadata from Excel files."""
    try:
        from openpyxl import load_workbook
        wb = load_workbook(str(file_path), read_only=True)
        props = wb.properties
        
        return {
            "format": "excel",
            "sheet_count": len(wb.sheetnames),
            "sheet_names": wb.sheetnames,
            "metadata": {
                "title": props.title,
                "author": props.creator,
                "subject": props.subject,
                "created": props.created.isoformat() if props.created else None,
                "modified": props.modified.isoformat() if props.modified else None
            }
        }
    except ImportError:
        logger.warning("openpyxl not installed")
        return {"format": "excel", "note": "openpyxl not available"}
    except Exception as e:
        logger.warning(f"Error extracting Excel metadata: {e}")
        return {"error": str(e)}


def extract_image_metadata(file_path: Path) -> Dict:
    """Extract metadata from image files."""
    try:
        from PIL import Image
        with Image.open(str(file_path)) as img:
            metadata = {
                "format": img.format,
                "mode": img.mode,
                "size": {"width": img.width, "height": img.height},
                "bits": img.bits if hasattr(img, 'bits') else None
            }
            
            # Try to get EXIF
            try:
                if hasattr(img, '_getexif'):
                    exif = img._getexif()
                    if exif:
                        from PIL.ExifTags import TAGS
                        exif_data = {}
                        for tag, value in exif.items():
                            decoded = TAGS.get(tag, tag)
                            exif_data[decoded] = str(value)
                        metadata["exif"] = exif_data
            except:
                pass
            
            return {"format": "image", "image": metadata}
    except ImportError:
        logger.warning("Pillow not installed")
        return {"format": "image", "note": "Pillow not available"}
    except Exception as e:
        logger.warning(f"Error extracting image metadata: {e}")
        return {"error": str(e)}


def extract_audio_metadata(file_path: Path) -> Dict:
    """Extract metadata from audio files."""
    try:
        # Try pydub
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(file_path))
            return {
                "format": "audio",
                "duration_seconds": len(audio) / 1000,
                "channels": audio.channels,
                "sample_width": audio.sample_width,
                "frame_rate": audio.frame_rate
            }
        except ImportError:
            pass
        
        # Try mutagen
        try:
            import mutagen
            from mutagen import File as MutagenFile
            audio = MutagenFile(str(file_path))
            return {
                "format": "audio",
                "duration_seconds": int(audio.info.length) if audio.info else None,
                "tags": dict(audio.tags) if audio.tags else {}
            }
        except ImportError:
            pass
        
        return {"format": "audio", "note": "No audio library available"}
        
    except Exception as e:
        logger.warning(f"Error extracting audio metadata: {e}")
        return {"error": str(e)}


def extract_video_metadata(file_path: Path) -> Dict:
    """Extract metadata from video files."""
    try:
        # Try OpenCV
        try:
            import cv2
            cap = cv2.VideoCapture(str(file_path))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            cap.release()
            
            return {
                "format": "video",
                "frame_count": frame_count,
                "fps": fps,
                "resolution": {"width": width, "height": height},
                "duration_seconds": duration
            }
        except ImportError:
            pass
        
        # Try FFmpeg (ffprobe)
        try:
            import subprocess
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration,bit_rate,format_name',
                '-show_entries', 'stream=codec_type,codec_name,width,height,fps',
                '-of', 'json',
                str(file_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {
                "format": "video",
                "ffprobe": json.loads(result.stdout)
            }
        except:
            pass
        
        return {"format": "video", "note": "No video library available"}
        
    except Exception as e:
        logger.warning(f"Error extracting video metadata: {e}")
        return {"error": str(e)}


def extract_archive_metadata(file_path: Path) -> Dict:
    """Extract metadata from archive files."""
    try:
        import zipfile
        import tarfile
        
        if file_path.suffix == '.zip':
            with zipfile.ZipFile(str(file_path), 'r') as zf:
                return {
                    "format": "archive",
                    "type": "zip",
                    "member_count": len(zf.namelist()),
                    "members": zf.namelist(),
                    "total_size": sum(empty for empty in [zf.getinfo(m).file_size for m in zf.namelist()])
                }
        elif file_path.suffix in ['.tar', '.tar.gz', '.tgz', '.tar.bz2']:
            mode = 'r:' + file_path.suffix[1:] if file_path.suffix != '.tar' else 'r:'
            with tarfile.open(str(file_path), mode) as tf:
                return {
                    "format": "archive",
                    "type": "tar",
                    "member_count": len(tf.getmembers()),
                    "members": [m.name for m in tf.getmembers()]
                }
        else:
            return {"format": "archive", "type": "unknown"}
            
    except Exception as e:
        logger.warning(f"Error extracting archive metadata: {e}")
        return {"error": str(e)}


# ============================================================================
# MAIN EXTRACTION FUNCTIONS
# ============================================================================

def extract_file(file_path: str, git_repo_path: Optional[str] = None,
                 output_format: str = "json") -> Dict:
    """
    Main extraction function.
    
    Extracts:
    1. All available metadata
    2. File content (if applicable)
    3. Version history
    4. Builds knowledge graph
    5. Assigns evaluation bands
    
    Args:
        file_path: Path to the file to extract
        git_repo_path: Optional path to git repository
        output_format: Output format (json, graphml, gexf)
    
    Returns:
        Dictionary containing all extracted information
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    logger.info(f"Starting extraction for: {file_path}")
    
    # Step 1: Extract metadata
    logger.info("Extracting metadata...")
    metadata_result = extract_all_metadata(file_path)
    
    # Step 2: Extract version history
    logger.info("Extracting version history...")
    git_path = Path(git_repo_path) if git_repo_path else None
    version_result = extract_version_history(str(file_path), str(git_path) if git_path else None)
    
    # Step 3: Build response
    result = {
        "extraction_metadata": {
            "file": str(file_path),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "extractor_version": "1.0.0"
        },
        "file_metadata": metadata_result["metadata"],
        "version_history": version_result,
        "knowledge_graph": version_result.get("knowledge_graph", {}),
        "summary": version_result.get("summary", {}),
        "evaluation_bands": {
            "metadata_confidence": _evaluate_metadata_confidence(metadata_result),
            "version_confidence": _evaluate_version_confidence(version_result)
        }
    }
    
    # Step 4: Format output
    if output_format == "json":
        return result
    elif output_format == "graphml":
        return _format_as_graphml(result)
    elif output_format == "gexf":
        return _format_as_gexf(result)
    else:
        return result


def _evaluate_metadata_confidence(metadata_result: Dict) -> str:
    """Evaluate overall confidence of metadata extraction."""
    success_count = 0
    total_count = 0
    
    for source, result in metadata_result.get("metadata", {}).items():
        total_count += 1
        if "error" not in result and "note" not in result:
            success_count += 1
    
    if total_count == 0:
        return "low"
    
    ratio = success_count / total_count
    if ratio > 0.7:
        return "high"
    elif ratio > 0.4:
        return "medium"
    else:
        return "low"


def _evaluate_version_confidence(version_result: Dict) -> str:
    """Evaluate overall confidence of version history extraction."""
    edits = version_result.get("edits", [])
    if not edits:
        return "low"
    
    summary = version_result.get("summary", {})
    sources = summary.get("sources_used", [])
    
    # High confidence if we have git or word track changes
    if "git" in sources or "word_track_changes" in sources:
        return "high"
    
    # Medium confidence for embedded markers
    if "embedded_marker" in sources or "embedded_marker_yaml" in sources:
        return "medium"
    
    # Low confidence for filesystem only
    return "low"


def _format_as_graphml(result: Dict) -> str:
    """Format result as GraphML."""
    kg = result.get("knowledge_graph", {})
    nodes = kg.get("nodes", [])
    edges = kg.get("edges", [])
    
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<graphml xmlns="http://graphml.graphdrawing.org/xmlns" ')
    lines.append('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ')
    lines.append('xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns ')
    lines.append('http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">')
    
    # Add keys for attributes
    lines.append('  <key id="node_id" for="node" attr.name="node_id" attr.type="string"/>')
    lines.append('  <key id="timestamp" for="node" attr.name="timestamp" attr.type="string"/>')
    lines.append('  <key id="Author" for="node" attr.name="Author" attr.type="string"/>')
    lines.append('  <key id="edit_type" for="node" attr.name="edit_type" attr.type="string"/>')
    lines.append('  <key id="content" for="node" attr.name="content" attr.type="string"/>')
    lines.append('  <key id="confidence" for="node" attr.name="confidence" attr.type="string"/>')
    lines.append('  <key id="relationship" for="edge" attr.name="relationship" attr.type="string"/>')
    lines.append('  <key id="weight" for="edge" attr.name="weight" attr.type="double"/>')
    
    lines.append('  <graph id="FileHistory" edgemode="directed">')
    
    # Add nodes
    for node in nodes:
        lines.append(f'    <node id="{node.get("node_id", "")}">')
        if node.get("node_id"):
            lines.append(f'      <data key="node_id">{node["node_id"]}</data>')
        if node.get("timestamp"):
            lines.append(f'      <data key="timestamp">{node["timestamp"]}</data>')
        if node.get("author"):
            lines.append(f'      <data key="Author">{node["author"]}</data>')
        if node.get("edit_type"):
            lines.append(f'      <data key="edit_type">{node["edit_type"]}</data>')
        if node.get("content_after"):
            content_preview = node["content_after"][:100] + "..." if len(node["content_after"]) > 100 else node["content_after"]
            lines.append(f'      <data key="content">{content_preview}</data>')
        if node.get("evaluation_band"):
            lines.append(f'      <data key="confidence">{node["evaluation_band"]}</data>')
        lines.append('    </node>')
    
    # Add edges
    for edge in edges:
        lines.append(f'    <edge id="{edge.get("edge_id", "")}" source="{edge.get("source", "")}" target="{edge.get("target", "")}">')
        if edge.get("relationship"):
            lines.append(f'      <data key="relationship">{edge["relationship"]}</data>')
        lines.append(f'      <data key="weight">{edge.get("weight", 1.0)}</data>')
        lines.append('    </edge>')
    
    lines.append('  </graph>')
    lines.append('</graphml>')
    
    return "\n".join(lines)


def _format_as_gexf(result: Dict) -> str:
    """Format result as GEXF for Gephi."""
    kg = result.get("knowledge_graph", {})
    nodes = kg.get("nodes", [])
    edges = kg.get("edges", [])
    
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">')
    lines.append('  <meta lastmodifieddate="' + datetime.utcnow().isoformat() + '">')
    lines.append('    <creator>File History Extractor</creator>')
    lines.append('    <description>File edit history knowledge graph</description>')
    lines.append('  </meta>')
    lines.append('  <graph mode="static" defaultedgetype="directed">')
    
    # Attributes
    lines.append('    <attributes class="node">')
    lines.append('      <attribute id="timestamp" title="Timestamp" type="string"/>')
    lines.append('      <attribute id="author" title="Author" type="string"/>')
    lines.append('      <attribute id="edit_type" title="Edit Type" type="string"/>')
    lines.append('      <attribute id="confidence" title="Confidence" type="string"/>')
    lines.append('    </attributes>')
    lines.append('    <attributes class="edge">')
    lines.append('      <attribute id="relationship" title="Relationship" type="string"/>')
    lines.append('      <attribute id="weight" title="Weight" type="float"/>')
    lines.append('    </attributes>')
    
    # Nodes
    lines.append('    <nodes>')
    for node in nodes:
        node_id = node.get("node_id", "")
        label = node.get("description", node.get("edit_type", ""))[:30]
        conf = node.get("evaluation_band", "medium")
        
        lines.append(f'      <node id="{node_id}" label="{label}">')
        lines.append('        <attvalues>')
        if node.get("timestamp"):
            lines.append(f'          <attvalue for="timestamp" value="{node["timestamp"]}"/>')
        if node.get("author"):
            lines.append(f'          <attvalue for="author" value="{node["author"]}"/>')
        if node.get("edit_type"):
            lines.append(f'          <attvalue for="edit_type" value="{node["edit_type"]}"/>')
        lines.append(f'          <attvalue for="confidence" value="{conf}"/>')
        lines.append('        </attvalues>')
        lines.append('      </node>')
    lines.append('    </nodes>')
    
    # Edges
    lines.append('    <edges>')
    for edge in edges:
        lines.append(f'      <edge id="{edge.get("edge_id", "")}" source="{edge.get("source", "")}" target="{edge.get("target", "")}">')
        lines.append('        <attvalues>')
        if edge.get("relationship"):
            lines.append(f'          <attvalue for="relationship" value="{edge["relationship"]}"/>')
        lines.append(f'          <attvalue for="weight" value="{edge.get("weight", 1.0)}"/>')
        lines.append('        </attvalues>')
        lines.append('      </edge>')
    lines.append('    </edges>')
    
    lines.append('  </graph>')
    lines.append('</gexf>')
    
    return "\n".join(lines)


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Universal File Metadata & Version History Extractor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract.py file.txt
  python extract.py document.docx --output-format json
  python extract.py file.py --git-repo /path/to/repo
  python extract.py file.txt --output graph.graphml
        """
    )
    
    parser.add_argument('file', help='Path to the file to extract')
    parser.add_argument('--git-repo', help='Path to git repository (if different from file location)')
    parser.add_argument('--output-format', choices=['json', 'graphml', 'gexf'], 
                        default='json', help='Output format (default: json)')
    parser.add_argument('--output', '-o', help='Output file path (default: stdout)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    try:
        # Run extraction
        result = extract_file(
            args.file,
            git_repo_path=args.git_repo,
            output_format=args.output_format
        )
        
        # Format output
        if args.output_format == 'json':
            output = json.dumps(result, indent=2, default=str)
        else:
            output = result
        
        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            logger.info(f"Output written to: {args.output}")
        else:
            print(output)
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Usage Examples

### 1. Basic Extraction
```bash
python extract.py samples4/multi_edit_text.txt
```

### 2. With Git Repository
```bash
python extract.py src/main.py --git-repo /path/to/project
```

### 3. Save to File
```bash
python extract.py document.docx --output result.json
```

### 4. GraphML Output (for visualization)
```bash
python extract.py samples4/multi_edit_text.txt --output-format graphml -o graph.graphml
```

### 5. GEXF Output (for Gephi)
```bash
python extract.py samples4/multi_edit_text.txt --output-format gexf -o graph.gexf
```

## Integration with Flow Pipeline

This main extractor orchestrates the complete flow pipeline:

1. **Ingestion**: `Path(file_path).exists()` and type detection
2. **Multi-Model Extraction**: `extract_all_metadata()` calls multiple extractors
3. **Version Analysis**: `extract_version_history()` extracts edit history
4. **Knowledge Graph Construction**: Built by `extract_version_history()`
5. **Evaluation Band Assignment**: `_evaluate_*_confidence()` functions
6. **Output**: Formatted as JSON, GraphML, or GEXF

## Testing with samples4

To test with the samples4 files:

```bash
# Create the samples4 directory structure
mkdir -p samples4/text_files
mkdir -p samples4/documents

# Create test files (use the content from samples4_design.md)
# Then run extraction
python extract.py samples4/text_files/multi_edit_text.txt

# Validate against expected history
python -c "
import json
with open('result.json') as f:
    result = json.load(f)
with open('samples4/text_files/multi_edit_text.history.json') as f:
    expected = json.load(f)
# Compare edits
print('Validation not yet implemented')
"
```

## Next Steps

1. Create the actual samples4 files with embedded markers
2. Implement the version_extractor.py module
3. Create the graph visualization
4. Add more extraction methods
5. Test with various file types
6. Optimize performance for large files
