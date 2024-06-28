import enum
from solver.tree_lib import CNode
from collections import defaultdict

class ActivityState(enum.IntEnum):
	WILL_NOT_BE_EXECUTED = -1
	WAITING = 0
	ACTIVE = 1
	COMPLETED = 2
	COMPLETED_WIHTOUT_PASSING_OVER = 3

	def __str__(self):
		return str(self.value)


class States:
	def __init__(self, state: CNode = None, activityState: ActivityState = ActivityState.WAITING, executed_time: int = 0):
		self.activityState = defaultdict(lambda: ActivityState.WAITING)
		self.executed_time = defaultdict(lambda: 0)

		if state is not None:
			self.add(state, activityState, executed_time)

	def add(self, state: CNode, activityState: ActivityState, executed_time: int):
		self.activityState[state] = activityState
		self.executed_time[state] = executed_time

	def update(self, state: CNode):
		self.activityState.update(state.activityState)
		self.executed_time.update(state.executed_time)

	def activityState_str(self):
		result = ""
		for state in sorted(self.activityState.keys(), key=lambda x: x.id):
			result += str(state.id) + ":" + str(self.activityState[state]) + ";"
		# Remove last  ";"
		return result[:-1]

	def executed_time_str(self):
		result = ""
		for state in sorted(self.executed_time.keys(), key=lambda x: x.id):
			# If state is >= WAITING there is no need to show because will not be executed
			if self.activityState[state] >= ActivityState.WAITING:
				result += str(state.id) + ":" + str(self.executed_time[state]) + ";"
		# Remove last  ";"
		return result[:-1]

	def __str__(self):
		return self.activityState_str() + "-" + self.executed_time_str()


def node_info(node: CNode, states: States):
	name = "" if node.name is None else "name:" + node.name + '; '
	result = f"id:{node.id}; {name}type:{node.type}; q|s: {states.activityState[node]}; q|delta: {states.executed_time[node]}; "

	if node.type == 'choice':
		result += f"delta: {node.max_delay}"
	elif node.type != 'natural':
		result += f"delta: {node.duration}"

	return result


def states_info(states):
	result = 'States:\n'
	for s in sorted(states.activityState.keys(), key=lambda x: x.id):
		result += node_info(s, states) + "\n"

	return result
