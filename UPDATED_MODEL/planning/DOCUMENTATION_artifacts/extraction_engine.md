---
format: html
---

# Universal File Extraction Engine

## Overview
This module implements the **Universal File Metadata & Version History Extractor** as specified in `artifacts/proposal.md` and `artifacts/specs.md`. It follows the flow pipeline to extract maximum information from any file, track all changes, and build a knowledge graph.

## File: `extract.py` (Main Entry Point)

```python
#!/usr/bin/env python3
"""
Universal File Metadata & Version History Extractor

Usage:
    python extract.py <file_path>
    python extract.py --git-repo <repo_path> <file_path>
    python extract.py --output-format graphml|gexf|json <file_path>
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import hashlib
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


class EvaluationBand:
    """Confidence scoring for extracted data."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EditNode:
    """Represents a single edit/change to a file."""
    
    def __init__(self, edit_id: str, timestamp: str, author: Optional[str], 
                 edit_type: str, content_before: Optional[str], 
                 content_after: Optional[str], affected_sections: List[str],
                 description: str, file_version: str, source: str, 
                 confidence: str = EvaluationBand.MEDIUM):
        self.edit_id = edit_id
        self.timestamp = timestamp
        self.author = author
        self.edit_type = edit_type  # create, add, modify, delete
        self.content_before = content_before
        self.content_after = content_after
        self.affected_sections = affected_sections
        self.description = description
        self.file_version = file_version
        self.source = source
        self.confidence = confidence
    
    def to_dict(self) -> Dict:
        return {
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


class FileMetadata:
    """Container for all extracted metadata."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_type = None
        self.size_bytes = 0
        self.created_time = None
        self.modified_time = None
        self.accessed_time = None
        self.metadata = {}
        self.content = None
        self.version_history = []
        self.extraction_results = []
        self.knowledge_graph = None
    
    def to_dict(self) -> Dict:
        return {
            "file": {
                "path": str(self.file_path),
                "type": self.file_type,
                "size_bytes": self.size_bytes,
                "created_time": self.created_time,
                "modified_time": self.modified_time,
                "accessed_time": self.accessed_time
            },
            "metadata": self.metadata,
            "content": self.content,
            "version_history": [edit.to_dict() for edit in self.version_history],
            "extraction_results": self.extraction_results,
            "knowledge_graph": self.knowledge_graph,
            "extracted_at": datetime.utcnow().isoformat() + "Z"
        }


class KnowledgeGraph:
    """Directed graph representing file evolution."""
    
    def __init__(self):
        self.nodes = []
        self.edges = []
    
    def add_node(self, node_data: Dict):
        node_id = node_data.get("node_id", hashlib.md5(json.dumps(node_data).encode()).hexdigest())
        node_data["node_id"] = node_id
        self.nodes.append(node_data)
        return node_id
    
    def add_edge(self, source: str, target: str, edge_type: str, 
                 relationship: str, timestamp: str, weight: float = 1.0,
                 properties: Optional[Dict] = None):
        edge_id = f"edge_{source}_{target}_{len(self.edges)}"
        edge = {
            "edge_id": edge_id,
            "source": source,
            "target": target,
            "edge_type": edge_type,
            "relationship": relationship,
            "timestamp": timestamp,
            "weight": weight,
            "properties": properties or {}
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
    
    def to_graphml(self) -> str:
        """Export to GraphML format."""
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<graphml xmlns="http://graphml.graphdrawing.org/xmlns"')
        lines.append('    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
        lines.append('    xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns ')
        lines.append('    http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">')
        lines.append('  <key id="timestamp" for="node" attr.name="timestamp" attr.type="string"/>')
        lines.append('  <key id="type" for="node" attr.name="type" attr.type="string"/>')
        lines.append('  <key id="author" for="node" attr.name="author" attr.type="string"/>')
        lines.append('  <key id="edit_type" for="node" attr.name="edit_type" attr.type="string"/>')
        lines.append('  <key id="confidence" for="node" attr.name="confidence" attr.type="string"/>')
        lines.append('  <key id="relationship" for="edge" attr.name="relationship" attr.type="string"/>')
        lines.append('  <key id="weight" for="edge" attr.name="weight" attr.type="double"/>')
        lines.append('  <graph id="FileEvolution" edgemode="directed">')
        
        for node in self.nodes:
            lines.append('    <node id="' + node["node_id"] + '">')
            lines.append('      <data key="timestamp">' + node.get("timestamp", "") + '</data>')
            lines.append('      <data key="type">' + node.get("node_type", "") + '</data>')
            if node.get("author"):
                lines.append('      <data key="author">' + node["author"] + '</data>')
            if node.get("edit_type"):
                lines.append('      <data key="edit_type">' + node["edit_type"] + '</data>')
            if node.get("evaluation_band"):
                lines.append('      <data key="confidence">' + node["evaluation_band"] + '</data>')
            lines.append('    </node>')
        
        for edge in self.edges:
            lines.append('    <edge id="' + edge["edge_id"] + '" source="' + edge["source"] + '" target="' + edge["target"] + '">')
            lines.append('      <data key="relationship">' + edge.get("relationship", "") + '</data>')
            lines.append('      <data key="weight">' + str(edge.get("weight", 1.0)) + '</data>')
            lines.append('    </edge>')
        
        lines.append('  </graph>')
        lines.append('</graphml>')
        return "\n".join(lines)
    
    def to_gexf(self) -> str:
        """Export to GEXF format for Gephi."""
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">')
        lines.append('  <meta lastmodifieddate="' + datetime.utcnow().isoformat() + '">')
        lines.append('    <creator>File Metadata Extractor</creator>')
        lines.append('    <description>File edit history knowledge graph</description>')
        lines.append('  </meta>')
        lines.append('  <graph mode="dynamic" defaultedgetype="directed">')
        lines.append('    <attributes class="node">')
        lines.append('      <attribute id="timestamp" title="timestamp" type="string"/>')
        lines.append('      <attribute id="type" title="type" type="string"/>')
        lines.append('      <attribute id="edit_type" title="edit_type" type="string"/>')
        lines.append('      <attribute id="confidence" title="confidence" type="string"/>')
        lines.append('    </attributes>')
        lines.append('    <attributes class="edge">')
        lines.append('      <attribute id="relationship" title="relationship" type="string"/>')
        lines.append('      <attribute id="weight" title="weight" type="float"/>')
        lines.append('    </attributes>')
        lines.append('    <nodes>')
        
        for node in self.nodes:
            lines.append('      <node id="' + node["node_id"] + '" label="' + node.get("description", "")[:50] + '">')
            lines.append('        <attvalues>')
            if node.get("timestamp"):
                lines.append('          <attvalue for="timestamp" value="' + node["timestamp"] + '"/>')
            if node.get("node_type"):
                lines.append('          <attvalue for="type" value="' + node["node_type"] + '"/>')
            if node.get("edit_type"):
                lines.append('          <attvalue for="edit_type" value="' + node["edit_type"] + '"/>')
            if node.get("evaluation_band"):
                lines.append('          <attvalue for="confidence" value="' + node["evaluation_band"] + '"/>')
            lines.append('        </attvalues>')
            lines.append('      </node>')
        
        lines.append('    </nodes>')
        lines.append('    <edges>')
        
        for edge in self.edges:
            lines.append('      <edge id="' + edge["edge_id"] + '" source="' + edge["source"] + '" target="' + edge["target"] + '">')
            lines.append('        <attvalues>')
            if edge.get("relationship"):
                lines.append('          <attvalue for="relationship" value="' + edge["relationship"] + '"/>')
            lines.append('          <attvalue for="weight" value="' + str(edge.get("weight", 1.0)) + '"/>')
            lines.append('        </attvalues>')
            lines.append('      </edge>')
        
        lines.append('    </edges>')
        lines.append('  </graph>')
        lines.append('</gexf>')
        return "\n".join(lines)


# ============================================================================
# EXTRACTION PIPELINE (Flow Pipeline Implementation)
# ============================================================================

class FlowPipeline:
    """Implements the structured flow pipeline for file extraction."""
    
    def __init__(self):
        self.stages = [
            self.stage_1_ingestion,
            self.stage_2_multi_model_extraction,
            self.stage_3_version_analysis,
            self.stage_4_knowledge_graph_construction,
            self.stage_5_evaluation_band_assignment,
            self.stage_6_output
        ]
    
    def run(self, file_path: str, output_format: str = "json", 
            git_repo_path: Optional[str] = None) -> FileMetadata:
        """Run the complete flow pipeline."""
        logger.info(f"Starting extraction for: {file_path}")
        
        # Create file metadata container
        file_meta = FileMetadata(file_path)
        
        # Run through all stages
        for stage in self.stages:
            try:
                logger.info(f"Running stage: {stage.__name__}")
                file_meta = stage(file_meta, git_repo_path=git_repo_path)
            except Exception as e:
                logger.error(f"Error in stage {stage.__name__}: {e}")
                file_meta.extraction_results.append({
                    "stage": stage.__name__,
                    "status": "failed",
                    "error": str(e)
                })
                continue
        
        # Generate output
        if output_format == "json":
            output = file_meta.to_dict()
        elif output_format == "graphml":
            output = file_meta.knowledge_graph.to_graphml() if file_meta.knowledge_graph else ""
        elif output_format == "gexf":
            output = file_meta.knowledge_graph.to_gexf() if file_meta.knowledge_graph else ""
        else:
            output = file_meta.to_dict()
        
        logger.info(f"Extraction complete for: {file_path}")
        return file_meta, output
    
    def stage_1_ingestion(self, file_meta: FileMetadata, 
                          git_repo_path: Optional[str] = None) -> FileMetadata:
        """Stage 1: File Ingestion"""
        file_path = file_meta.file_path
        
        # Validate file existence
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Detect file type
        file_meta.file_type = self._detect_file_type(file_path)
        
        # Get file stats
        stat = file_path.stat()
        file_meta.size_bytes = stat.st_size
        file_meta.created_time = datetime.fromtimestamp(stat.st_ctime).isoformat() + "Z"
        file_meta.modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z"
        file_meta.accessed_time = datetime.fromtimestamp(stat.st_atime).isoformat() + "Z"
        
        # Check if in git repo
        if git_repo_path:
            file_meta.git_repo_path = Path(git_repo_path)
        else:
            # Try to find git repo
            file_meta.git_repo_path = self._find_git_repo(file_path)
        
        file_meta.extraction_results.append({
            "stage": "ingestion",
            "status": "success",
            "file_type": file_meta.file_type,
            "size_bytes": file_meta.size_bytes,
            "has_git": file_meta.git_repo_path is not None
        })
        
        logger.info(f"Ingested file: {file_path} (type: {file_meta.file_type}, size: {file_meta.size_bytes} bytes)")
        return file_meta
    
    def _detect_file_type(self, file_path: Path) -> str:
        """Detect file type using extension and magic numbers."""
        import magic
        
        # Try using python-magic first
        try:
            mime = magic.from_file(str(file_path))
            if mime and mime != "application/octet-stream":
                return mime
        except:
            pass
        
        # Fall back to extension
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
            '.ppt': 'application/vnd.ms-powerpoint',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.zip': 'application/zip',
            '.tar': 'application/x-tar',
            '.gz': 'application/gzip',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.csv': 'text/csv',
            '.html': 'text/html',
            '.py': 'text/x-python',
            '.js': 'text/javascript'
        }
        return type_map.get(ext, 'application/octet-stream')
    
    def _find_git_repo(self, file_path: Path) -> Optional[Path]:
        """Find the git repository root for this file."""
        current = file_path.parent
        while current != current.parent:  # Stop at root
            if (current / ".git").is_dir():
                return current
            current = current.parent
        return None
    
    def stage_2_multi_model_extraction(self, file_meta: FileMetadata, 
                                        git_repo_path: Optional[str] = None) -> FileMetadata:
        """Stage 2: Multi-Model Extraction"""
        logger.info("Running multi-model extraction")
        
        # Get all extractors for this file type
        extractors = self._get_extractors(file_meta.file_type)
        
        logger.info(f"Found {len(extractors)} extractors for {file_meta.file_type}")
        
        # Run all extractors
        for extractor_name, extractor_func in extractors:
            try:
                logger.debug(f"Running extractor: {extractor_name}")
                result = extractor_func(file_meta.file_path)
                
                # Add confidence based on extractor type
                confidence = self._get_extractor_confidence(extractor_name)
                
                result["extractor"] = extractor_name
                result["confidence"] = confidence
                result["timestamp"] = datetime.utcnow().isoformat() + "Z"
                
                file_meta.extraction_results.append(result)
                
                # Merge metadata
                if "metadata" in result:
                    file_meta.metadata.update(result["metadata"])
                
                # Set content if not already set
                if "content" in result and not file_meta.content:
                    file_meta.content = result["content"]
                elif "content" in result and file_meta.content:
                    # Append or merge content
                    file_meta.content += "\n\n---\n\n" + result["content"]
                
                logger.debug(f"Extractor {extractor_name} succeeded")
                
            except Exception as e:
                logger.warning(f"Extractor {extractor_name} failed: {e}")
                file_meta.extraction_results.append({
                    "extractor": extractor_name,
                    "status": "failed",
                    "error": str(e),
                    "confidence": EvaluationBand.LOW
                })
        
        logger.info(f"Completed multi-model extraction with {len(file_meta.extraction_results)} results")
        return file_meta
    
    def _get_extractors(self, file_type: str) -> List[Tuple[str, Any]]:
        """Get all applicable extractors for a file type."""
        extractors = []
        
        # Metadata extractors (work on all file types)
        extractors.extend([
            ("filesystem_metadata", self._extract_filesystem_metadata),
            ("file_hashes", self._extract_file_hashes),
            ("magic_numbers", self._extract_magic_numbers),
        ])
        
        # File type specific extractors
        if file_type.startswith("text/"):
            extractors.extend([
                ("text_content", self._extract_text_content),
                ("text_encoding", self._extract_text_encoding),
                ("line_analysis", self._extract_line_analysis),
            ])
        
        elif file_type == "application/pdf":
            extractors.extend([
                ("pdf_metadata_pdfplumber", self._extract_pdf_metadata_pdfplumber),
                ("pdf_text_pdfplumber", self._extract_pdf_text_pdfplumber),
                ("pdf_metadata_pypdf2", self._extract_pdf_metadata_pypdf2),
                ("pdf_text_pypdf2", self._extract_pdf_text_pypdf2),
            ])
        
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            extractors.extend([
                ("word_metadata", self._extract_word_metadata),
                ("word_content", self._extract_word_content),
                ("word_track_changes", self._extract_word_track_changes),
            ])
        
        elif file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            extractors.extend([
                ("excel_metadata", self._extract_excel_metadata),
                ("excel_content", self._extract_excel_content),
            ])
        
        elif file_type.startswith("image/"):
            extractors.extend([
                ("image_metadata_pillow", self._extract_image_metadata_pillow),
                ("image_exif", self._extract_image_exif),
                ("image_ocr_tesseract", self._extract_image_ocr_tesseract),
            ])
        
        elif file_type.startswith("audio/"):
            extractors.extend([
                ("audio_metadata_pydub", self._extract_audio_metadata_pydub),
                ("audio_metadata_mutagen", self._extract_audio_metadata_mutagen),
                ("audio_transcription", self._extract_audio_transcription),
            ])
        
        elif file_type.startswith("video/"):
            extractors.extend([
                ("video_metadata_opencv", self._extract_video_metadata_opencv),
                ("video_audio_extraction", self._extract_video_audio),
                ("video_frames", self._extract_video_frames),
            ])
        
        elif "zip" in file_type or "tar" in file_type or "gzip" in file_type:
            extractors.extend([
                ("archive_listing", self._extract_archive_listing),
                ("archive_metadata", self._extract_archive_metadata),
            ])
        
        # Always add generic extractors
        extractors.extend([
            ("embedded_markers", self._extract_embedded_markers),
        ])
        
        return extractors
    
    def _get_extractor_confidence(self, extractor_name: str) -> str:
        """Get confidence level for an extractor."""
        high_confidence = [
            "filesystem_metadata", "magic_numbers", "pdf_metadata_pypdf2",
            "word_metadata", "excel_metadata", "image_metadata_pillow",
            "word_track_changes", "git_history"
        ]
        
        medium_confidence = [
            "text_content", "pdf_text_pdfplumber", "word_content",
            "excel_content", "image_exif", "embedded_markers"
        ]
        
        if extractor_name in high_confidence:
            return EvaluationBand.HIGH
        elif extractor_name in medium_confidence:
            return EvaluationBand.MEDIUM
        else:
            return EvaluationBand.LOW
    
    # ========================================================================
    # METADATA EXTRACTORS
    # ========================================================================
    
    def _extract_filesystem_metadata(self, file_path: Path) -> Dict:
        """Extract file system metadata."""
        stat = file_path.stat()
        return {
            "metadata": {
                "filesystem": {
                    "size_bytes": stat.st_size,
                    "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat() + "Z",
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
                    "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat() + "Z",
                    "mode": oct(stat.st_mode),
                    "uid": stat.st_uid,
                    "gid": stat.st_gid,
                    "inode": stat.st_ino,
                    "nlink": stat.st_nlink
                }
            }
        }
    
    def _extract_file_hashes(self, file_path: Path) -> Dict:
        """Extract file hashes."""
        import hashlib
        
        def file_hash(file_path: Path, algorithm: str) -> str:
            h = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
            return h.hexdigest()
        
        try:
            md5 = file_hash(file_path, 'md5')
            sha1 = file_hash(file_path, 'sha1')
            sha256 = file_hash(file_path, 'sha256')
        except:
            md5, sha1, sha256 = None, None, None
        
        return {
            "metadata": {
                "hashes": {
                    "md5": md5,
                    "sha1": sha1,
                    "sha256": sha256
                }
            }
        }
    
    def _extract_magic_numbers(self, file_path: Path) -> Dict:
        """Extract magic numbers/file signatures."""
        import magic
        
        try:
            mime = magic.from_file(str(file_path))
            desc = magic.from_file(str(file_path), mime=False)
        except:
            mime, desc = None, None
        
        # Read first few bytes for manual inspection
        try:
            with open(file_path, 'rb') as f:
                header = f.read(32)
            header_hex = header.hex()
            header_ascii = ''.join(chr(b) if 32 <= b < 127 else '.' for b in header)
        except:
            header_hex, header_ascii = None, None
        
        return {
            "metadata": {
                "magic": {
                    "mime_type": mime,
                    "description": desc,
                    "header_hex": header_hex,
                    "header_ascii": header_ascii
                }
            }
        }
    
    # ========================================================================
    # TEXT FILE EXTRACTORS
    # ========================================================================
    
    def _extract_text_content(self, file_path: Path) -> Dict:
        """Extract text content from text files."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            return {
                "content": content,
                "metadata": {
                    "text": {
                        "character_count": len(content),
                        "line_count": content.count('\n') + 1,
                        "word_count": len(content.split()),
                        "encoding": "utf-8"
                    }
                }
            }
        except Exception as e:
            raise Exception(f"Failed to read text file: {e}")
    
    def _extract_text_encoding(self, file_path: Path) -> Dict:
        """Detect text file encoding."""
        import chardet
        
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
            
            result = chardet.detect(raw_data)
            return {
                "metadata": {
                    "encoding": {
                        "detected_encoding": result['encoding'],
                        "confidence": result['confidence'],
                        "language": result.get('language', '')
                    }
                }
            }
        except:
            return {
                "metadata": {
                    "encoding": {
                        "error": "Failed to detect encoding"
                    }
                }
            }
    
    def _extract_line_analysis(self, file_path: Path) -> Dict:
        """Analyze text file line by line."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            line_info = []
            for i, line in enumerate(lines):
                line_info.append({
                    "line_number": i + 1,
                    "length": len(line),
                    "is_empty": line.strip() == '',
                    "content_preview": line[:50] + "..." if len(line) > 50 else line
                })
            
            return {
                "metadata": {
                    "line_analysis": {
                        "total_lines": len(lines),
                        "empty_lines": sum(1 for l in lines if l.strip() == ''),
                        "average_line_length": sum(len(l) for l in lines) / len(lines) if lines else 0,
                        "lines": line_info
                    }
                }
            }
        except Exception as e:
            raise Exception(f"Failed to analyze lines: {e}")
    
    # ========================================================================
    # PDF EXTRACTORS
    # ========================================================================
    
    def _extract_pdf_metadata_pdfplumber(self, file_path: Path) -> Dict:
        """Extract PDF metadata using pdfplumber."""
        try:
            import pdfplumber
            
            with pdfplumber.open(str(file_path)) as pdf:
                metadata = pdf.metadata
                
                return {
                    "metadata": {
                        "pdf_pdfplumber": {
                            "author": metadata.get("author"),
                            "creator": metadata.get("creator"),
                            "producer": metadata.get("producer"),
                            "title": metadata.get("title"),
                            "subject": metadata.get("subject"),
                            "creation_date": metadata.get("creation_date"),
                            "modification_date": metadata.get("modification_date"),
                            "encrypted": metadata.get("encrypted", False)
                        }
                    }
                }
        except ImportError:
            raise Exception("pdfplumber not installed")
        except Exception as e:
            raise Exception(f"pdfplumber error: {e}")
    
    def _extract_pdf_text_pdfplumber(self, file_path: Path) -> Dict:
        """Extract text from PDF using pdfplumber."""
        try:
            import pdfplumber
            
            text = ""
            page_info = []
            
            with pdfplumber.open(str(file_path)) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    text += page_text + "\n\n---\n\n"
                    
                    page_info.append({
                        "page_number": i + 1,
                        "width": page.width,
                        "height": page.height,
                        "character_count": len(page_text) if page_text else 0
                    })
            
            # Check for scanned PDF
            if len(text.strip()) < 80:
                warnings = ["This PDF looks scanned. OCR may not have extracted sufficient text."]
            else:
                warnings = []
            
            return {
                "content": text,
                "metadata": {
                    "pdf_text": {
                        "total_pages": len(page_info),
                        "total_characters": len(text),
                        "pages": page_info,
                        "is_scanned": len(text.strip()) < 80
                    }
                },
                "warnings": warnings
            }
        except ImportError:
            raise Exception("pdfplumber not installed")
        except Exception as e:
            raise Exception(f"pdfplumber text extraction error: {e}")
    
    def _extract_pdf_metadata_pypdf2(self, file_path: Path) -> Dict:
        """Extract PDF metadata using PyPDF2."""
        try:
            from PyPDF2 import PdfReader
            
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                metadata = reader.metadata
                
                return {
                    "metadata": {
                        "pdf_pypdf2": {
                            "author": metadata.get("/Author"),
                            "creator": metadata.get("/Creator"),
                            "producer": metadata.get("/Producer"),
                            "title": metadata.get("/Title"),
                            "subject": metadata.get("/Subject"),
                            "creation_date": metadata.get("/CreationDate"),
                            "modification_date": metadata.get("/ModDate"),
                            "num_pages": len(reader.pages)
                        }
                    }
                }
        except ImportError:
            raise Exception("PyPDF2 not installed")
        except Exception as e:
            raise Exception(f"PyPDF2 error: {e}")
    
    def _extract_pdf_text_pypdf2(self, file_path: Path) -> Dict:
        """Extract text from PDF using PyPDF2."""
        try:
            from PyPDF2 import PdfReader
            
            text = ""
            
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    text += page_text + "\n\n---\n\n"
            
            return {
                "content": text,
                "metadata": {
                    "pdf_text_pypdf2": {
                        "total_pages": len(reader.pages),
                        "total_characters": len(text)
                    }
                }
            }
        except ImportError:
            raise Exception("PyPDF2 not installed")
        except Exception as e:
            raise Exception(f"PyPDF2 text extraction error: {e}")
    
    # ========================================================================
    # WORD DOCUMENT EXTRACTORS
    # ========================================================================
    
    def _extract_word_metadata(self, file_path: Path) -> Dict:
        """Extract Word document metadata."""
        try:
            from docx import Document
            
            doc = Document(str(file_path))
            core_props = doc.core_properties
            
            return {
                "metadata": {
                    "word": {
                        "title": core_props.title,
                        "subject": core_props.subject,
                        "author": core_props.author,
                        "created": core_props.created.isoformat() if core_props.created else None,
                        "modified": core_props.modified.isoformat() if core_props.modified else None,
                        "last_printed": core_props.last_printed.isoformat() if core_props.last_printed else None,
                        "revision": core_props.revision,
                        "version": core_props.version,
                        "categories": core_props.categories,
                        "keywords": core_props.keywords,
                        "language": core_props.language,
                        "content_status": core_props.content_status
                    }
                }
            }
        except ImportError:
            raise Exception("python-docx not installed")
        except Exception as e:
            raise Exception(f"Word metadata extraction error: {e}")
    
    def _extract_word_content(self, file_path: Path) -> Dict:
        """Extract content from Word document."""
        try:
            from docx import Document
            
            doc = Document(str(file_path))
            text = "\n".join([p.text for p in doc.paragraphs])
            
            return {
                "content": text,
                "metadata": {
                    "word_content": {
                        "paragraph_count": len(doc.paragraphs),
                        "table_count": len(doc.tables),
                        "image_count": len([inline for p in doc.paragraphs for inline in p.runs if inline.inline_shapes])
                    }
                }
            }
        except ImportError:
            raise Exception("python-docx not installed")
        except Exception as e:
            raise Exception(f"Word content extraction error: {e}")
    
    def _extract_word_track_changes(self, file_path: Path) -> Dict:
        """Extract track changes from Word document."""
        try:
            from docx import Document
            from docx.enum.text import WD_REVISION_TYPE
            from docx.opc.constants import RELATIONSHIP_TYPE as RT
            
            doc = Document(str(file_path))
            
            # Note: python-docx doesn't directly expose track changes in older versions
            # We need to access the XML directly
            # This is a simplified version - full implementation would parse word/comments.xml
            
            # For now, extract basic document info and note that track changes exist
            # A full implementation would use lxml to parse the XML
            
            has_track_changes = False
            try:
                # Check if document has track changes XML
                for part in doc.part.package.parts:
                    if part.partname.startswith('/word/comments.xml'):
                        has_track_changes = True
                        break
            except:
                pass
            
            # Return metadata about track changes
            return {
                "metadata": {
                    "word_track_changes": {
                        "has_track_changes": has_track_changes,
                        "note": "Full track changes extraction requires XML parsing"
                    }
                }
            }
        except ImportError:
            raise Exception("python-docx not installed")
        except Exception as e:
            raise Exception(f"Word track changes extraction error: {e}")
    
    # ========================================================================
    # EXCEL EXTRACTORS
    # ========================================================================
    
    def _extract_excel_metadata(self, file_path: Path) -> Dict:
        """Extract Excel workbook metadata."""
        try:
            from openpyxl import load_workbook
            
            wb = load_workbook(str(file_path), read_only=True)
            
            return {
                "metadata": {
                    "excel": {
                        "title": wb.properties.title,
                        "subject": wb.properties.subject,
                        "author": wb.properties.creator,
                        "created": wb.properties.created.isoformat() if wb.properties.created else None,
                        "modified": wb.properties.modified.isoformat() if wb.properties.modified else None,
                        "sheet_count": len(wb.sheetnames),
                        "sheet_names": wb.sheetnames
                    }
                }
            }
        except ImportError:
            raise Exception("openpyxl not installed")
        except Exception as e:
            raise Exception(f"Excel metadata extraction error: {e}")
    
    def _extract_excel_content(self, file_path: Path) -> Dict:
        """Extract content from Excel workbook."""
        try:
            from openpyxl import load_workbook
            import json
            
            wb = load_workbook(str(file_path), read_only=True)
            
            sheets_data = {}
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                sheet_data = []
                
                for row in sheet.iter_rows(values_only=True):
                    sheet_data.append([str(cell) if cell is not None else "" for cell in row])
                
                sheets_data[sheet_name] = sheet_data
            
            content = json.dumps(sheets_data, indent=2)
            
            return {
                "content": content,
                "metadata": {
                    "excel_content": {
                        "sheet_count": len(wb.sheetnames),
                        "total_cells": sum(sum(1 for _ in row) for sheet in wb.sheetnames for row in wb[sheet].iter_rows()),
                        "total_rows": sum(sheet.max_row for sheet in wb.sheetnames)
                    }
                }
            }
        except ImportError:
            raise Exception("openpyxl not installed")
        except Exception as e:
            raise Exception(f"Excel content extraction error: {e}")
    
    # ========================================================================
    # IMAGE EXTRACTORS
    # ========================================================================
    
    def _extract_image_metadata_pillow(self, file_path: Path) -> Dict:
        """Extract image metadata using Pillow."""
        try:
            from PIL import Image
            import json
            
            with Image.open(str(file_path)) as img:
                metadata = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": {"width": img.width, "height": img.height},
                    "bits": img.bits if hasattr(img, 'bits') else None,
                    "color_palette": img.palette.tobytes().hex() if hasattr(img, 'palette') and img.palette else None
                }
                
                # Get EXIF-like info
                if hasattr(img, '_getexif'):
                    exif = img._getexif()
                    if exif:
                        metadata["exif_tags"] = {tag: value for tag, value in exif.items()}
                
                return {
                    "metadata": {
                        "image_pillow": metadata
                    }
                }
        except ImportError:
            raise Exception("Pillow not installed")
        except Exception as e:
            raise Exception(f"Pillow metadata extraction error: {e}")
    
    def _extract_image_exif(self, file_path: Path) -> Dict:
        """Extract EXIF metadata from image."""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            with Image.open(str(file_path)) as img:
                exif_data = {}
                
                if hasattr(img, '_getexif'):
                    exif = img._getexif()
                    if exif:
                        for tag, value in exif.items():
                            decoded = TAGS.get(tag, tag)
                            exif_data[decoded] = value
                
                # Parse important EXIF fields
                parsed = {}
                if 'DateTime' in exif_data:
                    parsed['datetime'] = str(exif_data['DateTime'])
                if 'DateTimeOriginal' in exif_data:
                    parsed['datetime_original'] = str(exif_data['DateTimeOriginal'])
                if 'DateTimeDigitized' in exif_data:
                    parsed['datetime_digitized'] = str(exif_data['DateTimeDigitized'])
                if 'CameraMake' in exif_data or 'Make' in exif_data:
                    parsed['make'] = str(exif_data.get('CameraMake', exif_data.get('Make', '')))
                if 'CameraModel' in exif_data or 'Model' in exif_data:
                    parsed['model'] = str(exif_data.get('CameraModel', exif_data.get('Model', '')))
                if 'Orientation' in exif_data:
                    parsed['orientation'] = str(exif_data['Orientation'])
                if 'GPSInfo' in exif_data:
                    parsed['gps'] = str(exif_data['GPSInfo'])
                
                return {
                    "metadata": {
                        "exif": {
                            "raw": exif_data,
                            "parsed": parsed
                        }
                    }
                }
        except ImportError:
            raise Exception("Pillow not installed")
        except Exception as e:
            raise Exception(f"EXIF extraction error: {e}")
    
    def _extract_image_ocr_tesseract(self, file_path: Path) -> Dict:
        """Extract text from image using Tesseract OCR."""
        try:
            import pytesseract
            from PIL import Image
            
            with Image.open(str(file_path)) as img:
                text = pytesseract.image_to_string(img)
            
            return {
                "content": text,
                "metadata": {
                    "ocr": {
                        "engine": "tesseract",
                        "character_count": len(text),
                        "word_count": len(text.split()),
                        "language": "eng"
                    }
                }
            }
        except ImportError:
            raise Exception("pytesseract or Tesseract OCR not installed")
        except Exception as e:
            raise Exception(f"OCR extraction error: {e}")
    
    # ========================================================================
    # EMBEDDED MARKERS EXTRACTOR (For samples4 files)
    # ========================================================================
    
    def _ Extract_embedded_markers(self, file_path: Path) -> Dict: 
```

I need to fix a typo in the function name. Let me continue with the version history extraction and complete the code. Let me create a separate file for the version history and knowledge graph components.