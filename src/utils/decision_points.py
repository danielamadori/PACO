"""Utilities for classifying decision points within execution snapshots."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, Optional, Set, Tuple

__all__ = [
    "get_active_decision_labels",
    "get_pending_decision_labels",
]

_PENDING_STATES = {
    "pending",
    "inactive",
    "waiting",
    "blocked",
    "disabled",
    "suspended",
    "paused",
}

_ACTIVE_STATES = {
    "active",
    "enabled",
    "ready",
    "current",
    "available",
    "running",
    "open",
    "selected",
}


def _normalize_label(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return str(value)


def _extract_status(entry: Dict[str, Any]) -> Any:
    for key in ("status", "state", "active", "is_active", "enabled"):
        if key in entry:
            return entry[key]
    return None


def _iter_labels(data: Any) -> Iterator[Tuple[str, Optional[Any]]]:
    if isinstance(data, dict):
        for label, entry in data.items():
            normalized_label = _normalize_label(label)
            if not normalized_label:
                continue
            if isinstance(entry, dict):
                yield normalized_label, _extract_status(entry)
            else:
                yield normalized_label, None
    elif isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict):
                label = (
                    entry.get("label")
                    or entry.get("name")
                    or entry.get("id")
                )
                normalized_label = _normalize_label(label)
                if not normalized_label:
                    continue
                yield normalized_label, _extract_status(entry)
            else:
                normalized_label = _normalize_label(entry)
                if normalized_label:
                    yield normalized_label, None
    else:
        normalized_label = _normalize_label(data)
        if normalized_label:
            yield normalized_label, None


def _collect_labels(data: Any) -> Set[str]:
    labels: Set[str] = set()
    if isinstance(data, dict):
        for label in data.keys():
            normalized = _normalize_label(label)
            if normalized:
                labels.add(normalized)
    elif isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict):
                normalized = _normalize_label(
                    entry.get("label")
                    or entry.get("name")
                    or entry.get("id")
                )
            else:
                normalized = _normalize_label(entry)
            if normalized:
                labels.add(normalized)
    else:
        normalized = _normalize_label(data)
        if normalized:
            labels.add(normalized)
    return labels


def _status_is_active(status: Any) -> bool:
    if isinstance(status, bool):
        return status
    if status is None:
        return False
    if isinstance(status, (int, float)):
        return status != 0
    if isinstance(status, str):
        normalized = status.strip().lower()
        if not normalized:
            return False
        if normalized in _PENDING_STATES:
            return False
        if normalized in _ACTIVE_STATES:
            return True
        # Treat truthy strings (e.g. "yes") as active and the rest as inactive.
        if normalized in {"true", "yes", "y", "1"}:
            return True
        if normalized in {"false", "no", "n", "0"}:
            return False
    return bool(status)


def _classify_decision_labels(snapshot: Dict[str, Any]) -> Tuple[Set[str], Set[str], Set[str]]:
    active: Set[str] = set()
    pending: Set[str] = set()
    observed: Set[str] = set()

    def process(
        data: Any,
        *,
        default_active: bool = False,
        default_pending: bool = False,
    ) -> None:
        if data is None:
            return
        labels = _collect_labels(data)
        if labels:
            observed.update(labels)
        for label, status in _iter_labels(data):
            if status is None:
                if default_active:
                    active.add(label)
                elif default_pending:
                    pending.add(label)
                continue
            if _status_is_active(status):
                active.add(label)
            else:
                pending.add(label)

    # Primary descriptors coming from the snapshot or node state.
    process(snapshot.get("decision_points"))
    process(snapshot.get("stop_transitions"))
    process(snapshot.get("active_decision_points"), default_active=True)

    # Choice/Nature lists signal availability of decision points.
    process(snapshot.get("choices"), default_active=True)
    process(snapshot.get("natures"), default_active=True)
    process(snapshot.get("active_choices"), default_active=True)
    process(snapshot.get("active_natures"), default_active=True)

    # Pending/waiting descriptors explicitly mark decisions that should be excluded.
    process(snapshot.get("pending_decision_points"), default_pending=True)
    process(snapshot.get("pending_choices"), default_pending=True)
    process(snapshot.get("pending_natures"), default_pending=True)
    process(snapshot.get("waiting_choices"), default_pending=True)
    process(snapshot.get("waiting_natures"), default_pending=True)
    process(snapshot.get("blocked_choices"), default_pending=True)
    process(snapshot.get("blocked_natures"), default_pending=True)

    return active, pending, observed


def get_active_decision_labels(snapshot: Dict[str, Any]) -> Set[str]:
    """Return the labels of decision points that are currently active."""

    active, pending, observed = _classify_decision_labels(snapshot or {})
    if active:
        # Pending markers should always win over active hints so that
        # conflicting metadata (e.g. an "active" list that still contains a
        # pending decision) does not leak inactive choices.
        active = active - pending
        if active:
            return active
    if observed:
        if pending:
            return observed - pending
        return observed
    return set()


def get_pending_decision_labels(snapshot: Dict[str, Any]) -> Set[str]:
    """Return the labels of decision points that are marked as pending."""

    _, pending, _ = _classify_decision_labels(snapshot or {})
    return pending


def extract_transition_ids(entries: Iterable[Any]) -> Set[str]:
    """Collect transition identifiers from heterogeneous structures."""

    result: Set[str] = set()
    for entry in entries or []:
        if isinstance(entry, dict):
            candidate = (
                entry.get("id")
                or entry.get("transition")
                or entry.get("value")
            )
        else:
            candidate = entry
        normalized = _normalize_label(candidate)
        if normalized:
            result.add(normalized)
    return result
