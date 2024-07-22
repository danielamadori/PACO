import copy
import numpy as np
from solver.tree_lib import CTree, CNode
from solver_optimized.create_branches import create_branches
from solver_optimized.next_state import next_state
from solver_optimized.solution_tree import SolutionNode, SolutionTree
from solver_optimized.states import States, states_info, ActivityState
from solver_optimized.step_to_saturation import steps_to_saturation


def tree_node_info(node: SolutionNode) -> str:
	result = "decisions:<"
	for n in node.decisions:
		result += str(n.id) + ";"

	result = result[:-1] + ">:choices_natures:<"
	tmp = ""
	for n in node.choices_natures:
		tmp += str(n.id) + ";"

	return result + tmp[:-1] + ">:status:" + states_info(node.states)


def saturate_solution_tree_node(region_tree: CTree, states: States) -> (States, tuple[CNode], dict[tuple[CNode], States]):
	branches = {}
	choices_natures = []

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


def create_tree(region_tree: CTree) -> (SolutionTree, list[SolutionTree]):
	states, choices_natures, branches = saturate_solution_tree_node(region_tree, States(region_tree.root, ActivityState.WAITING, 0))

	solution_tree = SolutionTree(SolutionNode(
		states=states,
		decisions=(region_tree.root,),
		choices_natures=choices_natures,
		is_final_state=states.activityState[region_tree.root] >= ActivityState.COMPLETED,
		parent=None)
	)

	print("create_tree:", tree_node_info(solution_tree.root))

	final_states = []
	for decisions, branch_states in branches.items():
		branch = copy.deepcopy(states)
		branch.update(branch_states)
		final_states.extend(create_tree_node(region_tree, decisions, branch, solution_tree))

	return solution_tree, final_states


def create_tree_node(region_tree: CTree, decisions: tuple[CNode], states: States, solution_tree: SolutionTree) -> list[SolutionTree]:
	saturatedStates, choices_natures, branches = saturate_solution_tree_node(region_tree, states)
	states.update(saturatedStates)

	is_final_state = states.activityState[region_tree.root] >= ActivityState.COMPLETED
	final_states = []
	next_node = SolutionTree(SolutionNode(
		states=states,
		decisions=decisions,
		choices_natures=choices_natures,
		is_final_state=is_final_state,
		parent=solution_tree)
	)

	print("create_tree_node:", tree_node_info(next_node.root))

	if is_final_state:
		final_states.append(next_node)

	solution_tree.root.add_child(next_node)

	for decisions, branch_states in branches.items():
		branch = copy.deepcopy(states)
		branch.update(branch_states)
		final_states.extend(create_tree_node(region_tree, decisions, branch, next_node))

	return final_states


def evaluate_cumulative_expected_impacts(solution_tree: SolutionTree):
	solution_tree.root.cei_top_down = solution_tree.root.probability * np.array(solution_tree.root.impacts)
	# solution_tree.root.cei_bottom_up = np.zeros(len(solution_tree.root.impacts))
	# Useless, already done in the constructor

	if solution_tree.root.is_final_state:
		solution_tree.root.cei_bottom_up = solution_tree.root.cei_top_down
		return

	for sub_tree in solution_tree.root.transitions.values():
		evaluate_cumulative_expected_impacts(sub_tree)
		solution_tree.root.cei_bottom_up += sub_tree.root.child.bottom_up


def evaluate_cumulative_expected_impacts2(solution_tree: SolutionTree):
	root = solution_tree.root
	root.cei_top_down = root.probability * np.array(root.impacts)
	# root.cei_bottom_up = np.zeros(len(root.impacts)) #Useless, already done in the constructor
	if root.is_final_state:
		root.cei_bottom_up += root.cei_top_down
		return

	onlyChoice = True
	choices_cei_bottom_up = {}
	for Transition, subTree in root.transitions.items():
		evaluate_cumulative_expected_impacts2(subTree)

		choices_transitions = []
		for t in Transition:
			if t[0].type == 'choice':
				onlyChoice = False
				choices_transitions.append(t)

		if onlyChoice:
			root.cei_bottom_up += subTree.root.cei_bottom_up
		else:
			choices_transitions = tuple(choices_transitions)
			if choices_transitions not in choices_cei_bottom_up:
				choices_cei_bottom_up[choices_transitions] = copy.deepcopy(subTree.root.cei_bottom_up)
				'''
				message = ""
				for t in range(len(choices_transitions)):
					message += str(choices_transitions[t][0].id) + "->" + str(choices_transitions[t][1].id) + ", "
				print(message[:-2] + " = " + str(result[choices_transitions]))
				'''
			else:
				'''
				message = ""
				for t in range(len(choices_transitions)):
					message += str(choices_transitions[t][0].id) + "->" + str(choices_transitions[t][1].id) + ", "
				print(message[:-2] + " = " + str(result[choices_transitions]) + " + " + str(subTree.root.cei_bottom_up))
				'''
				choices_cei_bottom_up[choices_transitions] += subTree.root.cei_bottom_up

	'''
	for Transition, subTree in root.transitions.items():
		print(subTree.root.cei_bottom_up)
	
	print("choices_cei_bottom_up:")
	for child, cei_bottom_up in choices_cei_bottom_up.items():
		message = ""
		for t in range(len(child)):
			message += str(child[t][0].id) + "->" + str(child[t][1].id) + ", "
		print(message[:-2] + " = " + str(cei_bottom_up))
	print("End")
	'''
	for c in choices_cei_bottom_up.keys():
		for i in range(len(root.impacts)):
			if root.cei_bottom_up[i] < choices_cei_bottom_up[c][i]:
				root.cei_bottom_up[i] = choices_cei_bottom_up[c][i]
