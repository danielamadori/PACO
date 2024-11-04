import numpy as np

from paco.evaluations.evaluate_impacts import evaluate_expected_impacts
from paco.parser.tree_lib import CNode
from paco.saturate_execution.states import States, ActivityState
from paco.execution_tree.view_point import ViewPoint


class ExecutionViewPoint(ViewPoint):
	def __init__(self, id: int, states: States, decisions: tuple[CNode], decision_min_max_impacts: dict, choices:tuple, natures: tuple,
				 is_final_state: bool, impacts_names, parent: 'ExecutionTree' = None):

		super().__init__(id, states, decisions, is_final_state, natures, choices, parent)

		self.probability, self.impacts = evaluate_expected_impacts(states, len(impacts_names))
		self.cei_top_down:np.ndarray = self.probability * self.impacts
		self.cei_bottom_up:np.ndarray = np.zeros(len(impacts_names), dtype=np.float64)

		self.cei_max = self.probability * self.impacts
		self.cei_min = self.probability * self.impacts

		for choice in decision_min_max_impacts.keys():
			is_actual_choice = choice not in choices or choice not in natures
			if not is_actual_choice and (choice not in states.activityState or states.activityState[choice] == ActivityState.WAITING):
				max_impact = decision_min_max_impacts[choice][0] * decision_min_max_impacts[choice][2]
				min_impact = decision_min_max_impacts[choice][0] * decision_min_max_impacts[choice][1]
				print(f"Choice {choice.name}: {decision_min_max_impacts[choice][2]}, p: {decision_min_max_impacts[choice][0]}")
				self.cei_max += max_impact
				self.cei_min += min_impact

		print(f"Max impacts:{self.cei_max}")
		print(f"Min impacts:{self.cei_min}\n")


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

		label += f"EI Test Max: {self.cei_max}\n"
		label += f"EI Test Min: {self.cei_min}\n"

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
