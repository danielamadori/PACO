import os
from paco.saturate_execution.next_state import next_state
from paco.saturate_execution.states import States, ActivityState
from paco.saturate_execution.step_to_saturation import steps_to_saturation
from paco.parser.parse_tree import ParseTree
from paco.parser.parse_node import ParseNode, Choice, Nature
from paco.searcher.create_execution_tree import write_image
from paco.execution_tree.execution_tree import ExecutionTree
from utils.env import PATH_STRATEGY_TREE, PATH_STRATEGY_TREE_STATE, PATH_STRATEGY_TREE_STATE_TIME, \
	PATH_STRATEGY_TREE_STATE_TIME_EXTENDED, PATH_STRATEGY_TREE_TIME


def saturate_execution(region_tree: ParseTree, states: States, pending_choices:set, pending_natures:set) -> (States, bool, list[ParseNode], list[ParseNode]):
	while states.activityState[region_tree.root] < ActivityState.COMPLETED:
		#print("step_to_saturation:")
		#print("start:", states_info(states))

		k = steps_to_saturation(region_tree.root, states)
		#print('step_to_saturation:k:', k, states_info(states))

		updatedStates, k = next_state(region_tree.root, states, k)
		states.update(updatedStates)

		#print('next_state:k:', k, states_info(states))
		if k > 0:
			raise Exception("StepsException" + str(k))

		choices, natures = [], []
		node: ParseNode
		for node in list(states.activityState.keys()):
			if (isinstance(node, Choice)
					and states.activityState[node] == ActivityState.ACTIVE
					and states.executed_time[node] == node.max_delay
					and states.activityState[node.sx_child] == ActivityState.WAITING
					and states.activityState[node.dx_child] == ActivityState.WAITING):
				choices.append(node)

			if (isinstance(node, Nature)
					and states.activityState[node] == ActivityState.ACTIVE
					and states.activityState[node.sx_child] == ActivityState.WAITING
					and states.activityState[node.dx_child] == ActivityState.WAITING):
				natures.append(node)

		pending_choices = pending_choices - set(choices)
		pending_natures = pending_natures - set(natures)
		if len(choices) > 0 or len(natures) > 0:
			return states, False, choices, natures, pending_choices, pending_natures

	return states, True, [], [], pending_choices, pending_natures


def write_strategy_tree(solution_tree: ExecutionTree):
	if not os.path.exists(PATH_STRATEGY_TREE):
		os.makedirs(PATH_STRATEGY_TREE)

	frontier = []

	solution_tree.save_dot(PATH_STRATEGY_TREE_STATE + '.dot')
	write_image(frontier, PATH_STRATEGY_TREE_STATE)  #, PATH_STRATEGY_TREE_STATE_IMAGE_SVG)

	solution_tree.save_dot(PATH_STRATEGY_TREE_STATE_TIME + '.dot', executed_time=True)
	write_image(frontier, PATH_STRATEGY_TREE_STATE_TIME)

	solution_tree.save_dot(PATH_STRATEGY_TREE_STATE_TIME_EXTENDED + '.dot', executed_time=True, diff=False)
	write_image(frontier, PATH_STRATEGY_TREE_STATE_TIME_EXTENDED)

	solution_tree.save_dot(PATH_STRATEGY_TREE_TIME + '.dot', state=False, executed_time=True)
	write_image(frontier, PATH_STRATEGY_TREE_TIME)

	os.remove(PATH_STRATEGY_TREE_STATE + '.dot')
	os.remove(PATH_STRATEGY_TREE_STATE_TIME + '.dot')
	os.remove(PATH_STRATEGY_TREE_TIME + '.dot')
	os.remove(PATH_STRATEGY_TREE_STATE_TIME_EXTENDED + '.dot')