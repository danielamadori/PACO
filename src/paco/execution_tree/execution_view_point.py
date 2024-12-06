import numpy as np
from paco.evaluations.evaluate_cumulative_expected_impacts import evaluate_min_max_impacts
from paco.evaluations.evaluate_impacts import evaluate_expected_impacts
from paco.parser.parse_node import ParseNode, Parallel
from paco.saturate_execution.states import States, ActivityState
from paco.execution_tree.view_point import ViewPoint


class ExecutionViewPoint(ViewPoint):
	def __init__(self, id: int, states: States, decisions: tuple[ParseNode], choices:tuple, natures: tuple,
				 is_final_state: bool, impacts_names, parent: 'ExecutionTree' = None):

		super().__init__(id, states, decisions, is_final_state, natures, choices, parent)

		self.probability, self.impacts = evaluate_expected_impacts(states, len(impacts_names))
		self.cei_top_down:np.ndarray = self.probability * self.impacts
		self.cei_bottom_up:np.ndarray = np.zeros(len(impacts_names), dtype=np.float64)

		pending_decisions = [*choices]
		unavoidable_pending_activities = [elem for elem in states.activityState if elem.parent not in pending_decisions and states.activityState[elem] == ActivityState.WAITING]

		self.min_impacts = np.zeros(len(impacts_names), dtype=np.float64)
		self.max_impacts = np.zeros(len(impacts_names), dtype=np.float64)
		for pending_activity in unavoidable_pending_activities:
			min_imp, max_imp = evaluate_min_max_impacts(pending_activity)
			self.min_impacts += min_imp
			self.max_impacts += max_imp

		pending_decisions_min_impacts = np.array(self.min_impacts)
		pending_decisions_max_impacts = np.array(self.max_impacts)
		for pending_decision in pending_decisions:
			min_imp, max_imp = evaluate_min_max_impacts(pending_decision)
			pending_decisions_min_impacts += min_imp
			pending_decisions_max_impacts += max_imp

			min_imp, max_imp = evaluate_min_max_impacts(pending_decision.sx_child)
			min_imp += self.min_impacts
			max_imp += self.max_impacts
			print(f"Pending Decisions {pending_decision.sx_child.name} Min impacts:{min_imp}")
			print(f"Pending Decisions {pending_decision.sx_child.name} Max impacts:{max_imp}")

			min_imp, max_imp = evaluate_min_max_impacts(pending_decision.dx_child)
			min_imp += self.min_impacts
			max_imp += self.max_impacts
			print(f"Pending Decisions {pending_decision.dx_child.name} Min impacts:{min_imp}")
			print(f"Pending Decisions {pending_decision.dx_child.name} Max impacts:{max_imp}")

		print(f"Total Pending Decisions Min impacts:{pending_decisions_min_impacts}")
		print(f"Total Pending Decisions Max impacts:{pending_decisions_max_impacts}\n")

		self.min_impacts = pending_decisions_min_impacts
		self.max_impacts = pending_decisions_max_impacts




	def dot_str(self, full: bool = True, state: bool = True, executed_time: bool = False, previous_node: States = None):
		result = super().common_dot_str(full, state, executed_time, previous_node)
		if full:
			result += "];\n"

		return result

	def dot_info_str(self):
		label = f"Impacts: {self.impacts}\n"
		if self.probability != 1:
			label += f"Probability: {round(self.probability, 2)}\n"
		label += f"EI Current: {self.cei_top_down}\n"
		#if not self.is_final_state:
		label += f"EI Max: {self.cei_bottom_up}\n"

		label += f"EI Test Max: {self.max_impacts}\n"
		label += f"EI Test Min: {self.min_impacts}\n"

		choice_label = ""
		nature_label = ""

		for choice in self.choices:
			choice_label += f"{choice.name}, "
		for nature in self.natures:
			nature_label += f"{nature.name}, "

		if nature_label != "":
			label += "Nature: " + nature_label[:-2] + "\n"
		if choice_label != "":
			label += "Choice: " + choice_label[:-2] + "\n"

		return self.dot_str(full=False) + "_description", f" [label=\"{label}\", shape=rect];\n"
