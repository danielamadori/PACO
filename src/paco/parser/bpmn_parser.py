from lark import Lark
from paco.parser.grammar import sese_diagram_grammar
from paco.parser.parse_tree import ParseTree
from paco.parser.parse_node import Sequential, Parallel, Choice, Nature, Task
from utils.env import LOOP_PROB, TASK_SEQ, IMPACTS, NAMES, PROBABILITIES, DURATIONS, DELAYS, H, LOOP_ROUND

SESE_PARSER = Lark(sese_diagram_grammar, parser='lalr')
DEFAULT_UNFOLDING_NUMBER = 3


def create_parse_tree(bpmn: dict, from_json=False):
	if from_json:
		parse_tree = ParseTree.from_json()
	else:
		tree = SESE_PARSER.parse(bpmn[TASK_SEQ])
		#print(tree.pretty())
		root_parse_tree, last_id = parse(tree, bpmn[PROBABILITIES], bpmn[IMPACTS], bpmn[DURATIONS], bpmn[NAMES], bpmn[DELAYS], h=bpmn[H], loop_probability=bpmn[LOOP_PROB], loop_round=bpmn[LOOP_ROUND])
		parse_tree = ParseTree(root_parse_tree)
		parse_tree.to_json()

	parse_tree.print()

	return parse_tree


def parse(lark_tree, probabilities, impacts, durations, names, delays, loop_probability, loop_round, h = 0, parent = None, index_in_parent = 0, id = 0):
	if lark_tree.data == 'task':
		impact = impacts[lark_tree.children[0].value] if lark_tree.children[0].value in impacts else []
		task = Task(parent, index_in_parent, id, name=lark_tree.children[0].value, impact=impact[0:len(impact) - h], non_cumulative_impact=impact[len(impact) - h:], duration=durations[lark_tree.children[0].value])
		#print(f"Task: {task.name}, Impact: {task.impact}, Non-cumulative Impact: {task.non_cumulative_impact}, Duration: {task.duration}, ID: {id}")
		return task, id

	if lark_tree.data == 'loop_probability':
		loop_prob = loop_probability[lark_tree.children[0].value] if lark_tree.children[0].value in loop_probability else 0.5
		number_of_unfoldings = loop_round[lark_tree.children[0].value] if lark_tree.children[0].value in loop_round else DEFAULT_UNFOLDING_NUMBER
		num_of_regions_to_replicate = ((number_of_unfoldings - 1)*2) + 1
		# loops have only one child
		id -= 1
		children_list = []
		for dup in range(num_of_regions_to_replicate):
			child, last_id = parse(lark_tree.children[1], probabilities, impacts, durations, names, delays, loop_probability, loop_round, id=id + 1, h=h, parent=None, index_in_parent=0) #parent and index will be modified
			children_list.append(child.copy())
			id = last_id
		unfolded_tree, last_id = recursiveUnfoldingOfLoop(children_list, last_id, parent, index_in_parent, loop_prob, lark_tree.children[0].value, 1)
		return unfolded_tree, last_id

	if lark_tree.data in {'choice', 'natural'}:
		#Check if lark_tree.children[1].value works instead of names[lark_tree.children[1].value]
		name = names[lark_tree.children[1].value]

		if lark_tree.data == 'choice':
			if lark_tree.children[1].value not in delays.keys():
				raise ValueError(f"Delay for {lark_tree.children[1].value} not found in the delays dictionary")

			node = Choice(parent, index_in_parent, id, name, max_delay=delays[lark_tree.children[1].value])
			#print(f"Choice: {name}, Max Delay: {node.max_delay}, ID: {id}")

		else:#Natural
			if lark_tree.children[1].value not in probabilities:
				raise ValueError(f"Probability for {lark_tree.children[1].value} not found in the probabilities dictionary")

			node = Nature(parent, index_in_parent, id, name, probability=probabilities[lark_tree.children[1].value])
			#print(f"Nature: {name}, Probability: {node.probability}, ID: {id}")

		left_child, last_id = parse(lark_tree.children[0], probabilities, impacts, durations, names, delays, loop_probability, loop_round, id =id + 1, h=h, parent=node, index_in_parent=0)
		right_child, last_id = parse(lark_tree.children[2], probabilities, impacts, durations, names, delays, loop_probability, loop_round, id =last_id + 1, h=h, parent=node, index_in_parent=1)

	elif lark_tree.data in {'sequential', 'parallel'}:
		node = Sequential(parent, index_in_parent, id) if lark_tree.data == 'sequential' else Parallel(parent, index_in_parent, id)
		left_child, last_id = parse(lark_tree.children[0], probabilities, impacts, durations, names, delays, loop_probability, loop_round, id =id + 1, h=h, parent=node, index_in_parent=0)
		right_child, last_id = parse(lark_tree.children[1], probabilities, impacts, durations, names, delays, loop_probability, loop_round, id =last_id + 1, h=h, parent=node, index_in_parent=1)
		#print(f"{lark_tree.data.capitalize()}: ID: {id}")

	else:
		raise ValueError(f"Unhandled lark_tree type: {lark_tree.data}")

	node.set_children(left_child, right_child)
	return node, last_id


def recursiveUnfoldingOfLoop(children_list, id, parent, index_in_parent, loop_probability, nature_name:str, iteration:int):
	#recursive construction of the final unfolded tree
	if len(children_list) == 1:
		return children_list[0], id

	nat = Nature(parent, index_in_parent, id + 1, f"{nature_name}_{iteration}", probability=loop_probability)
	seq = Sequential(nat, 0, id + 2)
	last_id = id+2
	unfolded, last_id = recursiveUnfoldingOfLoop(children_list[2:], last_id, seq, 1, loop_probability, nature_name, iteration + 1)
	children_list[0].parent = seq
	children_list[0].index_in_parent = 0
	children_list[1].parent = nat
	children_list[1].index_in_parent = 1
	seq.set_children(children_list[0], unfolded)
	nat.set_children(seq, children_list[1])
	return nat, last_id
