import copy

from paco.parser.parse_node import ParseNode, ExclusiveGateway, Choice, Gateway, Nature
from paco.saturate_execution.states import States, ActivityState
from itertools import product


def get_excluded_gateways(inactiveNode: ParseNode) -> set[ParseNode]:
	excluded_choice, excluded_nature = set(), set()
	if isinstance(inactiveNode, Choice):
		excluded_choice.add(inactiveNode)
	elif isinstance(inactiveNode, Nature):
		excluded_nature.add(inactiveNode)

	if isinstance(inactiveNode, Gateway):
		sx_excluded_choice, sx_excluded_nature = get_excluded_gateways(inactiveNode.sx_child)
		dx_excluded_choice, dx_excluded_nature = get_excluded_gateways(inactiveNode.dx_child)
		excluded_choice.update(sx_excluded_choice)
		excluded_choice.update(dx_excluded_choice)
		excluded_nature.update(sx_excluded_nature)
		excluded_nature.update(dx_excluded_nature)

	return excluded_choice, excluded_nature


def create_branches(states: States, pending_choices:set, pending_natures:set) -> (tuple[ParseNode], dict[tuple[ParseNode], (States,set,set)]):
	choices_natures = []
	choices = []
	natures = []
	node: ParseNode

	for node in list(states.activityState.keys()):
		if (isinstance(node, ExclusiveGateway)
				and states.activityState[node] == ActivityState.ACTIVE
				and states.activityState[node.sx_child] == ActivityState.WAITING
				and states.activityState[node.dx_child] == ActivityState.WAITING):

			if isinstance(node, Choice):
				if states.executed_time[node] < node.max_delay:
					continue
				choices.append(node)
			else:
				natures.append(node)

			choices_natures.append(node)
			#print(f"create_branches:active_choice-nature:" + node_info(node, states))

	pending_choices = pending_choices - set(choices)
	pending_natures = pending_natures - set(natures)

	branches = {}
	if len(choices_natures) == 0:
		return tuple(choices), tuple(natures), pending_choices, pending_natures, branches

	branches_choices = list(product([True, False], repeat=len(choices_natures)))
	#print(f"create_branches:cardinality:{choice_nature_dim}:combinations:{branches_choices}")
	for branch_choices in branches_choices:
		branch_states = copy.deepcopy(states)
		excluded_choice, excluded_nature = set(), set()
		decisions = []
		for i in range(len(choices_natures)):
			node = choices_natures[i]

			if branch_choices[i]:
				activeNode = node.sx_child
				inactiveNode = node.dx_child
			else:
				activeNode = node.dx_child
				inactiveNode = node.sx_child

			decisions.append(activeNode)
			branch_states.activityState[activeNode] = ActivityState.ACTIVE
			branch_states.activityState[inactiveNode] = ActivityState.WILL_NOT_BE_EXECUTED
			excluded_choice, excluded_nature = get_excluded_gateways(inactiveNode)


		branch_pending_choices = set(choice for choice in pending_choices if choice not in excluded_choice)
		branch_pending_natures = set(nature for nature in pending_natures if nature not in excluded_nature)
		branches[tuple(decisions)] = (branch_states, branch_pending_choices, branch_pending_natures)

	return tuple(choices), tuple(natures), pending_choices, pending_natures, branches
