"""Tests for resolving active stop transitions during tree expansion."""

from src.utils.decision_points import resolve_active_stop_transitions


PETRI_NET = {
    "transitions": [
        {"id": "35", "label": "C1", "stop": True, "inputs": ["p_c1"]},
        {"id": "30", "label": "C1", "stop": True, "inputs": ["p_c1"]},
        {"id": "20", "label": "N1", "stop": True, "inputs": ["p_n1"]},
        {"id": "15", "label": "N1", "stop": True, "inputs": ["p_n1"]},
        {"id": "47", "label": "C2", "stop": True, "inputs": ["p_c2"]},
        {"id": "42", "label": "C2", "stop": True, "inputs": ["p_c2"]},
    ]
}


ROOT_SNAPSHOT = {
    "marking": {
        "p_c1": {"token": 0},
        "p_n1": {"token": 0},
        "p_c2": {"token": 0},
    },
    "stop_transitions": {
        "C1": ["35", "30"],
        "N1": ["20", "15"],
        "C2": ["47", "42"],
    },
}


FIRST_DECISION_SNAPSHOT = {
    "marking": {
        "p_c1": {"token": 1},
        "p_n1": {"token": 1},
        "p_c2": {"token": 0},
    },
    "stop_transitions": {
        "C1": ["35", "30"],
        "N1": ["20", "15"],
        "C2": ["47", "42"],
    },
    "pending_choices": ["C2"],
}


def test_root_snapshot_has_no_enabled_stop_transitions() -> None:
    """The deterministic prefix should not expose any enabled stop transitions."""

    result = resolve_active_stop_transitions(ROOT_SNAPSHOT, PETRI_NET)
    assert result == {}


def test_first_decision_snapshot_exposes_c1_and_n1() -> None:
    """Once the prefix is consumed only C1 and N1 should be enabled."""

    result = resolve_active_stop_transitions(FIRST_DECISION_SNAPSHOT, PETRI_NET)
    assert result == {
        "C1": ["35", "30"],
        "N1": ["20", "15"],
    }
