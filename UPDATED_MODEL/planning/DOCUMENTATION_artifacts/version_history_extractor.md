---
format: html
---

# Version History Extractor Module

## Overview
This module extracts **edit history** from files using multiple sources and builds a **knowledge graph** where each node represents a distinct edit.

## File: `version_extractor.py`

```python
#!/usr/bin/env python3
"""
Version History Extractor
Extracts edit history from files and builds knowledge graphs.
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging
import subprocess
import tempfile
import shutil

logger = logging.getLogger(__name__)


class EditNode:
    """Represents a single edit/change to a file."""
    
    def __init__(self, edit_id: str, timestamp: str, author: Optional[str],
                 edit_type: str, content_before: Optional[str],
                 content_after: Optional[str], affected_sections: List[str],
                 description: str, file_version: str, source: str,
                 confidence: str = "medium", commit_hash: Optional[str] = None,
                 line_numbers: Optional[List[int]] = None):
        self.edit_id = edit_id
        self.timestamp = timestamp
        self.author = author
        self.edit_type = edit_type  # create, add, modify, delete, rename
        self.content_before = content_before
        self.content_after = content_after
        self.affected_sections = affected_sections
        self.description = description
        self.file_version = file_version
        self.source = source  # embedded_marker, git, word_track_changes, filesystem
        self.confidence = confidence  # high, medium, low
        self.commit_hash = commit_hash
        self.line_numbers = line_numbers or []
    
    def to_dict(self) -> Dict[str, Any]:
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
            "evaluation_band": self.confidence,
            "commit_hash": self.commit_hash,
            "line_numbers": self.line_numbers
        }
    
    def get_change_summary(self) -> str:
        """Get a short summary of the change."""
        if self.edit_type == "create":
            return f"Created file (v{self.file_version})"
        elif self.edit_type == "add":
            if self.content_after:
                preview = self.content_after[:30] + "..." if len(self.content_after) > 30 else self.content_after
                return f"Added: {preview}"
            return "Added content"
        elif self.edit_type == "delete":
            if self.content_before:
                preview = self.content_before[:30] + "..." if len(self.content_before) > 30 else self.content_before
                return f"Deleted: {preview}"
            return "Deleted content"
        elif self.edit_type == "modify":
            return f"Modified {', '.join(self.affected_sections) if self.affected_sections else 'content'}"
        else:
            return self.description


class VersionAnalyzer:
    """Analyzes files to extract version history from multiple sources."""
    
    def __init__(self):
        self.extraction_order = [
            self._extract_from_embedded_markers,
            self._extract_from_git_history,
            self._extract_from_word_track_changes,
            self._extract_from_filesystem,
        ]
    
    def extract_history(self, file_path: Path, git_repo_path: Optional[Path] = None) -> List[EditNode]:
        """
        Extract version history from a file using all available methods.
        
        Args:
            file_path: Path to the file
            git_repo_path: Optional path to git repository (if different from file's directory)
        
        Returns:
            List of EditNode objects representing the file's edit history
        """
        all_edits = []
        
        # Try each extraction method in order
        for extractor in self.extraction_order:
            try:
                edits = extractor(file_path, git_repo_path)
                if edits:
                    all_edits.extend(edits)
                    logger.info(f"Found {len(edits)} edits from {extractor.__name__}")
                    # If we got edits from a high-confidence source, stop
                    if edits and edits[0].source in ["git", "word_track_changes"]:
                        break
            except Exception as e:
                logger.warning(f"Error in {extractor.__name__}: {e}")
                continue
        
        # Sort edits by timestamp
        all_edits.sort(key=lambda x: x.timestamp)
        
        # Assign file versions if not already assigned
        if all_edits and not all_edits[0].file_version:
            self._assign_file_versions(all_edits)
        
        return all_edits
    
    def _assign_file_versions(self, edits: List[EditNode]):
        """Assign sequential version numbers to edits."""
        for i, edit in enumerate(edits):
            edit.file_version = f"{i + 1}.0"
    
    # ========================================================================
    # EXTRACTION METHOD 1: Embedded Markers
    # ========================================================================
    
    def _extract_from_embedded_markers(self, file_path: Path, 
                                       git_repo_path: Optional[Path] = None) -> List[EditNode]:
        """
        Extract edit history from embedded markers in text files.
        
        Supports two marker formats:
        1. HTML-style: <!-- EDIT: timestamp | AUTHOR: author | TYPE: type -->
        2. YAML-style: # EDIT: ...
        """
        edits = []
        
        # Only works on text files
        if not file_path.name.endswith(('.txt', '.md', '.csv', '.json', '.xml', '.html', '.py', '.js')):
            return edits
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Cannot read file {file_path}: {e}")
            return edits
        
        # Pattern 1: HTML-style comments
        # <!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: user1 | TYPE: add | SECTION: intro -->
        html_pattern = r'<!--\s*EDIT:\s*([^|]+)\s*\|\s*AUTHOR:\s*([^|]+)\s*\|\s*TYPE:\s*([^|]+)\s*(?:\|\s*SECTION:\s*([^|]+))?\s*(?:\|\s*DESCRIPTION:\s*([^|]+))?\s*-->'
        
        # Pattern 2: YAML-style comments
        # # EDIT:
        # #   timestamp: 2024-02-02T20:31:00Z
        # #   author: user1
        # #   type: add
        yaml_pattern = r'#\s*EDIT:\s*\n(?:#\s*[a-z_]+:\s*[^\n]+\n)+'
        
        # First, try HTML-style markers
        html_matches = list(re.finditer(html_pattern, content))
        if html_matches:
            edits = self._parse_html_markers(content, html_matches, file_path)
            return edits
        
        # Try YAML-style markers
        yaml_matches = list(re.finditer(yaml_pattern, content, re.IGNORECASE))
        if yaml_matches:
            edits = self._parse_yaml_markers(content, yaml_matches, file_path)
            return edits
        
        return []
    
    def _parse_html_markers(self, content: str, matches: List, 
                           file_path: Path) -> List[EditNode]:
        """Parse HTML-style embedded markers."""
        edits = []
        
        # Extract all text between markers
        marker_positions = [(m.start(), m.end(), m.groups()) for m in matches]
        
        # Group markers with the content that follows
        for i, (start, end, groups) in enumerate(marker_positions):
            timestamp = groups[0].strip()
            author = groups[1].strip()
            edit_type = groups[2].strip().lower()
            section = groups[3].strip() if groups[3] else None
            description = groups[4].strip() if groups[4] else None
            
            # Get content after this marker until next marker or end
            content_start = end
            if i + 1 < len(marker_positions):
                content_end = marker_positions[i + 1][0]
            else:
                content_end = len(content)
            
            content_after = content[content_start:content_end].strip()
            
            # Check if this is a deletion marker (content before)
            # Look for content before the marker
            if i == 0:
                content_before = None
            else:
                prev_end = marker_positions[i - 1][1]
                content_before = content[prev_end:start].strip()
            
            # Create edit node
            edit_id = f"edit_{timestamp.replace(':', '').replace('-', '').replace('T', '').replace('Z', '')}_{i}"
            
            edit = EditNode(
                edit_id=edit_id,
                timestamp=timestamp,
                author=author if author != "None" else None,
                edit_type=edit_type,
                content_before=content_before if edit_type == "delete" else None,
                content_after=content_after if edit_type != "delete" else None,
                affected_sections=[section] if section else [],
                description=description if description else f"{edit_type} at {timestamp}",
                file_version="",
                source="embedded_marker",
                confidence="high",
                line_numbers=[]
            )
            edits.append(edit)
        
        return edits
    
    def _parse_yaml_markers(self, content: str, matches: List, 
                           file_path: Path) -> List[EditNode]:
        """Parse YAML-style embedded markers."""
        edits = []
        
        for match in matches:
            marker_text = match.group(0)
            
            # Parse YAML-style key-value pairs
            timestamp = None
            author = None
            edit_type = None
            section = None
            description = None
            
            lines = marker_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('# EDIT:'):
                    continue
                if line.startswith('#'):
                    line = line[1:].strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if key in ['timestamp', 'date', 'time']:
                            timestamp = value
                        elif key in ['author', 'user', 'by']:
                            author = value
                        elif key in ['type', 'edit_type', 'action']:
                            edit_type = value.lower()
                        elif key in ['section', 'part', 'location']:
                            section = value
                        elif key in ['description', 'desc', 'note']:
                            description = value
            
            if not timestamp or not edit_type:
                continue
            
            # Get content after marker
            content_start = match.end()
            next_match = next((m for m in matches if m.start() > match.start()), None)
            content_end = next_match.start() if next_match else len(content)
            content_after = content[content_start:content_end].strip()
            
            # For modifications, we might need to look before the marker
            content_before = None
            
            # Create edit node
            edit_id = f"edit_{timestamp.replace(':', '').replace('-', '').replace('T', '').replace('Z', '')}_{len(edits)}"
            
            edit = EditNode(
                edit_id=edit_id,
                timestamp=timestamp,
                author=author if author else None,
                edit_type=edit_type,
                content_before=content_before,
                content_after=content_after,
                affected_sections=[section] if section else [],
                description=description if description else f"{edit_type} at {timestamp}",
                file_version="",
                source="embedded_marker_yaml",
                confidence="high"
            )
            edits.append(edit)
        
        return edits
    
    # ========================================================================
    # EXTRACTION METHOD 2: Git History
    # ========================================================================
    
    def _extract_from_git_history(self, file_path: Path,
                                  git_repo_path: Optional[Path] = None) -> List[EditNode]:
        """
        Extract edit history from git repository.
        
        Uses git log -p to get full patch history for the file.
        """
        edits = []
        
        # Find git repository
        repo_path = git_repo_path
        if not repo_path:
            repo_path = self._find_git_repo(file_path)
        
        if not repo_path:
            return edits
        
        # Get relative path
        try:
            relative_path = str(file_path.relative_to(repo_path))
        except:
            relative_path = str(file_path)
        
        # Use git log to get commit history
        try:
            # Get git log with patch
            cmd = [
                'git', '-C', str(repo_path), 'log',
                '--pretty=format:%H|%an|%aI|%s',
                '-p',
                '--', relative_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = result.stdout
            
            if not output:
                return edits
            
            # Parse git log output
            edits = self._parse_git_log(output, file_path, repo_path)
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"Git log failed: {e}")
        except FileNotFoundError:
            logger.warning("Git not installed or not in PATH")
        
        return edits
    
    def _find_git_repo(self, file_path: Path) -> Optional[Path]:
        """Find the git repository root for a file."""
        current = file_path.parent
        while current != current.parent:
            if (current / ".git").is_dir():
                return current
            current = current.parent
        return None
    
    def _parse_git_log(self, output: str, file_path: Path, 
                      repo_path: Path) -> List[EditNode]:
        """Parse git log -p output into EditNode objects."""
        edits = []
        
        # Split by commit separator
        commits = output.split('\n\ncommit ')
        
        for commit_block in commits:
            if not commit_block.strip():
                continue
            
            lines = commit_block.strip().split('\n')
            
            # First line: commit hash
            if lines[0].startswith('commit '):
                commit_hash = lines[0][7:]
            else:
                commit_hash = "unknown"
            
            # Parse header (after commit hash)
            header_end = 1
            for i, line in enumerate(lines[1:], 1):
                if line.startswith('Author:') or line.startswith('Date:'):
                    continue
                if line and not line.startswith(' ') and not line.startswith('\t'):
                    header_end = i + 1
                    break
                if i > 5:  # Safety
                    header_end = i + 1
                    break
            
            # Extract metadata from header
            author = None
            timestamp = None
            message = ""
            
            for line in lines[1:header_end]:
                if line.startswith('Author: '):
                    author = line[8:].strip()
                elif line.startswith('Date: '):
                    timestamp = line[6:].strip()
                elif line and not line.startswith(' '):
                    message = line
            
            if not timestamp:
                continue
            
            # Parse timestamp (git format: 2024-02-02T20:31:00+00:00)
            timestamp = timestamp.replace('+00:00', 'Z').replace(' ', 'T')
            
            # Extract diff
            diff_start = header_end
            diff_lines = []
            for line in lines[diff_start:]:
                if line.startswith('diff --git'):
                    continue
                if line.startswith('index '):
                    continue
                if line.startswith('@@'):
                    continue
                if line.startswith('++') or line.startswith('--'):
                    continue
                if line.startswith(' '):
                    continue
                # Actual diff lines
                if line.startswith('+') or line.startswith('-'):
                    diff_lines.append(line)
            
            # Parse diff to get added/deleted content
            added_lines = []
            deleted_lines = []
            for line in diff_lines:
                if line.startswith('+'):
                    added_lines.append(line[1:])
                elif line.startswith('-'):
                    deleted_lines.append(line[1:])
            
            content_added = '\n'.join(added_lines) if added_lines else None
            content_deleted = '\n'.join(deleted_lines) if deleted_lines else None
            
            # Determine edit type
            if added_lines and deleted_lines:
                edit_type = "modify"
            elif added_lines:
                edit_type = "add"
            elif deleted_lines:
                edit_type = "delete"
            else:
                edit_type = "modify"  # Metadata-only change
            
            # Create edit node
            edit_id = f"git_{commit_hash[:8]}"
            
            edit = EditNode(
                edit_id=edit_id,
                timestamp=timestamp,
                author=author,
                edit_type=edit_type,
                content_before=content_deleted,
                content_after=content_added,
                affected_sections=[str(file_path.name)],
                description=message,
                file_version="",
                source="git",
                confidence="high",
                commit_hash=commit_hash
            )
            edits.append(edit)
        
        # If no content-based edits found, create one based on commit
        if not edits:
            # Just create a single edit for the file
            edit = EditNode(
                edit_id="git_single",
                timestamp=timestamp,
                author=author,
                edit_type="create",
                content_before=None,
                content_after="File content from git",
                affected_sections=[str(file_path.name)],
                description=message or "Initial commit",
                file_version="1.0",
                source="git",
                confidence="medium",
                commit_hash=commit_hash
            )
            edits.append(edit)
        
        return edits
    
    # ========================================================================
    # EXTRACTION METHOD 3: Word Track Changes
    # ========================================================================
    
    def _extract_from_word_track_changes(self, file_path: Path,
                                         git_repo_path: Optional[Path] = None) -> List[EditNode]:
        """
        Extract edit history from Word document track changes.
        
        Note: This requires parsing Word's XML format directly.
        """
        edits = []
        
        if not file_path.name.endswith('.docx'):
            return edits
        
        try:
            from zipfile import ZipFile
            import xml.etree.ElementTree as ET
            
            # Word documents are ZIP archives
            with ZipFile(str(file_path), 'r') as zip_ref:
                # Check for track changes in document.xml
                if 'word/document.xml' in zip_ref.namelist():
                    with zip_ref.open('word/document.xml') as f:
                        tree = ET.parse(f)
                        root = tree.getroot()
                        
                        # Look for w:ins and w:del elements (insertions and deletions)
                        # Namespace: {http://schemas.openxmlformats.org/wordprocessingml/2006/main}
                        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                        
                        insertions = root.findall('.//w:ins', ns)
                        deletions = root.findall('.//w:del', ns)
                        
                        if insertions or deletions:
                            edits = self._parse_word_xml_insertions_deletions(
                                file_path, insertions, deletions, ns
                            )
                        else:
n                            # Check for comments (revisions)
                            if 'word/comments.xml' in zip_ref.namelist():
                                edits = self._parse_word_comments(zip_ref, file_path)
            
        except ImportError:
            logger.warning("zipfile not available")
        except Exception as e:
            logger.warning(f"Error parsing Word document: {e}")
        
        return edits
    
    def _parse_word_xml_insertions_deletions(self, file_path: Path,
                                              insertions: List, deletions: List,
                                              ns: Dict) -> List[EditNode]:
        """Parse Word XML for insertions and deletions."""
        edits = []
        
        # In Word, insertions and deletions have author and date attributes
        for i, ins in enumerate(insertions):
            author = ins.get('w:author', None)
            date_str = ins.get('w:date', None)
            
            # Parse date (format: 2024-02-02T20:31:00Z)
            timestamp = date_str if date_str else None
            
            # Get inserted text
            text_elements = ins.findall('.//w:t', ns)
            content = ''.join([t.text for t in text_elements if t.text])
            
            edit_id = f"word_ins_{i}"
            edit = EditNode(
                edit_id=edit_id,
                timestamp=timestamp,
                author=author,
                edit_type="add",
                content_before=None,
                content_after=content,
                affected_sections=[],
                description=f"Inserted text: {content[:30]}...",
                file_version="",
                source="word_track_changes",
                confidence="high"
            )
            edits.append(edit)
        
        for i, del_elem in enumerate(deletions):
            author = del_elem.get('w:author', None)
            date_str = del_elem.get('w:date', None)
            timestamp = date_str if date_str else None
            
            # Get deleted text
            text_elements = del_elem.findall('.//w:t', ns)
            content = ''.join([t.text for t in text_elements if t.text])
            
            edit_id = f"word_del_{i}"
            edit = EditNode(
                edit_id=edit_id,
                timestamp=timestamp,
                author=author,
                edit_type="delete",
                content_before=content,
                content_after=None,
                affected_sections=[],
                description=f"Deleted text: {content[:30]}...",
                file_version="",
                source="word_track_changes",
                confidence="high"
            )
            edits.append(edit)
        
        # Sort by timestamp
        edits.sort(key=lambda x: x.timestamp or "")
        
        return edits
    
    def _parse_word_comments(self, zip_ref, file_path: Path) -> List[EditNode]:
        """Parse Word comments.xml for revision history."""
        edits = []
        
        try:
            with zip_ref.open('word/comments.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                
                ns = {'w14': 'http://schemas.microsoft.com/office/word/2010/wordml'}
                
                # Look for comments with revision info
                comments = root.findall('.//w14:comment', ns)
                
                for i, comment in enumerate(comments):
                    author = comment.get('w14:authorId', None)
                    date_str = comment.get('w14:date', None)
                    
                    # Get comment text
                    text = comment.text or ""
                    
                    edit_id = f"word_comment_{i}"
                    edit = EditNode(
                        edit_id=edit_id,
                        timestamp=date_str,
                        author=author,
                        edit_type="modify",
                        content_before=None,
                        content_after=text,
                        affected_sections=[],
                        description=f"Comment: {text[:30]}...",
                        file_version="",
                        source="word_comments",
                        confidence="medium"
                    )
                    edits.append(edit)
        except Exception as e:
            logger.warning(f"Error parsing Word comments: {e}")
        
        return edits
    
    # ========================================================================
    # EXTRACTION METHOD 4: File System Metadata
    # ========================================================================
    
    def _extract_from_filesystem(self, file_path: Path,
                                  git_repo_path: Optional[Path] = None) -> List[EditNode]:
        """
        Extract edit history from file system metadata.
        
        This is a fallback method when no other history is available.
        It creates a single edit with the file's modification time.
        """
        try:
            stat = file_path.stat()
            
            # Use modification time as the edit timestamp
            timestamp = datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z"
            created = datetime.fromtimestamp(stat.st_ctime).isoformat() + "Z"
            
            edit_id = f"fs_{file_path.name}"
            
            # Try to get file content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except:
                content = None
            
            edit = EditNode(
                edit_id=edit_id,
                timestamp=timestamp,
                author=None,  # No author info from filesystem
                edit_type="create",  # Assume creation
                content_before=None,
                content_after=content,
                affected_sections=[str(file_path.name)],
                description=f"File last modified at {timestamp}",
                file_version="1.0",
                source="filesystem",
                confidence="low"  # Low confidence because no actual edit history
            )
            
            return [edit]
            
        except Exception as e:
            logger.warning(f"Error getting filesystem metadata: {e}")
            return []


# ============================================================================
# KNOWLEDGE GRAPH BUILDER
# ============================================================================

class KnowledgeGraphBuilder:
    """Builds a knowledge graph from edit history."""
    
    def __init__(self):
        self.graph = {"nodes": [], "edges": []}
    
    def build(self, edits: List[EditNode]) -> Dict:
        """
        Build a knowledge graph from a list of edits.
        
        Args:
            edits: List of EditNode objects
        
        Returns:
            Dictionary with nodes and edges
        """
        self.graph = {"nodes": [], "edges": []}
        
        if not edits:
            return self.graph
        
        # Add nodes for each edit
        for edit in edits:
            node = edit.to_dict()
            # Add additional graph-specific properties
            node["graph_properties"] = {
                "degree": 0,
                "in_degree": 0,
                "out_degree": 0
            }
            self.graph["nodes"].append(node)
        
        # Add edges between edits
        self._add_temporal_edges(edits)
        self._add_content_edges(edits)
        
        return self.graph
    
    def _add_temporal_edges(self, edits: List[EditNode]):
        """Add edges showing temporal sequence."""
        if len(edits) < 2:
            return
        
        for i in range(len(edits) - 1):
            current = edits[i]
            next_edit = edits[i + 1]
            
            # Determine relationship type
            if current.edit_type == "delete" and next_edit.edit_type == "add":
                relationship = "replaces"
            elif current.edit_type in ["add", "modify"] and next_edit.edit_type in ["add", "modify"]:
                relationship = "successor"
            elif current.edit_type == "create":
                relationship = "adds_to"
            else:
                relationship = "precursor"
            
            # Create edge
            edge = {
                "edge_id": f"edge_{current.edit_id}_{next_edit.edit_id}",
                "source": current.edit_id,
                "target": next_edit.edit_id,
                "edge_type": "temporal",
                "relationship": relationship,
                "timestamp": next_edit.timestamp,
                "weight": 1.0,
                "properties": {
                    "time_diff_seconds": self._calculate_time_diff(current.timestamp, next_edit.timestamp)
                }
            }
            self.graph["edges"].append(edge)
    
    def _calculate_time_diff(self, time1: str, time2: str) -> float:
        """Calculate time difference in seconds between two ISO timestamps."""
        try:
            from datetime import datetime
            dt1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
            dt2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))
            return (dt2 - dt1).total_seconds()
        except:
            return 0.0
    
    def _add_content_edges(self, edits: List[EditNode]):
        """Add edges showing content relationships."""
        # For now, just add edges based on affected sections
        section_map = {}  # section -> list of edit ids
        
        for edit in edits:
            for section in edit.affected_sections:
                if section not in section_map:
                    section_map[section] = []
                section_map[section].append(edit.edit_id)
        
        # Connect edits that affect the same section
        for section, edit_ids in section_map.items():
            for i in range(len(edit_ids) - 1):
                edge = {
                    "edge_id": f"content_edge_{edit_ids[i]}_{edit_ids[i+1]}_{section}",
                    "source": edit_ids[i],
                    "target": edit_ids[i+1],
                    "edge_type": "content",
                    "relationship": "affects_same_section",
                    "section": section,
                    "timestamp": None,
                    "weight": 0.8,
                    "properties": {}
                }
                self.graph["edges"].append(edge)
    
    def get_node_count(self) -> int:
        return len(self.graph["nodes"])
    
    def get_edge_count(self) -> int:
        return len(self.graph["edges"])


# ============================================================================
# EVALUATION BAND ASSIGNER
# ============================================================================

class EvaluationBandAssigner:
    """Assigns confidence bands to extracted data."""
    
    def __init__(self):
        # Define what constitutes high confidence
        self.high_confidence_sources = {
            "git": True,
            "word_track_changes": True,
            "exif": True,
            "pdf_metadata_pypdf2": True,
            "filesystem_metadata": True
        }
        
        self.medium_confidence_sources = {
            "embedded_marker": True,
            "embedded_marker_yaml": True,
            "pdf_metadata_pdfplumber": True,
            "word_metadata": True,
            "excel_metadata": True,
            "image_metadata_pillow": True
        }
        
        self.low_confidence_sources = {
            "filesystem": True,
            "magic_numbers": True
        }
    
    def assign_to_edit(self, edit: EditNode) -> str:
        """Assign evaluation band to an edit."""
        source = edit.source
        
        if source in self.high_confidence_sources:
            return "high"
        elif source in self.medium_confidence_sources:
            return "medium"
        elif source in self.low_confidence_sources:
            return "low"
        else:
            # Unknown source, default to medium if we have good data
            if edit.timestamp and edit.edit_type:
                return "medium"
            return "low"
    
    def assign_to_extraction(self, extraction_result: Dict) -> str:
        """Assign evaluation band to an extraction result."""
        extractor = extraction_result.get("extractor", "")
        success = extraction_result.get("status", "") == "success"
        
        if not success:
            return "low"
        
        if extractor in self.high_confidence_sources:
            return "high"
        elif extractor in self.medium_confidence_sources:
            return "medium"
        else:
            return "medium"  # Default for unknown


# ============================================================================
# MAIN API
# ============================================================================

def extract_version_history(file_path: str, git_repo_path: Optional[str] = None) -> Dict:
    """
    Main function to extract version history from a file.
    
    Args:
        file_path: Path to the file
        git_repo_path: Optional path to git repository
    
    Returns:
        Dictionary containing:
        - edits: List of edit nodes
        - knowledge_graph: Built knowledge graph
        - summary: Extraction summary
    """
    file_path = Path(file_path)
    git_path = Path(git_repo_path) if git_repo_path else None
    
    # Step 1: Extract history
    analyzer = VersionAnalyzer()
    edits = analyzer.extract_history(file_path, git_path)
    
    # Step 2: Assign evaluation bands
    band_assigner = EvaluationBandAssigner()
    for edit in edits:
        edit.confidence = band_assigner.assign_to_edit(edit)
    
    # Step 3: Build knowledge graph
    graph_builder = KnowledgeGraphBuilder()
    knowledge_graph = graph_builder.build(edits)
    
    # Step 4: Create summary
    summary = {
        "file": str(file_path),
        "total_edits": len(edits),
        "total_nodes": knowledge_graph["nodes"],
        "total_edges": knowledge_graph["edges"],
        "sources_used": list(set(e.source for e in edits)),
        "confidence_distribution": {
            "high": sum(1 for e in edits if e.confidence == "high"),
            "medium": sum(1 for e in edits if e.confidence == "medium"),
            "low": sum(1 for e in edits if e.confidence == "low")
        }
    }
    
    return {
        "edits": [e.to_dict() for e in edits],
        "knowledge_graph": knowledge_graph,
        "summary": summary
    }


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python version_extractor.py <file_path> [git_repo_path]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    git_repo = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = extract_version_history(file_path, git_repo)
    
    # Output as JSON
    print(json.dumps(result, indent=2, default=str))
```

## Usage

### Command Line
```bash
# Extract history from a single file
python version_extractor.py samples4/text_files/multi_edit_text.txt

# With git repository
python version_extractor.py samples4_git/evolution.txt samples4_git
```

### Python API
```python
from version_extractor import extract_version_history, EditNode, VersionAnalyzer

# Extract history
result = extract_version_history("path/to/file.txt")

# Access edits
for edit in result["edits"]:
    print(f"{edit['timestamp']}: {edit['edit_type']} by {edit['author']}")

# Access knowledge graph
print(f"Nodes: {result['knowledge_graph']['total_nodes']}")
print(f"Edges: {result['knowledge_graph']['total_edges']}")
```

## Integration with Main Extractor

This module integrates with `extract.py` as follows:

1. **Stage 3: Version Analysis** calls `VersionAnalyzer().extract_history()`
2. **Stage 4: Knowledge Graph Construction** uses `KnowledgeGraphBuilder().build()`
3. **Stage 5: Evaluation Band Assignment** uses `EvaluationBandAssigner()`

The flow pipeline orchestrates these components in the correct order.
