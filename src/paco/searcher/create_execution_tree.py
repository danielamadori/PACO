import copy
import os
import pydot

from paco.execution_tree.execution_view_point import ExecutionViewPoint
from paco.parser.parse_tree import ParseTree
from paco.parser.parse_node import ParseNode
from paco.saturate_execution.saturate_execution import saturate_execution_decisions
from paco.saturate_execution.states import States, ActivityState
from paco.execution_tree.execution_tree import ExecutionTree
from utils.env import PATH_EXECUTION_TREE, RESOLUTION, PATH_EXECUTION_TREE_STATE, PATH_EXECUTION_TREE_STATE_TIME, \
	PATH_EXECUTION_TREE_STATE_TIME_EXTENDED, PATH_EXECUTION_TREE_TIME


def create_execution_tree(region_tree: ParseTree, impacts_names:list) -> (ExecutionTree, list[ExecutionTree]):
	states, choices, natures, branches = saturate_execution_decisions(region_tree, States(region_tree.root, ActivityState.WAITING, 0))

	id = 0
	solution_tree = ExecutionTree(ExecutionViewPoint(
		id=id, states=states,
		decisions=(region_tree.root,),
		choices=choices, natures=natures,
		is_final_state=states.activityState[region_tree.root] >= ActivityState.COMPLETED,
		impacts_names=impacts_names)
	)

	#print("create_execution_tree:", tree_node_info(solution_tree.root))

	for decisions, branch_states in branches.items():
		branch = copy.deepcopy(states)
		branch.update(branch_states)
		id = create_execution_viewpoint(region_tree, decisions, branch, solution_tree, id + 1, impacts_names)

	return solution_tree


def create_execution_viewpoint(region_tree: ParseTree, decisions: tuple[ParseNode], states: States, solution_tree: ExecutionTree, id: int, impacts_names:list) -> int:
	saturatedStates, choices, natures, branches = saturate_execution_decisions(region_tree, states)
	states.update(saturatedStates)

	next_node = ExecutionTree(ExecutionViewPoint(
		id=id,
		states=states,
		decisions=decisions,
		choices=choices, natures=natures,
		is_final_state=states.activityState[region_tree.root] >= ActivityState.COMPLETED,
		impacts_names=impacts_names,
		parent=solution_tree)
	)

	#print("create_execution_viewpoint:", tree_node_info(next_node.root))

	solution_tree.root.add_child(next_node)
	for decisions, branch_states in branches.items():
		branch = copy.deepcopy(states)
		branch.update(branch_states)
		id = create_execution_viewpoint(region_tree, decisions, branch, next_node, id + 1, impacts_names)
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
