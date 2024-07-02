from solver.tree_lib import CTree
from solver_optimized.create_branches import create_branches
from solver_optimized.next_state import next_state
from solver_optimized.states import States, ActivityState
from solver_optimized.step_to_saturation import steps_to_saturation


def create_automa_state(region_tree: CTree, states: States):
	branches = {}

	while len(branches) == 0 and states.activityState[region_tree.root] < ActivityState.COMPLETED:
		#print("step_to_saturation:")
		#print("start:", states_info(states))

		k = steps_to_saturation(region_tree, states)
		#print('step_to_saturation:k:', k, states_info(states))

		updatedStates, k = next_state(region_tree, states, k)
		states.update(updatedStates)

		#print('next_state:k:', k, states_info(states))
		if k > 0:
			Exception("StepsException" + str(k))

		branches = create_branches(states)
	#if len(branches) > 0:
	#	print("create_branches:", states_info(states))


	#print("Branches:" + str(len(branches)))
	#print("Root activity state: ", states.activityState[region_tree.root], states_info(states))

	return branches, states

