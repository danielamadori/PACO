import copy
import numpy as np
from paco.saturate_execution.states import States, ActivityState
from paco.parser.parse_node import ParseNode, Sequential, Parallel, ExclusiveGateway, Nature, Task, Gateway


def evaluate_expected_impacts(states: States, impacts_size: int) -> (np.float64, np.ndarray):
	impacts = np.zeros(impacts_size, dtype=np.float64)
	probability = np.float64(1.0)

	for node, state in states.activityState.items():
		if (isinstance(node, Nature) and state > ActivityState.WAITING
				and (states.activityState[node.sx_child] > ActivityState.WAITING
					 or states.activityState[node.dx_child] > ActivityState.WAITING)):

			p = node.probability
			if states.activityState[node.dx_child] > 0:
				p = 1 - p
			probability *= p

		elif isinstance(node,Task) and state > ActivityState.WAITING:
			impacts += node.impact

	return probability, impacts


def unavoidable_tasks(root: ParseNode, states: States) -> set[ParseNode]:
	#print("root " + node_info(root, states))
	if root in states.activityState and states.activityState[root] in [ActivityState.WILL_NOT_BE_EXECUTED, ActivityState.COMPLETED, ActivityState.COMPLETED_WIHTOUT_PASSING_OVER]:
		#print("general node with: -1, 2, 3")
		return set()
	if isinstance(root, Task):
		if root not in states.activityState or (root in states.activityState and states.activityState[root] == ActivityState.WAITING):
			return set([root])
		return set()
	if isinstance(root, Sequential) or isinstance(root, Parallel):
		result = set[ParseNode]()
		result = result.union(unavoidable_tasks(root.sx_child, states))
		result = result.union(unavoidable_tasks(root.dx_child, states))
		return result

	if isinstance(root, ExclusiveGateway) and root in states.activityState and states.activityState[root] == ActivityState.ACTIVE:
		if root.sx_child in states.activityState and states.activityState[root.sx_child] == ActivityState.ACTIVE:
			return unavoidable_tasks(root.sx_child, states)
		if root.dx_child in states.activityState and states.activityState[root.dx_child] == ActivityState.ACTIVE:
			return unavoidable_tasks(root.dx_child, states)

	return set()


def evaluate_unavoidable_impacts(root: ParseNode, states: States, current_impacts: np.ndarray) -> np.ndarray:
	unavoidableImpacts = copy.deepcopy(current_impacts)
	#print("Unavoidable:\n" + states_info(states))
	for unavoidableTask in unavoidable_tasks(root, states):
		#print("unavoidableTask: " + node_info(unavoidableTask, states))
		unavoidableImpacts += unavoidableTask.impact

	return unavoidableImpacts


def evaluate_expected_impacts_from_parseNode(parseNode: ParseNode, impacts_size: int) -> (np.float64, np.ndarray):
	if isinstance(parseNode, Task):
		return parseNode.impact

	expected_impacts = np.zeros(impacts_size, dtype=np.float64)
	if isinstance(parseNode, Gateway):
		sx_expected_impacts = evaluate_expected_impacts_from_parseNode(parseNode.sx_child, impacts_size)
		dx_expected_impacts = evaluate_expected_impacts_from_parseNode(parseNode.dx_child, impacts_size)

		if isinstance(parseNode, Nature):
			sx_expected_impacts *= parseNode.probability
			dx_expected_impacts *= (1 - parseNode.probability)

		expected_impacts = sx_expected_impacts + dx_expected_impacts

	return expected_impacts
