import json
import unittest
from pathlib import Path
from typing import Callable, Dict, List


def _load_helper() -> Callable[[Dict[str, Dict[str, object]], Dict[str, Dict[str, object]]], Dict[str, List[str]]]:
    notebook_path = Path(__file__).resolve().parents[1] / "tree_expansion.ipynb"
    with notebook_path.open() as handle:
        notebook = json.load(handle)

    namespace: Dict[str, object] = {}
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if "def get_active_decision_transition" in source:
            exec(compile(source, str(notebook_path), "exec"), namespace)
            break
    else:
        raise AssertionError("get_active_decision_transition not found in notebook")

    helper = namespace.get("get_active_decision_transition")
    if not callable(helper):
        raise AssertionError("Helper function not loaded correctly")
    return helper  # type: ignore[return-value]


class GetActiveDecisionTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._helper = _load_helper()

    def test_returns_transitions_for_ready_choice(self) -> None:
        petri_net = {
            "places": [
                {"id": "p_choice", "label": "C1", "region_type": "choice", "duration": 0.0},
                {"id": "p_after_a", "label": "A", "region_type": "task"},
                {"id": "p_after_b", "label": "B", "region_type": "task"},
                {"id": "p_guard", "label": "Guard", "region_type": "task"},
            ],
            "transitions": [
                {"id": "t_a", "label": "C1_A", "stop": True, "inputs": ["p_choice"], "outputs": ["p_after_a"]},
                {"id": "t_b", "label": "C1_B", "stop": True, "inputs": ["p_choice", "p_guard"], "outputs": ["p_after_b"]},
                {"id": "t_skip", "label": "Skip", "stop": False, "inputs": ["p_choice"], "outputs": ["p_after_a"]},
            ],
            "arcs": [
                {"source": "p_choice", "target": "t_a"},
                {"source": "p_choice", "target": "t_b"},
                {"source": "p_choice", "target": "t_skip"},
                {"source": "t_a", "target": "p_after_a"},
                {"source": "t_b", "target": "p_after_b"},
                {"source": "t_skip", "target": "p_after_a"},
            ],
        }
        marking = {
            "p_choice": {"token": 1, "age": 1.0},
            "p_guard": {"token": 1, "age": 0.0},
        }

        result = self.__class__._helper(petri_net, marking)
        self.assertEqual({"C1": ["t_a", "t_b"]}, result)

    def test_ignores_choice_not_ready_due_to_duration(self) -> None:
        petri_net = {
            "places": [
                {"id": "p_choice", "label": "C1", "region_type": "choice", "duration": 2.0},
            ],
            "transitions": [
                {"id": "t_a", "label": "C1_A", "stop": True, "inputs": ["p_choice"], "outputs": []},
            ],
            "arcs": [
                {"source": "p_choice", "target": "t_a"},
            ],
        }
        marking = {
            "p_choice": {"token": 1, "age": 0.5},
        }

        result = self.__class__._helper(petri_net, marking)
        self.assertEqual({}, result)

    def test_requires_all_inputs_ready(self) -> None:
        petri_net = {
            "places": [
                {"id": "p_choice", "label": "C1", "region_type": "choice", "duration": 0.0},
                {"id": "p_guard", "label": "Guard", "region_type": "task", "duration": 0.0},
            ],
            "transitions": [
                {"id": "t_a", "label": "C1_A", "stop": True, "inputs": ["p_choice", "p_guard"], "outputs": []},
            ],
            "arcs": [
                {"source": "p_choice", "target": "t_a"},
                {"source": "p_guard", "target": "t_a"},
            ],
        }
        marking = {
            "p_choice": {"token": 1, "age": 1.0},
            "p_guard": {"token": 0, "age": 0.0},
        }

        result = self.__class__._helper(petri_net, marking)
        self.assertEqual({}, result)

    def test_handles_empty_inputs(self) -> None:
        petri_net = {"places": [], "transitions": [], "arcs": []}
        result = self.__class__._helper(petri_net, {})
        self.assertEqual({}, result)

    def test_loop_respects_visit_limit(self) -> None:
        petri_net = {
            "places": [
                {
                    "id": "p_loop",
                    "label": "L1",
                    "region_type": "loop",
                    "duration": 0.0,
                    "visit_limit": 1,
                    "entry_region_id": "loop_entry",
                },
                {
                    "id": "p_inside",
                    "label": "Inside",
                    "region_type": "task",
                    "entry_region_id": "loop_entry",
                },
                {
                    "id": "p_after",
                    "label": "After",
                    "region_type": "task",
                },
            ],
            "transitions": [
                {
                    "id": "t_continue",
                    "label": "L1_continue",
                    "stop": True,
                    "inputs": ["p_loop"],
                    "outputs": ["p_inside"],
                },
                {
                    "id": "t_exit",
                    "label": "L1_exit",
                    "stop": True,
                    "inputs": ["p_loop"],
                    "outputs": ["p_after"],
                },
            ],
            "arcs": [
                {"source": "p_loop", "target": "t_continue"},
                {"source": "p_loop", "target": "t_exit"},
                {"source": "t_continue", "target": "p_inside"},
                {"source": "t_exit", "target": "p_after"},
            ],
        }

        # After one visit the loop should only expose the exit transition.
        marking = {"p_loop": {"token": 1, "age": 1.0, "visit_count": 1}}

        result = self.__class__._helper(petri_net, marking)
        self.assertEqual({"L1": ["t_exit"]}, result)


if __name__ == "__main__":
    unittest.main()
