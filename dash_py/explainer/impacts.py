import copy
import numpy as np
from saturate_execution.states import States, ActivityState, node_info, states_info
from solver.tree_lib import CNode, CTree
from solver_optimized.execution_tree import ExecutionTree


def current_impacts(decisions: dict[CNode, set[ExecutionTree]]) -> (list, list):
	impacts, impacts_labels = [], []
	for decision, executionTrees in decisions.items():
		for executionTree in executionTrees:
			impacts.append(copy.deepcopy(executionTree.root.impacts))
			impacts_labels.append(decision.id)

	return impacts, impacts_labels

def unavoidable_tasks(root: CNode, states: States) -> set[CNode]:
	#print("root " + node_info(root, states))
	if root in states.activityState and states.activityState[root] in [ActivityState.WILL_NOT_BE_EXECUTED, ActivityState.COMPLETED, ActivityState.COMPLETED_WIHTOUT_PASSING_OVER]:
		#print("general node with: -1, 2, 3")
		return set()
	if root.type == 'task':
		if root not in states.activityState or (root in states.activityState and states.activityState[root] == ActivityState.WAITING):
			return set([root])
		return set()
	if root.type in ['sequential', 'parallel']:
		result = set[CNode]()
		for child in root.childrens:
			result = result.union(unavoidable_tasks(child.root, states))
		return result

	if root.type in ['choice', 'natural'] and root in states.activityState and states.activityState[root] == ActivityState.ACTIVE:
		for child in root.childrens:
			if child.root in states.activityState and states.activityState[child.root] == ActivityState.ACTIVE:
				return unavoidable_tasks(child.root, states)

	return set()

def unavoidable_impacts(region_tree: CTree, decisions: dict[CNode, set[ExecutionTree]]) -> (list, list):
	impacts, impacts_labels = [], []
	for decision, executionTrees in decisions.items():
		for executionTree in executionTrees:
			unavoidableImpacts = copy.deepcopy(executionTree.root.impacts)
			#print("Unavoidable:\n" + states_info(executionTree.root.states))
			for unavoidableTask in unavoidable_tasks(region_tree.root, executionTree.root.states):
				#print("unavoidableTask " + node_info(unavoidableTask, executionTree.root.states))
				unavoidableImpacts += np.array(unavoidableTask.impact)

			impacts.append(unavoidableImpacts)
			impacts_labels.append(decision.id)

	return impacts, impacts_labels


def propagate_status(node: CNode, states: States):
	print("ID: " + str(node.id))
	if node in states:
		print("propagate status: " + str(states[node]))
		return states[node]

	if node.parent is None:
		raise Exception("Node without parent")

	states[node] = propagate_status(node.parent, states)

	return states[node]


def get_full_states(all_states: list[dict[CNode, ActivityState]]):
	all_nodes = set()
	for states in all_states:
		nodes = set()
		for node in states.keys():
			if node.parent is not None and (node.parent.type == 'choice' or node.parent.type == 'natural'):
				nodes.add(node)
		all_nodes.update(nodes)

	all_nodes = sorted(all_nodes)

	vectors_states = []
	vector_size = len(all_nodes)
	for states in all_states:
		vector_states = np.zeros(vector_size, dtype='int')
		for i in range(vector_size):
			if all_nodes[i] not in states:
				print(f"Node ID:{str(all_nodes[i].id)} not in states")
				propagate_status(all_nodes[i], states)
			vector_states[i] = states[all_nodes[i]]

		vectors_states.append(vector_states)

	return all_nodes, vectors_states


def stateful(decisions: dict[CNode, set[ExecutionTree]]):
	states_vectors, labels = [], []
	for decision, executionTrees in decisions.items():
		for executionTree in executionTrees:
			states_vectors.append(executionTree.root.states.activityState)
			labels.append(decision.id)

	all_nodes, states_vectors = get_full_states(states_vectors)
	#print each state_vector with the corresponding label
	s = ''
	for node in all_nodes:
		s += str(node.id) + ', '
	print("\t\t  ID: ", s [:-2])
	for i in range(len(states_vectors)):
		print(f"State vector: {states_vectors[i]}, label: {labels[i]}")

	return all_nodes, states_vectors, labels
