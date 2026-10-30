"""
Reconstruction module for entity resolution and conflict resolution.

This module handles the transformation of extracted entities and facts
into a coherent knowledge graph with proper entity deduplication
and temporal conflict resolution.

Key components:
- Entity resolution: Merge duplicate entity references across sources
- Conflict resolution: Detect and handle temporal conflicts between facts
"""

from .conflict_resolver import ConflictResolver, resolve_conflict

__all__ = ["ConflictResolver", "resolve_conflict"]
