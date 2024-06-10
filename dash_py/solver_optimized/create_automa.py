import time

from solver.tree_lib import print_sese_custom_tree
from solver_optimized.create_branches import create_branches
from solver_optimized.next_state import next_state
from solver_optimized.states import States, print_states, ActivityState
from solver_optimized.step_to_saturation import steps_to_saturation


def create_automa(region_tree, states):
	k = steps_to_saturation(region_tree, states)
	print('create_automa:k:', k)
	#print_states(states)

	states, k, cl = next_state(region_tree, states, k)
	print_states(states)
	print('create_automa:k:', k)
	print('create_automa:cl:', cl)

	if states.activityState[region_tree.root] == ActivityState.COMPLETED:
		print("Finished")
		return states


	print("Automate:")
	automates = []
	branches = create_branches(states)

	return create_automa(region_tree, branches[0])


	for branch in create_branches(states): # Could be parallelized
		print(f'create_automa:branches:')
		print_states(branch)

		time.sleep(60)

		automa = create_automa(region_tree, branch)


		automates.append(automa)



	return automates

	#print_sese_custom_tree(region_tree)

