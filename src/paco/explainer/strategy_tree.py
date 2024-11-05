import os
from paco.saturate_execution.next_state import next_state
from paco.saturate_execution.states import States, ActivityState
from paco.saturate_execution.step_to_saturation import steps_to_saturation
from paco.parser.tree_lib import CNode, CTree
from paco.searcher.create_execution_tree import write_image
from paco.execution_tree.execution_tree import ExecutionTree
from utils.env import PATH_STRATEGY_TREE, PATH_STRATEGY_TREE_STATE, PATH_STRATEGY_TREE_STATE_TIME, \
	PATH_STRATEGY_TREE_STATE_TIME_EXTENDED, PATH_STRATEGY_TREE_TIME


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