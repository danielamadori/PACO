import os
import numpy as np
import pydot

from paco.evaluations.evaluate_impacts import evaluate_expected_impacts_from_parseNode, evaluate_expected_impacts
from paco.execution_tree.execution_view_point import ExecutionViewPoint
from paco.parser.parse_tree import ParseTree
from paco.parser.parse_node import ParseNode
from paco.saturate_execution.saturate_execution import saturate_execution_decisions
from paco.saturate_execution.states import States, ActivityState
from paco.execution_tree.execution_tree import ExecutionTree
from utils.env import PATH_EXECUTION_TREE, RESOLUTION, PATH_EXECUTION_TREE_STATE, PATH_EXECUTION_TREE_STATE_TIME, \
	PATH_EXECUTION_TREE_STATE_TIME_EXTENDED, PATH_EXECUTION_TREE_TIME

def evaluate_viewPoint(id, region_tree, decisions: tuple[ParseNode], states:States, pending_choices:set, pending_natures:set, solution_tree:ExecutionTree, impacts_size:int) -> (ExecutionViewPoint, dict[tuple[ParseNode], (States,set,set)]):
	states, choices, natures, pending_choices, pending_natures, branches = saturate_execution_decisions(region_tree, states, pending_choices, pending_natures)
	probability, impacts = evaluate_expected_impacts(states, impacts_size)
	cei_bottom_up = np.zeros(impacts_size, dtype=np.float64)

	earlyStop = len(pending_choices) + len(choices) == 0 and len(pending_natures) + len(natures) > 0
	earlyStop = False # TODO Daniel: earlyStop
	if earlyStop:
		print(f"EarlyStop:id:{id}: No pending choices, pending nature: {[n.name for n in pending_natures]}, nature: {[n.name for n in natures]}")
		for nature in natures:
			cei_bottom_up += evaluate_expected_impacts_from_parseNode(nature, impacts_size)
		for node in list(states.activityState.keys()):
			if states.activityState[node] == ActivityState.WAITING:
				cei_bottom_up += evaluate_expected_impacts_from_parseNode(node, impacts_size)
		#		print(f"Node:id:{node.id}:", evaluate_expected_impacts_from_parseNode(node, impacts_size))

		branches = {}

	#cei_bottom_up = probability * (cei_bottom_up + impacts)
	#impacts += cei_bottom_up
	#print("cei_bottom_up:", cei_bottom_up)
	#print("Impacts + cei_bottom_up:", impacts)

	return (ExecutionTree(ExecutionViewPoint(
				id=id, states=states, decisions=decisions, choices=choices, natures=natures,
				is_final_state=states.activityState[region_tree.root] >= ActivityState.COMPLETED,
				probability=probability, impacts=impacts,
				cei_top_down=probability * impacts, cei_bottom_up=cei_bottom_up,
				pending_choices=pending_choices, pending_natures=pending_natures,
				parent=solution_tree)),
			branches)


def create_execution_tree(region_tree: ParseTree, impacts_names:list, pending_choices:set, pending_natures:set) -> ExecutionTree:
	id = 0
	solution_tree, branches = evaluate_viewPoint(id, region_tree, (region_tree.root,), States(region_tree.root, ActivityState.WAITING, 0), pending_choices, pending_natures, None, len(impacts_names))

	for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
		id = create_execution_viewpoint(region_tree, decisions, branch_states, solution_tree, id + 1, pending_choices, pending_natures, impacts_names)

	return solution_tree


def create_execution_viewpoint(region_tree: ParseTree, decisions: tuple[ParseNode], states: States, solution_tree: ExecutionTree, id: int, pending_choices:set, pending_natures:set, impacts_names:list) -> int:
	new_solution_tree, branches = evaluate_viewPoint(id, region_tree, decisions, states, pending_choices, pending_natures, solution_tree, len(impacts_names))

	solution_tree.root.add_child(new_solution_tree)
	for decisions, (branch_states, pending_choices, pending_natures) in branches.items():
		id = create_execution_viewpoint(region_tree, decisions, branch_states, new_solution_tree, id + 1, pending_choices, pending_natures, impacts_names)

	return id


def write_image(frontier: list[ExecutionTree], path: str):
	graph = pydot.graph_from_dot_file(path + '.dot')[0]

	for tree in frontier:
		node = tree.root
		dot_node = graph.get_node(str(node.id))
		if len(dot_node) == 0:
			raise Exception("Node of thee frontier not found in the dot file")
		dot_node = dot_node[0]
		dot_node.set_style('filled')
		dot_node.set_fillcolor('lightblue')

	graph.write_svg(path + '.svg')

	#graph.set('dpi', RESOLUTION)
	#graph.write_png(path + '.png')


def write_execution_tree(solution_tree: ExecutionTree, frontier: list[ExecutionTree] = []):
	if not os.path.exists(PATH_EXECUTION_TREE):
		os.makedirs(PATH_EXECUTION_TREE)

	solution_tree.save_dot(PATH_EXECUTION_TREE_STATE + '.dot', diff=False)
	write_image(frontier, PATH_EXECUTION_TREE_STATE)

	solution_tree.save_dot(PATH_EXECUTION_TREE_STATE_TIME + '.dot', executed_time=True)
	write_image(frontier, PATH_EXECUTION_TREE_STATE_TIME)

	solution_tree.save_dot(PATH_EXECUTION_TREE_STATE_TIME_EXTENDED + '.dot', executed_time=True, diff=False)
	write_image(frontier, PATH_EXECUTION_TREE_STATE_TIME_EXTENDED)

	solution_tree.save_dot(PATH_EXECUTION_TREE_TIME + '.dot', state=False, executed_time=True)
	write_image(frontier, PATH_EXECUTION_TREE_TIME)

	os.remove(PATH_EXECUTION_TREE_STATE + '.dot')
	os.remove(PATH_EXECUTION_TREE_STATE_TIME + '.dot')
	os.remove(PATH_EXECUTION_TREE_STATE_TIME_EXTENDED + '.dot')
	os.remove(PATH_EXECUTION_TREE_TIME + '.dot')
