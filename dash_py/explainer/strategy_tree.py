import math
import os

import numpy as np
from graphviz import Source

from saturate_execution.next_state import next_state
from saturate_execution.states import States, ActivityState, states_info
from saturate_execution.step_to_saturation import steps_to_saturation
from parser.tree_lib import CNode, CTree
from solver.execution_tree import write_image
from explainer.bdd import Bdd
from utils.env import PATH_STRATEGY_TREE, PATH_STRATEGY_TREE_STATE_DOT, PATH_STRATEGY_TREE_STATE_IMAGE_SVG, \
	PATH_STRATEGY_TREE_STATE_TIME_DOT, PATH_STRATEGY_TREE_STATE_TIME_IMAGE_SVG, \
	PATH_STRATEGY_TREE_STATE_TIME_EXTENDED_DOT, PATH_STRATEGY_TREE_STATE_TIME_EXTENDED_IMAGE_SVG, \
	PATH_STRATEGY_TREE_TIME_DOT, PATH_STRATEGY_TREE_TIME_IMAGE_SVG


def saturate_execution(region_tree: CTree, states: States) -> (States, bool, list[CNode], list[CNode]):
	while states.activityState[region_tree.root] < ActivityState.COMPLETED:
		#print("step_to_saturation:")
		#print("start:", states_info(states))

		k = steps_to_saturation(region_tree, states)
		#print('step_to_saturation:k:', k, states_info(states))

		updatedStates, k = next_state(region_tree, states, k)
		states.update(updatedStates)

		#print('next_state:k:', k, states_info(states))
		if k > 0:
			raise Exception("StepsException" + str(k))

		choices, natures = [], []
		node: CNode
		for node in list(states.activityState.keys()):
			if (node.type == 'choice'
					and states.activityState[node] == ActivityState.ACTIVE
					and states.executed_time[node] == node.max_delay
					and states.activityState[node.children[0].root] == ActivityState.WAITING
					and states.activityState[node.children[1].root] == ActivityState.WAITING):
				choices.append(node)

			if (node.type == 'natural'
					and states.activityState[node] == ActivityState.ACTIVE
					and states.activityState[node.children[0].root] == ActivityState.WAITING
					and states.activityState[node.children[1].root] == ActivityState.WAITING):
				natures.append(node)

		if len(choices) > 0 or len(natures) > 0:
			return states, False, choices, natures

	return states, True, [], []


class StrategyViewPoint:
	def __init__(self, bpmn_root: CNode, id: int, states: States, decisions: tuple[CNode], choices: dict[CNode:Bdd], natures: list[CNode],
				 is_final_state: bool, probability:float, impacts: np.ndarray, parent: 'StrategyViewPoint' = None):
		self.id = id
		self.states = states
		s, _ = self.states.str()
		self.state_id = s
		self.decisions = decisions
		self.choices = choices # dict with choices and the bdd (None if arbitrary)
		self.natures = natures
		self.choices_natures = list(choices.keys()) + natures
		self.parent = parent
		self.is_final_state = is_final_state
		self.transitions: dict[tuple, StrategyTree] = {}
		self.probability = probability
		self.impacts = impacts
		self.executed_time = states.executed_time[bpmn_root]

	def __str__(self) -> str:
		return str(self.states)

	def __hash__(self):
		return hash(str(self))

	@staticmethod
	def text_format(text: str, line_length: int):
		parts = []
		current_part = ""
		char_count = 0

		for char in text:
			current_part += char
			char_count += 1
			if char == ';' and char_count >= line_length:
				parts.append(current_part)
				current_part = ""
				char_count = 0

		if current_part:
			parts.append(current_part)

		return "\\n".join(parts)

	def dot_str(self, full: bool = True, state: bool = True, executed_time: bool = False, previous_node: States = None):
		result = str(self).replace('(', '').replace(')', '').replace(';', '_').replace(':', '_').replace('-',
																										 "neg").replace(
			' | ', '_')

		if full:
			result += f' [label=\"'

			s, d = self.states.str(previous_node)
			s = "q|s:{" + s + "}"
			d = "q|delta:{" + d + "}"

			label = f"ID: {self.id}\n"  # ""
			if state:
				label += s
			if state and executed_time:
				label += ",\n"
			if executed_time:
				label += d

			line_length = int(1.3 * math.sqrt(len(label)))
			result += (self.text_format(label, line_length)) + "\", "
			#print(f"ID: {self.id}, choice: ", len(self.choices), "natures: ", len(self.natures))
			choices_number = len(self.choices)
			natures_number = len(self.natures)
			if choices_number > 0 and natures_number == 0:
				result += "style=filled, fillcolor=\"orange\""
			elif choices_number == 0 and natures_number > 0:
				result += "style=filled, fillcolor=\"yellowgreen\""
			elif choices_number > 0 and natures_number > 0:
				result += "style=wedged, fillcolor=\"yellowgreen;0.5:orange\""

			result += "];\n"

		return result

	def add_child(self, subTree: 'StrategyTree'):
		transition = []
		for i in range(len(self.choices_natures)):
			transition.append((self.choices_natures[i], subTree.root.decisions[i],))

		self.transitions[tuple(transition)] = subTree

	def dot_info_str(self):
		label = f" [label=\"Probability: {self.probability}\nImpacts: {self.impacts}\n"
		label += f"Time: {self.executed_time}\n"

		if len(self.choices) > 0:
			label += "Choice: "
			for choice, bdd in self.choices.items():
				label += f"{choice.name}{'*' if bdd is None else''}, "
			label = label[:-2] + "\n"
		if len(self.natures) > 0:
			label += "Nature: "
			for nature in list(self.natures):
				label += f"{nature.name}, "
			label = label[:-2]

		label += "\", shape=rect];\n"
		return (self.dot_str(full=False) + "_impact", label)


class StrategyTree:
	def __init__(self, root: StrategyViewPoint):
		self.root = root

	def __str__(self) -> str:
		result = self.create_dot_graph(self.root, True, True, False)
		return result[0] + result[1]

	def state_str(self):
		return self.root.dot_str(state=True, executed_time=True, previous_node=None).split(' [')[0]

	def save_dot(self, path, state: bool = True, executed_time: bool = False, diff: bool = True):
		with open(path, 'w') as file:
			file.write(self.init_dot_graph(state=state, executed_time=executed_time, diff=diff))

	def save_pdf(self, path, state: bool = True, executed_time: bool = False, diff: bool = True):
		Source(self.init_dot_graph(state=state, executed_time=executed_time, diff=diff),
			   format='pdf').render(path, cleanup=True)

	def init_dot_graph(self, state: bool, executed_time: bool, diff: bool):
		result = "digraph automa {\n"

		node, transition = self.create_dot_graph(self.root, state=state, executed_time=executed_time,
												 diff=diff)

		result += node
		result += transition
		result += "__start0 [label=\"\", shape=none];\n"

		starting_node_ids = ""
		for n in self.root.decisions:
			starting_node_ids += str(n.id) + ";"

		if len(self.root.choices_natures) > 0:  #Just if we don't have choice
			starting_node_ids = starting_node_ids[:-1] + "->"
			for n in self.root.choices_natures:
				starting_node_ids += str(n.id) + ";"

		result += f"__start0 -> {self.root.dot_str(full=False)}  [label=\"{starting_node_ids[:-1]}\"];\n" + "}"
		return result

	def create_dot_graph(self, root: StrategyViewPoint, state: bool, executed_time: bool, diff: bool,
						 previous_node: States = None):
		if diff == False:  # print all nodes
			previous_node = None

		nodes_id = root.dot_str(state=state, executed_time=executed_time, previous_node=previous_node)
		transitions_id = ""


		impact_id, impact_label = root.dot_info_str()
		transitions_id += f"{root.dot_str(full=False)} -> {impact_id} [label=\"\" color=red];\n"  #style=invis
		nodes_id += impact_id + impact_label

		for transition in root.transitions.keys():
			next_node = root.transitions[transition].root
			x = ""
			for t in transition:
				x += str(t[0].id) + '->' + str(t[1].id) + ';'
			#x += str(t)[1:-1].replace(',', '->') + ";"

			transitions_id += f"{root.dot_str(full=False)} -> {next_node.dot_str(full=False)} [label=\"{x[:-1]}\"];\n"

			ids = self.create_dot_graph(next_node, state=state, executed_time=executed_time, diff=diff,
										previous_node=root.states)
			nodes_id += ids[0]
			transitions_id += ids[1]

		return nodes_id, transitions_id


def tree_node_info(node: StrategyViewPoint) -> str:
	result = f"ID:{node.id}:decisions:<"
	for n in list(node.decisions):
		result += str(n.id) + ";"
	result = result[:-1]

	if len(node.choices) > 0:
		result += ">:choices:<"
		tmp = ""
		for n in node.choices:
			tmp += str(n.id) + ";"
		result += tmp[:-1]
	if len(node.natures) > 0:
		result += ">:natures:<"
		tmp = ""
		for n in node.natures:
			tmp += str(n.id) + ";"
		result += tmp[:-1]

	return result + ">:status:\n" + states_info(node.states)


def write_strategy_tree(solution_tree: StrategyTree, frontier: list[StrategyTree] = []):
	if not os.path.exists(PATH_STRATEGY_TREE):
		os.makedirs(PATH_STRATEGY_TREE)

	solution_tree.save_dot(PATH_STRATEGY_TREE_STATE_DOT)
	write_image(frontier, PATH_STRATEGY_TREE_STATE_DOT,
				svgPath=PATH_STRATEGY_TREE_STATE_IMAGE_SVG)  #, PATH_STRATEGY_TREE_STATE_IMAGE_SVG)

	solution_tree.save_dot(PATH_STRATEGY_TREE_STATE_TIME_DOT, executed_time=True)
	write_image(frontier, PATH_STRATEGY_TREE_STATE_TIME_DOT,
				svgPath=PATH_STRATEGY_TREE_STATE_TIME_IMAGE_SVG)  #, PATH_STRATEGY_TREE_STATE_TIME_IMAGE_SVG)

	solution_tree.save_dot(PATH_STRATEGY_TREE_STATE_TIME_EXTENDED_DOT, executed_time=True, diff=False)
	write_image(frontier, PATH_STRATEGY_TREE_STATE_TIME_EXTENDED_DOT,
				svgPath=PATH_STRATEGY_TREE_STATE_TIME_EXTENDED_IMAGE_SVG)  #, PATH_STRATEGY_TREE_STATE_TIME_EXTENDED_IMAGE_SVG)

	solution_tree.save_dot(PATH_STRATEGY_TREE_TIME_DOT, state=False, executed_time=True)
	write_image(frontier, PATH_STRATEGY_TREE_TIME_DOT,
				svgPath=PATH_STRATEGY_TREE_TIME_IMAGE_SVG)  #, PATH_STRATEGY_TREE_TIME_IMAGE_SVG)
