import math
from paco.parser.tree_lib import ParseNode, Task, ExclusiveGateway, Choice, Sequential, Parallel
from paco.saturate_execution.states import States, ActivityState, node_info


def steps_to_saturation(root: ParseNode, states: States):
	#print("step_to_saturation: " + node_info(root, states))

	if isinstance(root, Task):
		remaining_time = root.duration - states.executed_time[root]
		#print("step_to_saturation:Task:remaining_time: ", remaining_time)
		return remaining_time

	if isinstance(root, ExclusiveGateway):
		# print("step_to_saturation:Natural/Choice: " + node_info(root, states))
		# print("step_to_saturation:Natural/Choice:Left: " + node_info(root.sx_child, states))
		# print("step_to_saturation:Natural/Choice:Right: " + node_info(root.dx_child, states))

		if states.activityState[root.sx_child] == ActivityState.ACTIVE:
			return steps_to_saturation(root.sx_child, states)
		if states.activityState[root.dx_child] == ActivityState.ACTIVE:
			return steps_to_saturation(root.dx_child, states)

		remaining_time = 0
		if isinstance(root, Choice):
			remaining_time = root.max_delay - states.executed_time[root]
		# print("step_to_saturation:Natural/Choice:remaining_time: ", remaining_time)
		return remaining_time


	if isinstance(root, Sequential):
		#print("step_to_saturation:Sequential: " + node_info(root, states))
		#print("step_to_saturation:Sequential:Left: " + node_info(root.sx_child, states))
		#print("step_to_saturation:Sequential:Right: " + node_info(root.dx_child, states))

		# If the activity state of left child is in active mode (it means that the activity is currently ongoing)
		if states.activityState[root.dx_child] == ActivityState.ACTIVE:
			return steps_to_saturation(root.dx_child, states)
		else:
			return steps_to_saturation(root.sx_child, states)

	if isinstance(root, Parallel):
		#print("step_to_saturation:Parallel:  " + node_info(root, states))
		#print("step_to_saturation:Parallel:Left: " + node_info(root.sx_child, states))
		#print("step_to_saturation:Parallel:Right: " + node_info(root.dx_child, states))
		dur_left = math.inf
		dur_right = math.inf

		if states.activityState[root.sx_child] < ActivityState.COMPLETED:
			dur_left = steps_to_saturation(root.sx_child, states)
		if states.activityState[root.dx_child] < ActivityState.COMPLETED:
			dur_right = steps_to_saturation(root.dx_child, states)

		return min(dur_left, dur_right)

	raise Exception("step_to_saturation:invalid type", root)
