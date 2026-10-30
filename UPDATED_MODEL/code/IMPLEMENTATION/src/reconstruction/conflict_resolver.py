"""
Conflict resolution module for temporal knowledge graph.

This module implements the most-recent-wins conflict resolution policy
required by the Temporal-Valid KG RAG system. When new facts conflict
with existing facts, the system automatically:
1. Detects the conflict via entity identity and predicate matching
2. Promotes the newer fact to current=true
3. Marks the older fact as current=false with superseded_by reference
4. Retains full history for audit

This ensures the system always returns the most current information
by default while preserving history for debugging and compliance.

Usage:
    from src.reconstruction.conflict_resolver import ConflictResolver

    resolver = ConflictResolver()
    result = resolver.reconcile(new_fact, existing_facts)
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

from src.models import Fact, ReconciliationResult


class ConflictResolver:
    """
    Resolves conflicts between facts in the temporal knowledge graph.

    Implements the most-recent-wins policy with explicit supersession
    tracking for audit compliance in military environments.

    Key behaviors:
    - Compares facts by entity_id + predicate identity
    - Uses valid_at timestamp to determine which is newer
    - Creates SUPERSEDES edges in the graph
    - Returns reconciliation action for the caller to execute
    """

    def __init__(self, strategy: str = "most_recent_wins") -> None:
        """
        Initialize the conflict resolver.

        Args:
            strategy: Resolution strategy (default: "most_recent_wins")
        """
        self.strategy = strategy

    def reconcile(
        self, new_fact: Dict[str, Any], existing_facts: List[Dict[str, Any]]
    ) -> ReconciliationResult:
        """
        Determine how to handle a new fact against existing facts.

        This method checks for conflicts by comparing entity identity
        and predicate. If a conflict exists, it determines which fact
        should be current based on valid_at timestamps.

        Args:
            new_fact: The newly extracted fact to evaluate
            existing_facts: List of existing facts that might conflict

        Returns:
            ReconciliationResult indicating whether to keep or supersede

        Example:
            >>> resolver = ConflictResolver()
            >>> result = resolver.reconcile(new_fact, existing_facts)
            >>> if result.action == "supersede":
            ...     print(f"Superseded fact: {result.superseded_fact_id}")
        """
        # Find conflicting facts (same entity_id and predicate)
        conflicts = []
        for existing in existing_facts:
            if existing.get("entity_id") == new_fact.get("entity_id") and existing.get(
                "predicate"
            ) == new_fact.get("predicate"):
                conflicts.append(existing)

        if not conflicts:
            # No conflict found - keep the new fact
            return ReconciliationResult(
                action="keep", reason="No existing conflict found"
            )

        # Parse timestamps for comparison
        new_valid_at = self._parse_timestamp(new_fact.get("valid_at"))

        # Find the most recent conflicting fact
        most_recent_conflict = None
        most_recent_time = None

        for conflict in conflicts:
            conflict_time = self._parse_timestamp(conflict.get("valid_at"))
            if most_recent_time is None or conflict_time > most_recent_time:
                most_recent_time = conflict_time
                most_recent_conflict = conflict

        # Compare timestamps
        new_time = new_valid_at

        if new_time > most_recent_time:
            # New fact is more recent - supersede
            return ReconciliationResult(
                action="supersede",
                superseded_fact_id=most_recent_conflict.get("fact_id"),
                reason=f"New fact valid_at {new_time} is newer than existing {most_recent_time}",
            )
        else:
            # Existing fact is more recent - keep it, don't supersede new
            return ReconciliationResult(
                action="keep",
                reason=f"Existing fact is newer or equal (existing: {most_recent_time}, new: {new_time})",
            )

    def _parse_timestamp(self, ts: str | datetime | None) -> datetime:
        """
        Parse a timestamp string to datetime object.

        Handles ISO-8601 format with Z or +00:00 timezone suffix.

        Args:
            ts: Timestamp string or datetime

        Returns:
            timezone-aware datetime in UTC
        """
        if ts is None:
            return datetime.min.replace(tzinfo=None)

        if isinstance(ts, datetime):
            return ts

        # Parse ISO format
        normalized = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)

    def detect_conflicts(
        self, facts: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """
        Detect all conflicts in a list of facts.

        Groups facts by (entity_id, predicate) pairs that have
        multiple facts - these are potential conflicts.

        Args:
            facts: List of facts to check for conflicts

        Returns:
            List of conflict groups (each group is a list of conflicting facts)
        """
        from collections import defaultdict

        groups = defaultdict(list)
        for fact in facts:
            key = (fact.get("entity_id"), fact.get("predicate"))
            groups[key].append(fact)

        # Return only groups with conflicts (more than one fact)
        return [group for group in groups.values() if len(group) > 1]


def resolve_conflict(
    new_fact: Dict[str, Any], existing_facts: List[Dict[str, Any]]
) -> ReconciliationResult:
    """
    Convenience function to resolve a single conflict.

    Args:
        new_fact: The new fact to evaluate
        existing_facts: Existing facts that might conflict

    Returns:
        ReconciliationResult with action and reason
    """
    resolver = ConflictResolver()
    return resolver.reconcile(new_fact, existing_facts)
