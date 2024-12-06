import numpy as np
from paco.evaluations.evaluate_cumulative_expected_impacts import evaluate_min_max_impacts
from paco.evaluations.evaluate_impacts import evaluate_expected_impacts
from paco.parser.parse_node import ParseNode
from paco.saturate_execution.states import States
from paco.execution_tree.view_point import ViewPoint


class ExecutionViewPoint(ViewPoint):
	def __init__(self, id: int, states: States, decisions: tuple[ParseNode], choices:tuple, natures: tuple,
				 is_final_state: bool, impacts_names, parent: 'ExecutionTree' = None):

		super().__init__(id, states, decisions, is_final_state, natures, choices, parent)

		self.probability, self.impacts = evaluate_expected_impacts(states, len(impacts_names))
		self.cei_top_down:np.ndarray = self.probability * self.impacts
		self.cei_bottom_up:np.ndarray = np.zeros(len(impacts_names), dtype=np.float64)

		self.cei_max = self.probability * self.impacts
		self.cei_min = self.probability * self.impacts

		min_impacts = np.zeros(len(impacts_names), dtype=np.float64)
		max_impacts = np.zeros(len(impacts_names), dtype=np.float64)


		pending_choices_natures = [*choices, *natures]
		pending_activity = [elem for elem in states.activityState if elem.parent not in pending_choices_natures and states.activityState[elem] == ActivityState.WAITING]
		pending_activity.extend(pending_choices_natures)
		#print all the nodes names
		print(f"Activity nodes: {[elem.name for elem in pending_activity]}")

		parallel = CNode(None, None,'parallel')
		parallel.set_children([CTree(elem) for elem in pending_activity])

		decision_min_max_impacts = {}
		min_imp, max_imp = evaluate_min_max_impacts(CTree(parallel), decision_min_max_impacts, len(impacts_names))
		for choice in decision_min_max_impacts.keys():
			print(f"Choice {choice.name}: max: {decision_min_max_impacts[choice][1]}, min: {decision_min_max_impacts[choice][0]}")
			#min_impacts += min_imp
			#max_impacts += max_imp

		self.cei_max += max_imp
		self.cei_min += min_imp

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
