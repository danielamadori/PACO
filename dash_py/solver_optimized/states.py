import enum
from solver.tree_lib import CNode


class ActivityState(enum.IntEnum):
	WILL_NOT_BE_EXECUTED = -1
	WAITING = 0
	ACTIVE = 1
	COMPLETED = 2


class States:
	# Indicate for the nodes with activityState = ACTIVE
	# how much time they are staying in that node.
	def __init__(self, state: CNode = None, activityState: ActivityState = ActivityState.WAITING, executed_time: int = 0):
		self.activityState = {}
		self.executed_time = {}
		if state is not None:
			self.add(state, activityState, executed_time)

	def add(self, state: CNode, activityState: ActivityState, executed_time: int):
		self.activityState[state] = activityState
		self.executed_time[state] = executed_time


def check_state(root: CNode, states: States):
	if root not in states.activityState:
		states.add(root, ActivityState.WAITING, 0)

	if (not root.isLeaf and (states.activityState[root] == ActivityState.WAITING
			or states.activityState[root] == ActivityState.ACTIVE)):
		# We need the children just if activityState[root] is waiting or active
		for subTree in root.childrens:
			if subTree.root not in states.activityState:
				states.add(subTree.root, ActivityState.WAITING, 0)


def node_info(node: CNode, states: States):
	duration = node.duration
	if node.type == 'choice':
		duration = node.max_delay
	return f"name:{node.name}; id:{node.id}; type:{node.type}; activityState: {states.activityState[node]}; executed_time: {states.executed_time[node]}; duration: {duration}"


def print_states(states):
	print('States:')
	for s in states.activityState.keys():
		print(node_info(s, states))
