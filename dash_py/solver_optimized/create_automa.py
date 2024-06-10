import time

from solver.tree_lib import print_sese_custom_tree
from solver_optimized.create_branches import create_branches
from solver_optimized.next_state import next_state
from solver_optimized.states import States, print_states, ActivityState
from solver_optimized.step_to_saturation import steps_to_saturation


def create_automa(region_tree, states, automa=[]):
	branches = []

	while len(branches) == 0:
		#print("step_to_saturation:")
		#print_states(states)
		k = steps_to_saturation(region_tree, states)
		#print('step_to_saturation:k:', k)
		#print_states(states)

		states, k, cl = next_state(region_tree, states, k)
		#print('next_state:k:', k)
		#print('next_state:cl:', cl)
		print_states(states)

		if states.activityState[region_tree.root] == ActivityState.COMPLETED:
			#print("Finished")
			#print_states(states)
			automa.append(states)
			return

		branches = create_branches(states)

	automa.append(states)
	for branch in branches:
		#print("Branch:")
		create_automa(region_tree, branch, automa)

	#print_sese_custom_tree(region_tree)
