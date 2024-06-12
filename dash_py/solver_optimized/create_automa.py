from solver.automaton_graph import AGraph, ANode
from solver.tree_lib import print_sese_custom_tree, CTree
from solver_optimized.create_branches import create_branches
from solver_optimized.next_state import next_state
from solver_optimized.states import States, print_states, ActivityState
from solver_optimized.step_to_saturation import steps_to_saturation


def create_automa(region_tree: CTree, states: States, automa: AGraph = None) -> AGraph:
	branches = []

	while len(branches) == 0 and states.activityState[region_tree.root] != ActivityState.COMPLETED:
		#print("step_to_saturation:")
		#print_states(states)
		k = steps_to_saturation(region_tree, states)
		#print('step_to_saturation:k:', k)
		#print_states(states)

		#print("next_state:")
		states, k, cl = next_state(region_tree, states, k)
		#print('next_state:k:', k)
		#print('next_state:cl:', cl)
		#print_states(states)

		branches = create_branches(states)

	#print_states(states)
	id = str(max([s.id for s in states.activityState.keys()])) + ";" + str(states)
	node = AGraph(ANode(id,
						is_final_state=states.activityState[region_tree.root] == ActivityState.COMPLETED))

	if automa == None:
		automa = node
	else:
		automa.init_node.add_transition(id, node)
	#automa.append(states)

	for branch in branches:
		#print("Branch:")
		automa = create_automa(region_tree, branch, automa)

	return automa
	#print_sese_custom_tree(region_tree)
	