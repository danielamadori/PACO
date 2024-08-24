import copy
import math
import numpy as np
import pydot
from graphviz import Source
from solver.tree_lib import CNode, CTree
from saturate_execution.saturate_execution import saturate_execution
from saturate_execution.states import States, states_info, ActivityState
from utils.env import RESOLUTION, PATH_AUTOMA_DOT, PATH_AUTOMA_IMAGE_SVG, PATH_AUTOMA_TIME_DOT, \
	PATH_AUTOMA_TIME_IMAGE_SVG, PATH_AUTOMA_TIME_EXTENDED_DOT, \
	PATH_AUTOMA_TIME_EXTENDED_IMAGE_SVG


class ExecutionViewPoint:
	def __init__(self, id: int, states: States, decisions: tuple[CNode], choices_natures: tuple,
				parent: 'ExecutionTree', is_final_state: bool):
		self.id = id
		self.states = states
		s, _ = self.states.str()
		self.state_id = s
		self.decisions = decisions
		self.choices_natures = choices_natures
		self.parent = parent
		self.is_final_state = is_final_state
		self.transitions: dict[tuple, ExecutionTree] = {}
		self.probability = None
		self.impacts = None
		self.probability, self.impacts = ExecutionViewPoint.impacts_evaluation(states)
		self.cei_top_down = np.zeros(len(self.impacts), dtype=np.float64)
		self.cei_bottom_up = np.zeros(len(self.impacts), dtype=np.float64)

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

			label = f"ID: {self.id}\n" # ""
			if state:
				label += s
			if state and executed_time:
				label += ",\n"
			if executed_time:
				label += d

			line_length = int(1.3 * math.sqrt(len(label)))
			result += self.text_format(label, line_length) + "\"];\n"

		return result

	def add_child(self, subTree: 'ExecutionTree'):
		transition = []
		for i in range(len(self.choices_natures)):
			transition.append((self.choices_natures[i], subTree.root.decisions[i],))

		self.transitions[tuple(transition)] = subTree

	@staticmethod
	def impacts_evaluation(states: States):
		impacts = None

		probability = 1.0
		for node, state in states.activityState.items():
			if (node.type == 'natural' and state > ActivityState.WAITING
					and (states.activityState[node.childrens[0].root] > ActivityState.WAITING
						 or states.activityState[node.childrens[1].root] > ActivityState.WAITING)):

				p = node.probability
				if states.activityState[node.childrens[1].root] > 0:
					p = 1 - p
				probability *= p

			if node.type == 'task':
				if state > ActivityState.WAITING:
					if impacts is None:
						impacts = np.array(node.impact, dtype=np.float64)
					elif state > 0:
						impacts += node.impact
				else:
					if impacts is None:
						impacts = np.zeros(len(node.impact), dtype=np.float64)

		return probability, impacts

	def dot_cei_str(self):
		return (self.dot_str(full=False) + "_impact",
				f" [label=\"(cei_td: {self.cei_top_down},\ncei_bu: {self.cei_bottom_up})\", shape=rect];\n")
				#f" [label=\"ID: {self.id} (cei_td: {self.cei_top_down},\ncei_bu: {self.cei_bottom_up})\", shape=rect];\n")


class ExecutionTree:
	def __init__(self, root: ExecutionViewPoint):
		self.root = root

	def __str__(self) -> str:
		result = self.create_dot_graph(self.root, True, True, True)
		return result[0] + result[1]

	def state_str(self):
		return self.root.dot_str(state=True, executed_time=True, previous_node=None).split(' [')[0]

	def save_dot(self, path, state: bool = True, executed_time: bool = False, all_states: bool = False):
		with open(path, 'w') as file:
			file.write(self.init_dot_graph(state=state, executed_time=executed_time, all_states=all_states))

	def save_pdf(self, path, state: bool = True, executed_time: bool = False, all_states: bool = False):
		Source(self.init_dot_graph(state=state, executed_time=executed_time, all_states=all_states),
			   format='pdf').render(path, cleanup=True)

	def init_dot_graph(self, state: bool, executed_time: bool, all_states: bool):
		result = "digraph automa {\n"

		node, transition = self.create_dot_graph(self.root, state=state, executed_time=executed_time,
												 all_states=all_states)

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

	def create_dot_graph(self, root: ExecutionViewPoint, state: bool, executed_time: bool, all_states: bool,
						 previous_node: States = None):
		if all_states:
			previous_node = None

		nodes_id = root.dot_str(state=state, executed_time=executed_time, previous_node=previous_node)
		transitions_id = ""

		impact_id, impact_label = root.dot_cei_str()
		transitions_id += f"{root.dot_str(full=False)} -> {impact_id} [label=\"\" color=red];\n"  #style=invis
		nodes_id += impact_id + impact_label

		for transition in root.transitions.keys():
			next_node = root.transitions[transition].root
			x = ""
			for t in transition:
				x += str(t[0].id) + '->' + str(t[1].id) + ';'
			#x += str(t)[1:-1].replace(',', '->') + ";"

			transitions_id += f"{root.dot_str(full=False)} -> {next_node.dot_str(full=False)} [label=\"{x[:-1]}\"];\n"

			ids = self.create_dot_graph(next_node, state=state, executed_time=executed_time, all_states=all_states,
										previous_node=root.states)
			nodes_id += ids[0]
			transitions_id += ids[1]

		return nodes_id, transitions_id


def tree_node_info(node: ExecutionViewPoint) -> str:
	result = f"ID:{node.id}:decisions:<"
	for n in node.decisions:
		result += str(n.id) + ";"

	result = result[:-1] + ">:choices_natures:<"
	tmp = ""
	for n in node.choices_natures:
		tmp += str(n.id) + ";"

	return result + tmp[:-1] + ">:status:\n" + states_info(node.states)


def create_execution_tree(region_tree: CTree) -> (ExecutionTree, list[ExecutionTree]):
	states, choices_natures, branches = saturate_execution(region_tree, States(region_tree.root, ActivityState.WAITING, 0))

	solution_tree = ExecutionTree(ExecutionViewPoint(
		id=0, states=states,
		decisions=(region_tree.root,),
		choices_natures=choices_natures,
		is_final_state=states.activityState[region_tree.root] >= ActivityState.COMPLETED,
		parent=None)
	)

	print("create_tree:", tree_node_info(solution_tree.root))

	nodes = [solution_tree]
	next_id = 0
	for decisions, branch_states in branches.items():
		branch = copy.deepcopy(states)
		branch.update(branch_states)
		sub_nodes, last_child_id = create_execution_viewpoint(region_tree, decisions, branch, solution_tree, next_id + 1)
		nodes.extend(sub_nodes)
		next_id = last_child_id

	return solution_tree, nodes


def create_execution_viewpoint(region_tree: CTree, decisions: tuple[CNode], states: States, solution_tree: ExecutionTree, id: int) -> list[ExecutionTree]:
	saturatedStates, choices_natures, branches = saturate_execution(region_tree, states)
	states.update(saturatedStates)

	next_node = ExecutionTree(ExecutionViewPoint(
		id=id,
		states=states,
		decisions=decisions,
		choices_natures=choices_natures,
		is_final_state=states.activityState[region_tree.root] >= ActivityState.COMPLETED,
		parent=solution_tree)
	)

	print("create_tree_node:", tree_node_info(next_node.root))

	solution_tree.root.add_child(next_node)
	nodes = [next_node]

	for decisions, branch_states in branches.items():
		branch = copy.deepcopy(states)
		branch.update(branch_states)
		tmp, last_child_id = create_execution_viewpoint(region_tree, decisions, branch, next_node, id + 1)
		nodes.extend(tmp)
		id = last_child_id

	return nodes, id


def write_image(frontier: list[ExecutionTree], dotPath: str, svgPath: str = "", pngPath: str = ""):
	graphs = pydot.graph_from_dot_file(dotPath)
	graph = graphs[0]
	# print([node.get_name() for node in graph.get_nodes()])
	# color the winning nodes
	if frontier is not None:
		for el in frontier:
			node = graph.get_node('"' + el.state_str() + '"')[0]
			node.set_style('filled')
			node.set_fillcolor('green')

	# if svgPath not ""
	if svgPath != "":
		graph.write_svg(svgPath)

	graph.set('dpi', RESOLUTION)
	if pngPath != "":
		graph.write_png(pngPath)


def write_execution_tree(solution_tree: ExecutionTree, frontier: list[ExecutionTree] = []):
	solution_tree.save_dot(PATH_AUTOMA_DOT)
	write_image(frontier, PATH_AUTOMA_DOT, svgPath=PATH_AUTOMA_IMAGE_SVG)#, PATH_AUTOMA_IMAGE)

	solution_tree.save_dot(PATH_AUTOMA_TIME_DOT, executed_time=True)
	write_image(frontier, PATH_AUTOMA_TIME_DOT, svgPath=PATH_AUTOMA_TIME_IMAGE_SVG)#, PATH_AUTOMA_TIME_IMAGE)

	solution_tree.save_dot(PATH_AUTOMA_TIME_EXTENDED_DOT, executed_time=True, all_states=True)
	write_image(frontier, PATH_AUTOMA_TIME_EXTENDED_DOT, svgPath=PATH_AUTOMA_TIME_EXTENDED_IMAGE_SVG)#, PATH_AUTOMA_TIME_EXTENDED_IMAGE)
