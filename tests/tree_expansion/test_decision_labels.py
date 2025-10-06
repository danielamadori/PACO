"""Tests for the decision point helpers used in the tree expansion notebook."""


import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.utils.decision_points import (
    get_active_decision_labels,
    get_pending_decision_labels,
)

FIXTURE_DIR = Path(__file__).parent / "data"


def load_snapshot(name: str) -> dict:
    path = FIXTURE_DIR / name
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_root_snapshot_has_no_active_decisions() -> None:
    """The initial snapshot should only report pending decisions."""

    snapshot = load_snapshot("root_snapshot.json")
    assert get_active_decision_labels(snapshot) == set()
    assert get_pending_decision_labels(snapshot) == {"C1", "C2", "N1"}


def test_first_decision_snapshot_exposes_c1_and_n1() -> None:
    """After the deterministic prefix only C1 and N1 should be enabled."""

    snapshot = load_snapshot("first_decision_snapshot.json")
    assert get_active_decision_labels(snapshot) == {"C1", "N1"}
    assert get_pending_decision_labels(snapshot) == {"C2"}


def test_labels_without_statuses_use_pending_information() -> None:
    """Pending markers should exclude inactive decisions when statuses are missing."""

    snapshot = {
        "decision_points": {
            "C1": {"transitions": ["35", "30"]},
            "N1": {"transitions": ["20", "15"]},
            "C2": {"transitions": ["47", "42"]},
        },
        "pending_choices": ["C2"],
    }

    assert get_active_decision_labels(snapshot) == {"C1", "N1"}
    assert get_pending_decision_labels(snapshot) == {"C2"}


def test_pending_labels_override_active_hints() -> None:
    """Explicit pending flags should override conflicting active lists."""

    snapshot = {
        "active_decision_points": ["C1", "C2"],
        "pending_choices": ["C2"],
        "stop_transitions": {
            "C1": ["35", "30"],
            "C2": ["47", "42"],
        },
    }

    assert get_active_decision_labels(snapshot) == {"C1"}
    assert get_pending_decision_labels(snapshot) == {"C2"}


def test_all_pending_results_in_no_active_labels() -> None:
    """If every decision is pending we should not return any active label."""

    snapshot = {
        "pending_choices": ["C1", "C2"],
        "pending_natures": ["N1"],
    }

    assert get_active_decision_labels(snapshot) == set()
    assert get_pending_decision_labels(snapshot) == {"C1", "C2", "N1"}
