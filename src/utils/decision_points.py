"""Utilities for classifying decision points within execution snapshots."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple

__all__ = [
    "get_active_decision_labels",
    "get_pending_decision_labels",
    "resolve_active_stop_transitions",
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
    # Pending markers should always win over active hints so that conflicting
    # metadata (e.g. an "active" list that still contains a pending decision)
    # does not leak inactive choices.
    active = active - pending
    if active:
        return active
    if observed:
        remaining = observed - pending
        if remaining:
            return remaining
        if not pending:
            return observed
    return set()


def get_pending_decision_labels(snapshot: Dict[str, Any]) -> Set[str]:
    """Return the labels of decision points that are marked as pending."""

    _, pending, _ = _classify_decision_labels(snapshot or {})
    return pending


def _normalize_transition_ids(values: Iterable[Any]) -> List[str]:
    """Normalize heterogeneous transition descriptors into ordered identifiers."""

    result: List[str] = []
    seen: Set[str] = set()

    for value in values or []:
        if isinstance(value, dict):
            candidate = (
                value.get("id")
                or value.get("transition")
                or value.get("value")
            )
        else:
            candidate = value
        normalized = _normalize_label(candidate)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)

    return result


def _get_enabled_stop_transitions(
    petri_net: Dict[str, Any],
    marking: Dict[str, Any],
) -> Dict[str, List[str]]:
    """Compute the stop transitions that are enabled for the provided marking."""

    transitions = (petri_net or {}).get("transitions", [])
    enabled: Dict[str, List[str]] = {}

    for transition in transitions:
        if not isinstance(transition, dict):
            continue
        if not transition.get("stop"):
            continue

        trans_id = _normalize_label(transition.get("id"))
        label = _normalize_label(transition.get("label") or transition.get("name"))
        if not trans_id or not label:
            continue

        inputs = transition.get("inputs", [])
        is_enabled = True
        for place in inputs:
            place_id = _normalize_label(place)
            if not place_id:
                continue
            place_state = marking.get(place_id, {})
            if isinstance(place_state, dict):
                tokens = place_state.get("token", 0)
            elif isinstance(place_state, (int, float)):
                tokens = place_state
            else:
                tokens = 0
            if tokens <= 0:
                is_enabled = False
                break

        if is_enabled:
            enabled.setdefault(label, []).append(trans_id)

    return enabled


def resolve_active_stop_transitions(
    snapshot: Dict[str, Any],
    petri_net: Dict[str, Any],
    *,
    decision_points: Optional[Any] = None,
) -> Dict[str, List[str]]:
    """Resolve active stop transitions by combining hints and Petri net state."""

    snapshot = snapshot or {}
    active_labels = get_active_decision_labels(snapshot)
    pending_labels = get_pending_decision_labels(snapshot)
    marking = snapshot.get("marking") or {}

    enabled_stop: Optional[Dict[str, List[str]]] = None
    if petri_net and marking:
        enabled_stop = _get_enabled_stop_transitions(petri_net, marking)

    active: Dict[str, List[str]] = {}
    raw_candidates: Optional[Any] = None

    for source in (
        snapshot.get("stop_transitions"),
        snapshot.get("decision_points"),
        decision_points,
    ):
        if isinstance(source, (dict, list)):
            raw_candidates = source
            break

    def assign(label: str, transitions: Any) -> None:
        normalized_label = _normalize_label(label)
        if not normalized_label:
            return

        candidates = (
            transitions if isinstance(transitions, list) else [transitions]
        )
        normalized_ids = _normalize_transition_ids(candidates)

        if enabled_stop is not None:
            allowed = enabled_stop.get(normalized_label, [])
            if not allowed:
                return
            if normalized_ids:
                normalized_ids = [t for t in normalized_ids if t in allowed]
            if not normalized_ids:
                normalized_ids = allowed

        if not normalized_ids:
            return
        if active_labels and normalized_label not in active_labels:
            return
        if (
            pending_labels
            and normalized_label in pending_labels
            and normalized_label not in active_labels
        ):
            return

        active[normalized_label] = normalized_ids

    if isinstance(raw_candidates, dict):
        for label, entry in raw_candidates.items():
            if isinstance(entry, dict):
                transitions = (
                    entry.get("transitions")
                    or entry.get("ids")
                    or entry.get("alternatives")
                    or []
                )
            else:
                transitions = entry
            assign(label, transitions)
    elif isinstance(raw_candidates, list):
        for entry in raw_candidates:
            if isinstance(entry, dict):
                label = (
                    entry.get("label")
                    or entry.get("name")
                    or entry.get("id")
                )
                transitions = (
                    entry.get("transitions")
                    or entry.get("ids")
                    or entry.get("alternatives")
                    or []
                )
                if label is not None:
                    assign(label, transitions)
            else:
                assign(entry, [])

    if active:
        return active

    if enabled_stop is None:
        enabled_stop = _get_enabled_stop_transitions(petri_net or {}, marking)

    enabled_stop = enabled_stop or {}

    if active_labels:
        enabled_stop = {
            label: ids for label, ids in enabled_stop.items() if label in active_labels
        }
    elif pending_labels:
        enabled_stop = {
            label: ids
            for label, ids in enabled_stop.items()
            if label not in pending_labels
        }

    return enabled_stop


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
