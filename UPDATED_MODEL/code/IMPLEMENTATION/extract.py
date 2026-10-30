
#!/usr/bin/env python3
"""
Universal File Metadata & Version History Extractor
Extracts edit history from files and builds knowledge graphs.

Usage:
    python extract.py <file_path> [options]
"""

import os
import sys
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import argparse


# ============================================================================
# DATA CLASSES
# ============================================================================

class EditNode:
    """Represents a single edit/change to a file."""
    
    def __init__(self, edit_id: str, timestamp: str, author: Optional[str],
                 edit_type: str, content_before: Optional[str] = None,
                 content_after: Optional[str] = None,
                 affected_sections: Optional[List[str]] = None,
                 description: str = "", file_version: str = "1.0",
                 source: str = "unknown", confidence: str = "medium"):
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
            "evaluation_band": self.confidence
        }


class KnowledgeGraph:
    """Directed graph representing file evolution."""
    
    def __init__(self):
        self.nodes: List[Dict] = []
        self.edges: List[Dict] = []
    
    def add_node(self, node_data: Dict) -> str:
        """Add a node to the graph."""
        node_id = node_data.get("node_id", hashlib.md5(json.dumps(node_data).encode()).hexdigest())
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
    
    def extract(self, file_path: Path) -> List[EditNode]:
        """Main extraction method - tries all available sources."""
        edits = []
        
        # Try each extraction method
        for extractor in [
            self._extract_from_embedded_markers,
            self._extract_from_filesystem,
        ]:
            try:
                result = extractor(file_path)
                if result:
                    edits.extend(result)
                    # If we got results from a good source, stop
                    if edits and edits[0].source in ["embedded_marker"]:
                        break
            except Exception as e:
                print(f"Warning: {extractor.__name__} failed: {e}", file=sys.stderr)
                continue
        
        # Sort by timestamp
        edits.sort(key=lambda x: x.timestamp)
        
        # Assign sequential versions
        for i, edit in enumerate(edits):
            edit.file_version = f"{i + 1}.0"
        
        return edits
    
    def _extract_from_embedded_markers(self, file_path: Path) -> List[EditNode]:
        """Extract edit history from embedded HTML-style markers."""
        edits = []
        
        # Only process text-based files
        if not file_path.name.endswith(('.txt', '.md', '.csv', '.json', '.xml', '.html', '.py', '.js')):
            return edits
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            print(f"Cannot read file {file_path}: {e}", file=sys.stderr)
            return edits
        
        # Pattern: <!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: add | SECTION: header -->
        pattern = r'<!--\s*EDIT:\s*([^|]+)\s*\|\s*AUTHOR:\s*([^|]+)\s*\|\s*TYPE:\s*([^|]+)'
        
        for i, match in enumerate(re.finditer(pattern, content)):
            timestamp = match.group(1).strip()
            author = match.group(2).strip()
            edit_type = match.group(3).strip().lower()
            
            # Get content after this marker
            content_start = match.end()
            next_match = next((m for m in re.finditer(pattern, content[content_start:])), None)
            
            if next_match:
                content_end = content_start + next_match.start()
            else:
                content_end = len(content)
            
            content_after = content[content_start:content_end].strip()
            
            # For delete operations, the marker indicates removal
            content_before = None
            if edit_type == "delete":
                # Look for content before the marker (previous edit's content)
                prev_matches = list(re.finditer(pattern, content[:content_start]))
                if prev_matches:
                    prev_match = prev_matches[-1]
                    content_before = content[prev_match.end():content_start].strip()
            
            edit_id = f"edit_{timestamp.replace(':', '').replace('-', '').replace('T', '').replace('Z', '')}_{i}"
            
            edit = EditNode(
                edit_id=edit_id,
                timestamp=timestamp,
                author=author if author.lower() != "none" else None,
                edit_type=edit_type,
                content_before=content_before,
                content_after=content_after if edit_type != "delete" else None,
                source="embedded_marker",
                confidence="high"
            )
            edits.append(edit)
        
        return edits
    
    def _extract_from_filesystem(self, file_path: Path) -> List[EditNode]:
        """Fallback: use file system metadata."""
        try:
            stat = file_path.stat()
            timestamp = datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z"
            
            edit_id = f"fs_{file_path.name}"
            
            # Try to get content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except:
                content = f"[Binary file: {file_path.name}]"
            
            edit = EditNode(
                edit_id=edit_id,
                timestamp=timestamp,
                author=None,
                edit_type="create",
                content_after=content[:500] + "..." if len(content) > 500 else content,
                source="filesystem",
                confidence="low"
            )
            return [edit]
        except Exception as e:
            print(f"Filesystem extraction failed: {e}", file=sys.stderr)
            return []


# ============================================================================
# METADATA EXTRACTOR
# ============================================================================

class MetadataExtractor:
    """Extracts basic metadata from files."""
    
    def extract(self, file_path: Path) -> Dict:
        """Extract metadata from a file."""
        import os
        
        stat = file_path.stat()
        
        metadata = {
            "filesystem": {
                "size_bytes": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat() + "Z",
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
                "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat() + "Z",
            }
        }
        
        # Try to get file type
        import mimetypes
        mime_type, encoding = mimetypes.guess_type(str(file_path))
        metadata["file_type"] = mime_type or "unknown"
        
        # For text files, try to read content
        if file_path.name.endswith(('.txt', '.md', '.csv', '.json', '.xml', '.html', '.py', '.js')):
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
        
        return metadata


# ============================================================================
# MAIN EXTRACTION FUNCTION
# ============================================================================

def extract_file(file_path: str, git_repo_path: Optional[str] = None,
                 output_format: str = "json") -> Dict[str, Any]:
    """
    Extract all information from a file and build knowledge graph.
    
    Args:
        file_path: Path to the file
        git_repo_path: Optional git repository path
        output_format: Output format (json, graphml, gexf)
    
    Returns:
        Dictionary with extraction results
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Step 1: Extract metadata
    metadata_extractor = MetadataExtractor()
    metadata = metadata_extractor.extract(file_path)
    
    # Step 2: Extract version history
    version_extractor = VersionHistoryExtractor()
    edits = version_extractor.extract(file_path)
    
    # Step 3: Build knowledge graph
    kg = KnowledgeGraph()
    
    # Add edit nodes
    for edit in edits:
        kg.add_node(edit.to_dict())
    
    # Add edges between consecutive edits
    for i in range(len(edits) - 1):
        current = edits[i]
        next_edit = edits[i + 1]
        
        # Determine relationship
        if current.edit_type == "delete" and next_edit.edit_type == "add":
            relationship = "replaces"
        elif current.edit_type in ["add", "create"] and next_edit.edit_type in ["add", "modify"]:
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
    result = {
        "extraction_metadata": {
            "file": str(file_path),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "extractor_version": "1.0.0"
        },
        "file_metadata": metadata,
        "version_history": {
            "edits": [e.to_dict() for e in edits],
            "edit_count": len(edits)
        },
        "knowledge_graph": kg.to_dict(),
        "summary": {
            "total_edits": len(edits),
            "total_nodes": len(kg.nodes),
            "total_edges": len(kg.edges),
            "sources_used": list(set(e.source for e in edits)),
            "confidence_distribution": {
                "high": sum(1 for e in edits if e.confidence == "high"),
                "medium": sum(1 for e in edits if e.confidence == "medium"),
                "low": sum(1 for e in edits if e.confidence == "low")
            }
        }
    }
    
    return result


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Universal File Metadata & Version History Extractor',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('file', help='Path to the file to extract')
    parser.add_argument('--git-repo', help='Path to git repository (optional)')
    parser.add_argument('--output-format', choices=['json', 'graphml', 'gexf'],
                        default='json', help='Output format (default: json)')
    parser.add_argument('--output', '-o', help='Output file path (default: stdout)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        result = extract_file(
            args.file,
            git_repo_path=args.git_repo,
            output_format=args.output_format
        )
        
        # Format output
        if args.output_format == 'json':
            output = json.dumps(result, indent=2, default=str)
        elif args.output_format == 'graphml':
            output = knowledge_graph_to_graphml(result.get('knowledge_graph', {}))
        elif args.output_format == 'gexf':
            output = knowledge_graph_to_gexf(result.get('knowledge_graph', {}))
        else:
            output = json.dumps(result, indent=2, default=str)
        
        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Output written to: {args.output}", file=sys.stderr)
        else:
            print(output)
        
    except Exception as e:
        print(f"Extraction failed: {e}", file=sys.stderr)
        sys.exit(1)


def knowledge_graph_to_graphml(kg: Dict) -> str:
    """Convert knowledge graph to GraphML format."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"',
        '    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        '    xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns',
        '    http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">',
        '  <key id="timestamp" for="node" attr.name="timestamp" attr.type="string"/>',
        '  <key id="author" for="node" attr.name="author" attr.type="string"/>',
        '  <key id="edit_type" for="node" attr.name="edit_type" attr.type="string"/>',
        '  <key id="confidence" for="node" attr.name="confidence" attr.type="string"/>',
        '  <key id="relationship" for="edge" attr.name="relationship" attr.type="string"/>',
        '  <key id="weight" for="edge" attr.name="weight" attr.type="double"/>',
        '  <graph id="FileHistory" edgemode="directed">'
    ]
    
    for node in kg.get('nodes', []):
        node_id = node.get('node_id', 'unknown')
        lines.append(f'    <node id="{node_id}">')
        if node.get('timestamp'):
            lines.append(f'      <data key="timestamp">{node["timestamp"]}</data>')
        if node.get('author'):
            lines.append(f'      <data key="author">{node["author"]}</data>')
        if node.get('edit_type'):
            lines.append(f'      <data key="edit_type">{node["edit_type"]}</data>')
        if node.get('evaluation_band'):
            lines.append(f'      <data key="confidence">{node["evaluation_band"]}</data>')
        lines.append('    </node>')
    
    for edge in kg.get('edges', []):
        lines.append(f'    <edge id="{edge.get("edge_id", "unknown")}" source="{edge.get("source", "unknown")}" target="{edge.get("target", "unknown")}">')
        if edge.get('relationship'):
            lines.append(f'      <data key="relationship">{edge["relationship"]}</data>')
        lines.append(f'      <data key="weight">{edge.get("weight", 1.0)}</data>')
        lines.append('    </edge>')
    
    lines.extend(['  </graph>', '</graphml>'])
    return '\n'.join(lines)


def knowledge_graph_to_gexf(kg: Dict) -> str:
    """Convert knowledge graph to GEXF format (for Gephi)."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">',
        '  <meta lastmodifieddate="' + datetime.utcnow().isoformat() + '">',
        '    <creator>File History Extractor</creator>',
        '    <description>File edit history knowledge graph</description>',
        '  </meta>',
        '  <graph mode="static" defaultedgetype="directed">',
        '    <attributes class="node">',
        '      <attribute id="0" title="timestamp" type="string"/>',
        '      <attribute id="1" title="author" type="string"/>',
        '      <attribute id="2" title="edit_type" type="string"/>',
        '      <attribute id="3" title="confidence" type="string"/>',
        '    </attributes>',
        '    <attributes class="edge">',
        '      <attribute id="0" title="relationship" type="string"/>',
        '      <attribute id="1" title="weight" type="float"/>',
        '    </attributes>',
        '    <nodes>'
    ]
    
    for node in kg.get('nodes', []):
        node_id = node.get('node_id', 'unknown')
        label = node.get('description', node.get('edit_type', 'edit'))[:30]
        lines.append(f'      <node id="{node_id}" label="{label}">')
        lines.append('        <attvalues>')
        if node.get('timestamp'):
            lines.append(f'          <attvalue for="0" value="{node["timestamp"]}"/>')
        if node.get('author'):
            lines.append(f'          <attvalue for="1" value="{node["author"]}"/>')
        if node.get('edit_type'):
            lines.append(f'          <attvalue for="2" value="{node["edit_type"]}"/>')
        if node.get('evaluation_band'):
            lines.append(f'          <attvalue for="3" value="{node["evaluation_band"]}"/>')
        lines.append('        </attvalues>')
        lines.append('      </node>')
    
    lines.append('    </nodes>')
    lines.append('    <edges>')
    
    for edge in kg.get('edges', []):
        lines.append(f'      <edge id="{edge.get("edge_id", "unknown")}" source="{edge.get("source", "unknown")}" target="{edge.get("target", "unknown")}">')
        lines.append('        <attvalues>')
        if edge.get('relationship'):
            lines.append(f'          <attvalue for="0" value="{edge["relationship"]}"/>')
        lines.append(f'          <attvalue for="1" value="{edge.get("weight", 1.0)}"/>')
        lines.append('        </attvalues>')
        lines.append('      </edge>')
    
    lines.extend(['    </edges>', '  </graph>', '</gexf>'])
    return '\n'.join(lines)


if __name__ == "__main__":
    main()
