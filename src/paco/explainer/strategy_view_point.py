import numpy as np

from paco.execution_tree.view_point import ViewPoint
from paco.explainer.bdd.bdd import Bdd
from paco.parser.parse_node import ParseNode
from paco.saturate_execution.states import States

class StrategyViewPoint(ViewPoint):
	def __init__(self, bpmn_root: ParseNode, id: int, states: States, decisions: tuple[ParseNode], choices: dict[ParseNode:Bdd], natures: list[ParseNode],
				 is_final_state: bool, probability:np.float64, impacts: np.ndarray, pending_choice:set, parent = None, expected_impacts: np.ndarray = None, expected_time: np.float64 = None, explained_choices: dict[ParseNode:Bdd] = None):
		super().__init__(id, states, decisions, is_final_state, tuple(natures), tuple(choices), pending_choice, parent)

		self.probability = probability
		self.impacts = impacts
		self.executed_time = states.executed_time[bpmn_root]

		if explained_choices is None:
			# Each choice is a key and the value is the bdd (None if arbitrary)
			self.explained_choices: dict[ParseNode:Bdd] = {choice: None for choice in choices}
			# initially all choices are arbitrary, will be updated using make_decisions
		if expected_impacts is None or expected_time is None:
			self.expected_impacts = probability * impacts
			self.expected_time = probability * self.executed_time



	def dot_str(self, full: bool = True, state: bool = True, executed_time: bool = False, previous_node: States = None):
		result = super().common_dot_str(full, state, executed_time, previous_node)
		if full:
			#print(f"ID: {self.id}, choice: ", len(self.choices), "natures: ", len(self.natures))
			choices_number = len(self.explained_choices)
			natures_number = len(self.natures)
			if choices_number > 0 and natures_number == 0:
				result += "style=filled, fillcolor=\"orange\""
			elif choices_number == 0 and natures_number > 0:
				result += "style=filled, fillcolor=\"yellowgreen\""
			elif choices_number > 0 and natures_number > 0:
				result += "style=wedged, fillcolor=\"yellowgreen;0.5:orange\""

			result += "];\n"

		return result

	def dot_info_str(self):
		label = f" [label=\""
		label += f"Time: {self.executed_time}\n"
		label += f"Impacts: {self.impacts}\n"
		if self.probability != 1:
			label += f"Probability: {round(self.probability, 2)}\n"
			label += f"Exp. Time: {round(self.expected_time, 2)}\n"
			label += f"Exp. Impacts: {np.round(self.expected_impacts, 2)}\n"
		if len(self.natures) > 0:
			label += "Nature: "
			for nature in list(self.natures):
				label += f"{nature.name}, "
			label = label[:-2] + "\n"
		if len(self.explained_choices) > 0:
			label += "Choice:\n"
			for choice, bdd in self.explained_choices.items():
				label += f"{choice.name}: {'arbitrary' if bdd is None else str(bdd.typeStrategy)}\n"

		label += "\", shape=rect];\n"
		return self.dot_str(full=False) + "__description", label


	def to_dict(self) -> dict:
		base = super().to_dict()
		base.update({
			"probability": self.probability,
			"impacts": self.impacts.tolist(),
			"executed_time": self.executed_time,
			"expected_impacts": self.expected_impacts.tolist(),
			"expected_time": self.expected_time,
			"explained_choices": {choice.id: None if bdd is None else bdd.to_dict() for choice, bdd in self.explained_choices.items()}
		})
		return base
