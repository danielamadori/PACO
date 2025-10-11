import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def _load_tree_expansion_env() -> Dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    notebook_path = root / "tree_expansion.ipynb"
    with notebook_path.open() as handle:
        notebook = json.load(handle)

    env: Dict[str, Any] = {
        "Any": Any,
        "Dict": Dict,
        "List": List,
        "Optional": Optional,
    }

    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if "def _collect_transition_ids" in source:
            exec(source, env, env)
            break

    return env


def test_stop_groups_use_active_markings_filtering():
    env = _load_tree_expansion_env()
    get_stop_groups_from_status = env["get_stop_groups_from_status"]

    status = {
        "C1": {"choices": [{"id": "t1"}, {"id": "t2"}]},
        "N1": {"options": [{"transition_id": "t3"}]},
        "state": "RUNNING",
    }
    active_markings = {"C1": [{"place": "p1"}]}

    assert get_stop_groups_from_status(status, active_markings=active_markings) == {
        "C1": ["t1", "t2"],
    }


def test_stop_groups_from_status_handles_decision_lists():
    env = _load_tree_expansion_env()
    get_stop_groups_from_status = env["get_stop_groups_from_status"]

    status = {
        "decisions": [
            {
                "label": "C2",
                "choices": [
                    {"transition": {"id": "t5"}},
                    {"transition": {"id": "t6"}},
                ],
            },
            {
                "label": "N2",
                "transitions": ["t7", {"id": "t8"}],
            },
        ],
        "active_markings": [
            {"label": "C2"},
            {"label": "N2"},
        ],
    }

    result = get_stop_groups_from_status(status, active_markings=status["active_markings"])

    assert result == {
        "C2": ["t5", "t6"],
        "N2": ["t7", "t8"],
    }


def test_stop_groups_without_active_markings_returns_all():
    env = _load_tree_expansion_env()
    get_stop_groups_from_status = env["get_stop_groups_from_status"]

    status = {
        "enabled": {
            "C3": [{"id": "t9"}, {"id": "t10"}],
        }
    }

    assert get_stop_groups_from_status(status) == {"C3": ["t9", "t10"]}
