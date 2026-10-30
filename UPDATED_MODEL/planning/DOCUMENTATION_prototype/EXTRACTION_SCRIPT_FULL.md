# Universal File Extraction Script - Full Version

This is the **complete Python script** with PDF and Excel support for the Universal File Metadata & Version History Extractor.

---

## Complete Python Code with PDF + Excel Support

This version supports:
- **Text files** with embedded markers (high confidence)
- **PDF files** via PyPDF2/pdfplumber (medium confidence)
- **Excel files** via openpyxl (medium confidence)
- **Any file** via filesystem metadata (low confidence fallback)

**Copy this code to create `extract.py`:**

```python
#!/usr/bin/env python3
"""
Universal File Metadata & Version History Extractor - Full Version

Extracts maximum information from any file, tracks all historical changes,
builds knowledge graphs, and assigns confidence scores.

Supports: Text, PDF, Excel, Images, and any other file type.

Usage:
    python extract.py <file_path> [--output OUTPUT_FILE]
    
Example:
    python extract.py document.pdf --output result.json
    python extract.py data.xlsx --output result.json
"""

import os
import sys
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
import argparse

# Check for optional dependencies
try:
    import PyPDF2
    HAS_PYPdf2 = True
except ImportError:
    HAS_PYPdf2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

try:
    from PIL import Image
    import PIL.ExifTags
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# ============================================================================
# DATA CLASSES
# ============================================================================

class EditNode:
    """Represents a single edit/change to a file."""
    
    def __init__(self, edit_id: str, timestamp: str, author: Optional[str] = None,
                 edit_type: str = "create", content_before: Optional[str] = None,
                 content_after: Optional[str] = None,
                 affected_sections: Optional[List[str]] = None,
                 description: str = "", file_version: str = "1.0",
                 source: str = "unknown", confidence: str = "medium",
                 metadata: Optional[Dict] = None):
        self.edit_id = edit_id
        self.timestamp = timestamp
        self.author = author
        self.edit_type = edit_type
        self.content_before = content_before
        self.content_after = content_after
        self.affected_sections = affected_sections or []
        self.description = description
        self.file_version = file_version
        self.source = source
        self.confidence = confidence
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "node_id": self.edit_id,
            "node_type": "edit",
            "timestamp": self.timestamp,
            "author": self.author,
            "edit_type": self.edit_type,
            "content_before": self.content_before,
            "content_after": self.content_after,
            "affected_sections": self.affected_sections,
            "description": self.description,
            "file_version": self.file_version,
            "source": self.source,
            "evaluation_band": self.confidence
        }
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class KnowledgeGraph:
    """Directed graph representing file evolution."""
    
    def __init__(self):
        self.nodes: List[Dict] = []
        self.edges: List[Dict] = []
    
    def add_node(self, node_data: Dict) -> str:
        """Add a node to the graph."""
        node_id = node_data.get("node_id")
        if not node_id:
            node_id = hashlib.md5(json.dumps(node_data).encode()).hexdigest()
            node_data["node_id"] = node_id
        self.nodes.append(node_data)
        return node_id
    
    def add_edge(self, source_id: str, target_id: str, relationship: str,
                 timestamp: str, edge_type: str = "temporal", weight: float = 1.0) -> str:
        """Add an edge between nodes."""
        edge_id = f"edge_{source_id}_{target_id}"
        edge = {
            "edge_id": edge_id,
            "source": source_id,
            "target": target_id,
            "edge_type": edge_type,
            "relationship": relationship,
            "timestamp": timestamp,
            "weight": weight
        }
        self.edges.append(edge)
        return edge_id
    
    def to_dict(self) -> Dict:
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges)
        }


# ============================================================================
# VERSION HISTORY EXTRACTOR
# ============================================================================

class VersionHistoryExtractor:
    """Extracts version history from files using multiple methods."""
    
    def __init__(self):
        self.extractors = [
            self._extract_from_embedded_markers,
            self._extract_from_pdf_timestamps,
            self._extract_from_excel_metadata,
            self._extract_from_filesystem,
        ]
    
    def extract(self, file_path: Path) -> Tuple[List[EditNode], str]:
        """
        Main extraction method - tries all available sources.
        
        Returns:
            Tuple of (list of EditNodes, extraction source)
        """
        all_edits = []
        sources_used = []
        
        for extractor in self.extractors:
            try:
                result, source = extractor(file_path)
                if result:
                    all_edits.extend(result)
                    sources_used.append(source)
                    # If we got results from a good source, stop
                    if source in ["embedded_marker", "pdf_plumber", "pdf_pypdf2", "excel"]:
                        break
            except Exception as e:
                print(f"Warning: {extractor.__name__} failed: {e}", file=sys.stderr)
                continue
        
        # Sort by timestamp
        all_edits.sort(key=lambda x: x.timestamp)
        
        # Assign sequential versions
        for i, edit in enumerate(all_edits):
            edit.file_version = f"{i + 1}.0"
        
        return all_edits, sources_used
    
    # ---------------------------------------------------------------------------
    # TEXT FILE EXTRACTORS
    # ---------------------------------------------------------------------------
    
    def _extract_from_embedded_markers(self, file_path: Path) -> Tuple[List[EditNode], str]:
        """Extract edit history from embedded HTML-style markers."""
        edits = []
        
        # Only process text-based files
        text_extensions = ('.txt', '.md', '.csv', '.json', '.xml', '.html', '.py', '.js', '.sh')
        if not file_path.name.endswith(text_extensions):
            return edits, ""
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            print(f"Cannot read file {file_path}: {e}", file=sys.stderr)
            return edits, ""
        
        # Pattern: <!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: add -->
        pattern = r'<!--\s*EDIT:\s*([^|]+)\s*\|\s*AUTHOR:\s*([^|]+)\s*\|\s*TYPE:\s*([^|]+)'
        
        for i, match in enumerate(re.finditer(pattern, content)):
            timestamp = match.group(1).strip()
            author = match.group(2).strip()
            edit_type = match.group(3).strip().lower()
            
            # Get content after this marker
            content_start = match.end()
            content_text = content[content_start:].strip()
            
            # Find next marker or end of file
            next_match = next((m for m in re.finditer(pattern, content[content_start:])), None)
            if next_match:
                content_end = content_start + next_match.start()
                content_text = content[content_start:content_end].strip()
            
            # For delete operations, try to get content before
            content_before = None
            if edit_type == "delete":
                prev_matches = list(re.finditer(pattern, content[:content_start]))
                if prev_matches:
                    prev_match = prev_matches[-1]
                    content_before = content[prev_match.end():content_start].strip()
            
            edit_id = f"edit_{hashlib.md5(timestamp.encode()).hexdigest()[:8]}_{i}"
            
            edit = EditNode(
                edit_id=edit_id,
                timestamp=timestamp,
                author=author if author.lower() != "none" else None,
                edit_type=edit_type,
                content_before=content_before,
                content_after=content_text if edit_type != "delete" else None,
                source="embedded_marker",
                confidence="high"
            )
            edits.append(edit)
        
        return edits, "embedded_marker"
    
    # ---------------------------------------------------------------------------
    # PDF FILE EXTRACTORS
    # ---------------------------------------------------------------------------
    
    def _extract_pdf_metadata_with_pypdf2(self, file_path: Path) -> Dict:
        """Extract metadata from PDF using PyPDF2."""
        metadata = {}
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                doc_info = reader.metadata
                
                if doc_info:
                    metadata = {
                        "title": doc_info.get("/Title", ""),
                        "author": doc_info.get("/Author", ""),
                        "creator": doc_info.get("/Creator", ""),
                        "producer": doc_info.get("/Producer", ""),
                        "subject": doc_info.get("/Subject", ""),
                        "creation_date": doc_info.get("/CreationDate", ""),
                        "modification_date": doc_info.get("/ModDate", ""),
                        "page_count": len(reader.pages),
                        "source": "pypdf2"
                    }
        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}", file=sys.stderr)
        
        return metadata
    
    def _extract_pdf_metadata_with_pdfplumber(self, file_path: Path) -> Dict:
        """Extract metadata from PDF using pdfplumber."""
        metadata = {}
        try:
            with pdfplumber.open(file_path) as pdf:
                metadata = {
                    "author": pdf.metadata.get("author", ""),
                    "title": pdf.metadata.get("title", ""),
                    "subject": pdf.metadata.get("subject", ""),
                    "creator": pdf.metadata.get("creator", ""),
                    "producer": pdf.metadata.get("producer", ""),
                    "creation_date": pdf.metadata.get("creationdate", ""),
                    "page_count": len(pdf.pages),
                    "source": "pdfplumber"
                }
        except Exception as e:
            print(f"pdfplumber extraction failed: {e}", file=sys.stderr)
        
        return metadata
    
    def _extract_from_pdf_timestamps(self, file_path: Path) -> Tuple[List[EditNode], str]:
        """Extract metadata from PDF files."""
        if not file_path.name.lower().endswith(('.pdf',)):
            return [], ""
        
        if not (HAS_PYPdf2 or HAS_PDFPLUMBER):
            print("Warning: Neither PyPDF2 nor pdfplumber installed. Install with: pip install PyPDF2 pdfplumber", file=sys.stderr)
            return [], ""
        
        # Try both libraries
        metadata = {}
        if HAS_PYPdf2:
            metadata = self._extract_pdf_metadata_with_pypdf2(file_path)
        if not metadata and HAS_PDFPLUMBER:
            metadata = self._extract_pdf_metadata_with_pdfplumber(file_path)
        
        if not metadata:
            return [], ""
        
        # Convert PDF dates to ISO format
        creation_date = metadata.get("creation_date", "")
        mod_date = metadata.get("modification_date", "")
        
        # PDF dates are in format: D:YYYYMMDDHHmmSSZ or D:YYYYMMDDHHmmSS+00'00'
        def parse_pdf_date(pdf_date: str) -> str:
            if not pdf_date or pdf_date == "":
                return datetime.now(timezone.utc).isoformat() + "Z"
            # Remove D: prefix
            pdf_date = pdf_date.lstrip("D:")
            try:
                dt = datetime.strptime(pdf_date[:14], "%Y%m%d%H%M%S")
                return dt.isoformat() + "Z"
            except:
                return datetime.now(timezone.utc).isoformat() + "Z"
        
        # Create edit nodes
        edits = []
        
        # Creation edit
        creation_ts = parse_pdf_date(creation_date)
        edit_id = f"pdf_create_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}"
        
        creation_edit = EditNode(
            edit_id=edit_id,
            timestamp=creation_ts,
            author=metadata.get("author"),
            edit_type="create",
            description=f"PDF created: {metadata.get('title', file_path.name)}",
            metadata={
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "page_count": metadata.get("page_count", 0),
                "creator": metadata.get("creator", "")
            },
            source=metadata.get("source", "pdf_metadata"),
            confidence="high"
        )
        edits.append(creation_edit)
        
        # Modification edit (if different from creation)
        mod_ts = parse_pdf_date(mod_date)
        if mod_ts != creation_ts:
            edit_id = f"pdf_modify_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}"
            mod_edit = EditNode(
                edit_id=edit_id,
                timestamp=mod_ts,
                author=metadata.get("author"),
                edit_type="modify",
                description=f"PDF modified: {metadata.get('title', file_path.name)}",
                metadata={
                    "title": metadata.get("title", ""),
                    "page_count": metadata.get("page_count", 0)
                },
                source=metadata.get("source", "pdf_metadata"),
                confidence="high"
            )
            edits.append(mod_edit)
        
        return edits, metadata.get("source", "pdf_metadata")
    
    # ---------------------------------------------------------------------------
    # EXCEL FILE EXTRACTORS
    # ---------------------------------------------------------------------------
    
    def _extract_from_excel_metadata(self, file_path: Path) -> Tuple[List[EditNode], str]:
        """Extract metadata from Excel files using openpyxl."""
        if not file_path.name.lower().endswith(('.xlsx', '.xls')):
            return [], ""
        
        if not HAS_OPENPYXL:
            print("Warning: openpyxl not installed. Install with: pip install openpyxl", file=sys.stderr)
            return [], ""
        
        try:
            workbook = openpyxl.load_workbook(file_path, read_only=True)
            metadata = {
                "authorized": workbook.properties.author,
                "title": workbook.properties.title,
                "subject": workbook.properties.subject,
                "category": workbook.properties.category,
                "company": workbook.properties.company,
                "created": workbook.properties.created,
                "modified": workbook.properties.modified,
                "sheet_count": len(workbook.sheetnames),
                "sheet_names": list(workbook.sheetnames)
            }
            
            # Convert dates to ISO format
            created_iso = metadata["created"].isoformat() + "Z" if metadata["created"] else ""
            modified_iso = metadata["modified"].isoformat() + "Z" if metadata["modified"] else ""
        except Exception as e:
            print(f"Excel extraction failed: {e}", file=sys.stderr)
            return [], ""
        
        edits = []
        
        # Creation edit
        if created_iso:
            edit_id = f"excel_create_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}"
            creation_edit = EditNode(
                edit_id=edit_id,
                timestamp=created_iso,
                author=metadata.get("authorized"),
                edit_type="create",
                description=f"Excel workbook created: {metadata.get('title', file_path.name)}",
                metadata={
                    "title": metadata.get("title", ""),
                    "author": metadata.get("authorized", ""),
                    "sheet_count": metadata.get("sheet_count", 0),
                    "sheet_names": metadata.get("sheet_names", []),
                    "subject": metadata.get("subject", ""),
                    "category": metadata.get("category", ""),
                    "company": metadata.get("company", "")
                },
                source="excel",
                confidence="high"
            )
            edits.append(creation_edit)
        
        # Modification edit
        if modified_iso and modified_iso != created_iso:
            edit_id = f"excel_modify_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}"
            mod_edit = EditNode(
                edit_id=edit_id,
                timestamp=modified_iso,
                author=metadata.get("authorized"),
                edit_type="modify",
                description=f"Excel workbook modified: {metadata.get('title', file_path.name)}",
                metadata={
                    "sheet_count": metadata.get("sheet_count", 0),
                    "sheet_names": metadata.get("sheet_names", []),
                    "title": metadata.get("title", "")
                },
                source="excel",
                confidence="high"
            )
            edits.append(mod_edit)
        
        return edits, "excel"
    
    # ---------------------------------------------------------------------------
    # FALLBACK EXTRACTORS
    # ---------------------------------------------------------------------------
    
    def _extract_from_filesystem(self, file_path: Path) -> Tuple[List[EditNode], str]:
        """Fallback: use file system metadata."""
        try:
            stat = file_path.stat()
            timestamp = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            
            edit_id = f"fs_{file_path.name}_{stat.st_mtime}"
            
            # Try to get content
            content = None
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    contentLucy = f.read()
                content = contentLucy[:500] + "..." if len(contentLucy) > 500 else contentLucy
            except:
                content = f"[Binary file: {file_path.name}, size: {stat.st_size} bytes]"
            
            edit = EditNode(
                edit_id=edit_id,
                timestamp=timestamp,
                author=None,
                edit_type="create",
                content_after=content,
                metadata={
                    "file_size": stat.st_size,
                    "created_time": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
                    "accessed_time": datetime.fromtimestamp(stat.st_atime, tz=timezone.utc).isoformat()
                },
                source="filesystem",
                confidence="low"
            )
            return [edit], "filesystem"
        except Exception as e:
            print(f"Filesystem extraction failed: {e}", file=sys.stderr)
            return [], ""


# ============================================================================
# MAIN EXTRACTION FUNCTION
# ============================================================================

def extract_file(file_path: str) -> Dict[str, Any]:
    """
    Extract all information from a file and build knowledge graph.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Dictionary with extraction results
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Step 1: Extract version history
    version_extractor = VersionHistoryExtractor()
    edits, sources_used = version_extractor.extract(file_path)
    
    # Step 2: Extract additional metadata
    additional_metadata = _extract_additional_metadata(file_path, edits)
    
    # Step 3: Build knowledge graph
    kg = KnowledgeGraph()
    
    # Add metadata node
    file_node = {
        "node_id": f"file_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}",
        "node_type": "file",
        "name": file_path.name,
        "path": str(file_path),
        "size": file_path.stat().st_size,
        "type": _get_file_type(file_path),
        "evaluation_band": "high"
    }
    kg.add_node(file_node)
    
    # Add edit nodes
    for i, edit in enumerate(edits):
        node_dict = edit.to_dict()
        kg.add_node(node_dict)
        # Add edge from file to first edit
        if i == 0:
            kg.add_edge(file_node["node_id"], edit.edit_id, "has_edit", edit.timestamp)
    
    # Add edges between consecutive edits
    for i in range(len(edits) - 1):
        current = edits[i]
        next_edit = edits[i + 1]
        
        # Determine relationship
        if current.edit_type == "delete" and next_edit.edit_type in ["add", "create"]:
            relationship = "replaces"
        elif current.edit_type in ["create", "add"] and next_edit.edit_type in ["add", "modify"]:
            relationship = "adds_to"
        elif current.edit_type == "create":
            relationship = "adds_to"
        else:
            relationship = "modifies"
        
        kg.add_edge(
            current.edit_id,
            next_edit.edit_id,
            relationship=relationship,
            timestamp=next_edit.timestamp
        )
    
    # Step 4: Build result
    all_sources = list(set(sources_used + [e.source for e in edits]))
    
    confidence_dist = {
        "high": sum(1 for e in edits if e.confidence == "high"),
        "medium": sum(1 for e in edits if e.confidence == "medium"),
        "low": sum(1 for e in edits if e.confidence == "low")
    }
    
    result = {
        "extraction_metadata": {
            "file": str(file_path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "extractor_version": "2.0.0",
            "dependencies": {
                "PyPDF2": HAS_PYPdf2,
                "pdfplumber": HAS_PDFPLUMBER,
                "openpyxl": HAS_OPENPYXL,
                "PIL": HAS_PIL
            }
        },
        "file_metadata": additional_metadata,
        "version_history": {
            "edits": [e.to_dict() for e in edits],
            "edit_count": len(edits),
            "sources_used": all_sources
        },
        "knowledge_graph": kg.to_dict(),
        "summary": {
            "total_edits": len(edits),
            "total_nodes": len(kg.nodes) - 1,  # Exclude file node
            "total_edges": len(kg.edges),
            "sources_used": all_sources,
            "confidence_distribution": confidence_dist
        }
    }
    
    return result


def _extract_additional_metadata(file_path: Path, edits: List[EditNode]) -> Dict:
    """Extract additional metadata based on file type."""
    metadata = {"filesystem": {}}
    
    try:
        stat = file_path.stat()
        metadata["filesystem"] = {
            "size_bytes": stat.st_size,
            "created_time": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "accessed_time": datetime.fromtimestamp(stat.st_atime, tz=timezone.utc).isoformat()
        }
    except:
        pass
    
    # JSON detection
    if file_path.name.endswith('.json'):
        try:
            with open(file_path, 'r') as f:
                json_data = json.load(f)
                metadata["json_content"] = {
                    "key_count": len(json_data) if isinstance(json_data, dict) else None,
                    "array_length": len(json_data) if isinstance(json_data, list) else None
                }
        except:
            pass
    
    # Text file statistics
    text_extensions = ('.txt', '.md', '.csv', '.json', '.xml', '.html', '.py', '.js', '.sh')
    if file_path.name.endswith(text_extensions):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            metadata["text"] = {
                "character_count": len(content),
                "line_count": content.count('\n') + 1,
                "word_count": len(content.split())
            }
        except:
            pass
    
    # Excel metadata
    if file_path.name.lower().endswith(('.xlsx', '.xls')):
        try:
            if HAS_OPENPYXL:
                workbook = openpyxl.load_workbook(file_path, read_only=True)
                metadata["excel"] = {
                    "sheet_count": len(workbook.sheetnames),
                    "sheet_names": list(workbook.sheetnames),
                    "total_cells": sum(
                        len(list(sheet.rows)) * len(list(sheet.columns))
                        for sheet in workbook
                    )
                }
        except:
            pass
    
    # PDF metadata
    if file_path.name.lower().endswith('.pdf'):
        try:
            if HAS_PYPdf2:
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    metadata["pdf"] = {
                        "page_count": len(reader.pages),
                        "is_encrypted": reader.is_encrypted,
                        "metadata": dict(reader.metadata) if reader.metadata else {}
                    }
            elif HAS_PDFPLUMBER:
                with pdfplumber.open(file_path) as pdf:
                    metadata["pdf"] = {
                        "page_count": len(pdf.pages),
                        "metadata": pdf.metadata
                    }
        except:
            pass
    
    return metadata


def _get_file_type(file_path: Path) -> str:
    """Get file type category."""
    ext = file_path.name.lower()
    
    if ext.endswith('.pdf'):
        return "pdf"
    elif ext.endswith(('.xlsx', '.xls')):
        return "excel"
    elif ext.endswith(('.txt', '.md', '.csv', '.tsv', '.json', '.xml', '.yaml', '.yml', '.html', '.css', '.js', '.py')):
        return "text"
    elif ext.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
        return "image"
    elif ext.endswith(('.mp3', '.wav', '.ogg', '.flac', '.aac')):
        return "audio"
    elif ext.endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.wmv')):
        return "video"
    elif ext.endswith('.docx'):
        return "word"
    elif ext.endswith('.zip'):
        return "archive"
    else:
        return "other"


# ============================================================================
# OUTPUT FORMATTERS
# ============================================================================

def format_json(result: Dict, pretty: bool = True) -> str:
    """Format as JSON."""
    if pretty:
        return json.dumps(result, indent=2, default=str)
    return json.dumps(result, default=str)


def format_simple(result: Dict) -> str:
    """Format as simple text summary."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"File: {result['extraction_metadata']['file']}")
    lines.append("=" * 60)
    lines.append(f"\nVersion History:")
    lines.append(f"  Total edits: {result['summary']['total_edits']}")
    lines.append(f"  Sources: {', '.join(result['summary']['sources_used'])}")
    lines.append(f"\nKnowledge Graph:")
    lines.append(f"  Nodes: {result['summary']['total_nodes']}")
    lines.append(f"  Edges: {result['summary']['total_edges']}")
    lines.append(f"\nConfidence Distribution:")
    for band, count in result['summary']['confidence_distribution'].items():
        lines.append(f"  {band.capitalize()}: {count}")
    
    if result['version_history']['edits']:
        lines.append(f"\nEdit Timeline:")
        for edit in result['version_history']['edits']:
            lines.append(f"  [{edit['timestamp']}] {edit['author'] or 'Unknown'} - {edit['edit_type']}")
    
    return "\n".join(lines)


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Universal File Metadata & Version History Extractor - Full Version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract.py document.txt --output result.json
  python extract.py report.pdf --output result.json
  python extract.py data.xlsx --output result.json
  python extract.py image.png --simple
        """
    )
    
    parser.add_argument('file', help='Path to the file to extract')
    parser.add_argument('--output', '-o', help='Output file path (default: stdout)')
    parser.add_argument('--format', '-f', choices=['json', 'simple'],
                        default='json', help='Output format (default: json)')
    parser.add_argument('--pretty', action='store_true', default=True,
                        help='Pretty print JSON (default: True)')
    parser.add_argument('--no-pretty', action='store_false', dest='pretty')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Check dependencies
    if args.verbose:
        print("Dependency Status:", file=sys.stderr)
        print(f"  PyPDF2: {HAS_PYPdf2}", file=sys.stderr)
        print(f"  pdfplumber: {HAS_PDFPLUMBER}", file=sys.stderr)
        print(f"  openpyxl: {HAS_OPENPYXL}", file=sys.stderr)
        print(f"  PIL: {HAS_PIL}", file=sys.stderr)
    
    try:
        result = extract_file(args.file)
        
        # Format output
        if args.format == 'json':
            output = format_json(result, pretty=args.pretty)
        else:
            output = format_simple(result)
        
        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Output written to: {args.output}", file=sys.stderr)
        else:
            print(output)
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Check that the file path is correct.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Extraction failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## Installation Requirements

```bash
pip install PyPDF2 pdfplumber openpyxl Pillow python-magic
```

## Test Commands

```bash
# Test with text file
python3 extract.py samples/text1.txt --output results/text1.json

# Test with PDF file  
python3 extract.py samples/report.pdf --output results/report.json

# Test with Excel file
python3 extract.py samples/data.xlsx --output results/data.json

# Simple format
python3 extract.py samples/text1.txt --format simple

# Verbose mode
python3 extract.py samples/report.pdf --verbose
```

---

## What This Version Adds

1. **PDF Support**: Extract metadata using PyPDF2 and/or pdfplumber
2. **Excel Support**: Extract workbook properties and metadata using openpyxl
3. **Dependency Detection**: Auto-detect which libraries are installed
4. **Simple Format**: Human-readable output option
5. **File Type Detection**: Automatic categorization of files
6. **Enhanced Metadata**: Extract additional type-specific metadata
7. **File Node**: Add file itself as a node in the knowledge graph

---

## How to Create extract.py

Run this exact command:

```bash
cd /home/karthikean.juttumaha/mini-extract/prototype
python3 -c "
import re
with open('EXTRACTION_SCRIPT_FULL.md', 'r') as f:
    content = f.read()
code = re.search(r'```python(.*?)```', content, re.DOTALL)
if code:
    with open('extract.py', 'w') as f:
        f.write(code.group(1))
    print('extract.py created successfully from EXTRACTION_SCRIPT_FULL.md')
else:
    print('ERROR: Python code not found in EXTRACTION_SCRIPT_FULL.md')
"
```

This will extract the Python code and save it as `extract.py`.
