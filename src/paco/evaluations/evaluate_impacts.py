import copy
import numpy as np
from src.paco.saturate_execution.states import States, ActivityState
from src.paco.parser.parse_node import ParseNode, Sequential, Parallel, ExclusiveGateway, Nature, Task, Gateway


def evaluate_expected_impacts(states: States, impacts_size: int) -> (np.float64, np.ndarray):
	impacts = np.zeros(impacts_size, dtype=np.float64)
	probability = np.float64(1.0)

	for node, state in states.activityState.items():
		if (isinstance(node, Nature) and state > ActivityState.WAITING
				and ((node.sx_child in states.activityState and states.activityState[node.sx_child] > ActivityState.WAITING)
					 or (node.dx_child in states.activityState and states.activityState[node.dx_child] > ActivityState.WAITING))):

			p = node.probability
			if states.activityState[node.dx_child] > 0:
				p = 1 - p
			probability *= p

		elif isinstance(node,Task) and state > ActivityState.WAITING:
			impacts += node.impacts

	return probability, impacts

def evaluate_expected_impacts_from_parseNode(parseNode: ParseNode, impacts_size: int) -> (np.float64, np.ndarray):
	probability = np.float64(1)

	if isinstance(parseNode, Task):
		return parseNode.impacts

	expected_impacts = np.zeros(impacts_size, dtype=np.float64)
	if isinstance(parseNode, Gateway):
		sx_expected_impacts = evaluate_expected_impacts_from_parseNode(parseNode.sx_child, impacts_size)
		dx_expected_impacts = evaluate_expected_impacts_from_parseNode(parseNode.dx_child, impacts_size)
		if isinstance(parseNode, Nature):
			sx_expected_impacts *= parseNode.probability
			dx_expected_impacts *= (1 - parseNode.probability)

		expected_impacts = sx_expected_impacts + dx_expected_impacts

	return expected_impacts
