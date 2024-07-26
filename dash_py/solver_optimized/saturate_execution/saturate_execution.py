from solver.tree_lib import CTree, CNode
from solver_optimized.saturate_execution.create_branches import create_branches
from solver_optimized.saturate_execution.next_state import next_state
from solver_optimized.saturate_execution.states import States, ActivityState
from solver_optimized.saturate_execution.step_to_saturation import steps_to_saturation


def saturate_execution(region_tree: CTree, states: States) -> (States, tuple[CNode], dict[tuple[CNode], States]):
	branches = dict()
	choices_natures = tuple()

	while len(choices_natures) == 0 and states.activityState[region_tree.root] < ActivityState.COMPLETED:
		#print("step_to_saturation:")
		#print("start:", states_info(states))

		k = steps_to_saturation(region_tree, states)
		#print('step_to_saturation:k:', k, states_info(states))

		updatedStates, k = next_state(region_tree, states, k)
		states.update(updatedStates)

		#print('next_state:k:', k, states_info(states))
		if k > 0:
			Exception("StepsException" + str(k))

		choices_natures, branches = create_branches(states)

	#if len(branches) > 0:
	#	print("create_branches:", states_info(states))

	#print("Branches:" + str(len(branches)))
	#print("Root activity state: ", states.activityState[region_tree.root], states_info(states))

	return states, choices_natures, branches
