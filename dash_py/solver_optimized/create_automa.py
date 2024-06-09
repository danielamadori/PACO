import time

from solver.tree_lib import print_sese_custom_tree
from solver_optimized.create_branches import create_branches
from solver_optimized.next_state import next_state
from solver_optimized.states import States, print_states
from solver_optimized.step_to_saturation import steps_to_saturation


def create_automa(region_tree, states):
	cl = False

	while cl == False:
		k = steps_to_saturation(region_tree, states)
		print('create_automa:k:', k)
		#print_states(states)

		states, k, cl = next_state(region_tree, states, k)
		print_states(states)
		print('create_automa:k:', k)
		print('create_automa:cl:', cl)
		#time.sleep(60)

	print("Automate:")
	automates = []

	for branch in create_branches(states): # Could be parallelized
		print(f'create_automa:branches:')
		print_states(branch)

		automa = create_automa(region_tree, branch)
		time.sleep(60)

		automates.append(automa)

		#automates += create_automa(region_tree, branch)
		#return create_automa(region_tree, branches)
		'''
		if(len(branches.) > 0):
			automa = create_automa(region_tree, branches)
			if len(automa) > 0:
				automates.append(automa)
		'''

	# Sleep 60 seconds to avoid the "Too many requests" error
	#time.sleep(60)

	return automates

	#print_sese_custom_tree(region_tree)
