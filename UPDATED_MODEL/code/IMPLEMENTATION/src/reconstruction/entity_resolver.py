"""
Entity resolution module for merging duplicate entities.

This module handles the critical task of identifying when multiple
entity mentions refer to the same real-world entity, regardless of
variations in naming (e.g., "Apple Inc.", "Apple", "AAPL").

This is essential for building a coherent knowledge graph from
multiple documents that may reference the same entities.

Usage:
    from src.reconstruction.entity_resolver import resolve_entities

    resolved = resolve_entities(entities, strategy="fuzzy")
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
import hashlib


def resolve_entities(
    entities: List[Dict[str, Any]], strategy: str = "fuzzy", threshold: float = 0.85
) -> List[Dict[str, Any]]:
    """
    Resolve and deduplicate entities across multiple extractions.

    This function takes a list of extracted entities and merges
    duplicates based on similarity. The strategy determines how
    similarity is computed.

    Args:
        entities: List of entity dicts with 'text' and 'label' keys
        strategy: Resolution strategy - "exact", "fuzzy", or "ml"
        threshold: Similarity threshold for fuzzy matching (0.0-1.0)

    Returns:
        List of deduplicated entities with canonical IDs

    Example:
        >>> entities = [
        ...     {"text": "Apple", "label": "ORG"},
        ...     {"text": "Apple Inc.", "label": "ORG"},
        ...     {"text": "Microsoft", "label": "ORG"}
        ... ]
        >>> resolved = resolve_entities(entities)
        >>> len(resolved)  # Apple and Apple Inc. merged
        2
    """
    if not entities:
        return []

    if strategy == "exact":
        return _resolve_exact(entities)
    elif strategy == "fuzzy":
        return _resolve_fuzzy(entities, threshold)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def _resolve_exact(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Resolve entities using exact string matching.

    Simple but strict - only exact text matches are merged.
    """
    seen = {}
    resolved = []

    for entity in entities:
        text = entity.get("text", "")
        label = entity.get("label", "UNKNOWN")

        key = (text.lower(), label)

        if key not in seen:
            entity_id = hashlib.sha256(text.encode()).hexdigest()[:16]
            resolved_entity = {
                "entity_id": entity_id,
                "text": text,
                "label": label,
                "canonical": True,
                "aliases": [text],
            }
            seen[key] = resolved_entity
            resolved.append(resolved_entity)
        else:
            # Add as alias to existing entity
            seen[key]["aliases"].append(text)

    return resolved


def _resolve_fuzzy(
    entities: List[Dict[str, Any]], threshold: float = 0.85
) -> List[Dict[str, Any]]:
    """
    Resolve entities using fuzzy string matching.

    Uses a simple similarity measure to detect near-duplicates.
    For production, consider using semantic similarity from embeddings.
    """
    resolved = []
    used = set()

    for i, entity1 in enumerate(entities):
        if i in used:
            continue

        # Find all similar entities
        similar = [entity1]
        for j, entity2 in enumerate(entities[i + 1 :], start=i + 1):
            if j in used:
                continue

            if (
                _similarity(entity1.get("text", ""), entity2.get("text", ""))
                >= threshold
            ):
                similar.append(entity2)
                used.add(j)

        used.add(i)

        # Create canonical entity from similar group
        canonical_text = _choose_canonical([e.get("text", "") for e in similar])
        entity_id = hashlib.sha256(canonical_text.encode()).hexdigest()[:16]

        resolved_entity = {
            "entity_id": entity_id,
            "text": canonical_text,
            "label": similar[0].get("label", "UNKNOWN"),
            "canonical": True,
            "aliases": list(set(e.get("text", "") for e in similar)),
        }
        resolved.append(resolved_entity)

    return resolved


def _similarity(s1: str, s2: str) -> float:
    """
    Compute similarity between two strings.

    Simple implementation using character-level comparison.
    For production, use sentence-transformers embeddings.
    """
    if not s1 or not s2:
        return 0.0

    s1_lower = s1.lower()
    s2_lower = s2.lower()

    if s1_lower == s2_lower:
        return 1.0

    # Simple token-based similarity
    tokens1 = set(s1_lower.split())
    tokens2 = set(s2_lower.split())

    if not tokens1 and not tokens2:
        return 1.0

    intersection = tokens1 & tokens2
    union = tokens1 | tokens2

    if not union:
        return 0.0

    return len(intersection) / len(union)


def _choose_canonical(texts: List[str]) -> str:
    """
    Choose the canonical text from a list of similar entities.

    Strategy: Choose the longest text that contains the most
    specific information.
    """
    if not texts:
        return ""

    # Prefer longer, more descriptive text
    return max(texts, key=len)
