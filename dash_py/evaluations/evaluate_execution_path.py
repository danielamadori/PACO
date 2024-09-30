import numpy as np
from saturate_execution.states import ActivityState
from solver.tree_lib import CNode


def evaluate_execution_path(all_states: list[ActivityState], all_nodes = set()):
	#if all_nodes is empty, we need to get all nodes
	if len(all_nodes) == 0:
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
				#print(f"Node ID:{str(all_nodes[i].id)} not in states")
				propagate_status(all_nodes[i], states)
			vector_states[i] = states[all_nodes[i]]

		vectors_states.append(vector_states)

	return all_nodes, vectors_states


def propagate_status(node: CNode, states: ActivityState):
	#print("ID: " + str(node.id))
	if node in states:
		#print("propagate status: " + str(states[node]))
		return states[node]

	if node.parent is None:
		raise Exception("Node without parent")

	states[node] = propagate_status(node.parent, states)

	return states[node]
