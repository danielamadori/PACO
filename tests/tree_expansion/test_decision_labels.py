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

FIXTURE_PATH = Path(__file__).parent / "data" / "root_snapshot.json"


def load_snapshot() -> dict:
    with FIXTURE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_root_snapshot_active_labels() -> None:
    """The root snapshot from the notebook should expose C1 and N1 as active."""

    snapshot = load_snapshot()
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


def test_all_pending_results_in_no_active_labels() -> None:
    """If every decision is pending we should not return any active label."""

    snapshot = {
        "pending_choices": ["C1", "C2"],
        "pending_natures": ["N1"],
    }

    assert get_active_decision_labels(snapshot) == set()
    assert get_pending_decision_labels(snapshot) == {"C1", "C2", "N1"}
