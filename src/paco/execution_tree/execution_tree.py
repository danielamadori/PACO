import json
import numpy as np
from jsonschema import validate, ValidationError
from graphviz import Source

from paco.execution_tree.execution_view_point import ExecutionViewPoint
from paco.explainer.bdd.bdd import Bdd
from paco.explainer.strategy_view_point import StrategyViewPoint
from paco.parser.parse_node import ParseNode, Sequential, Parallel
from paco.saturate_execution.states import States
from utils.env import PATH_EXECUTION_TREE


class ExecutionTree:
	def __init__(self, root: 'ExecutionViewPoint|StrategyViewPoint'):
		self.root = root

	def __str__(self) -> str:
		result = self.create_dot_graph(self.root, True, True, False)
		return result[0] + result[1]

	def to_dict(self) -> dict:
		root_type = self.root.__class__.__name__
		dictionary = {"type": root_type}
		dictionary.update(self.root.to_dict())
		return dictionary

	def state_str(self):
		return self.root.dot_str(state=True, executed_time=True, previous_node=None).split(' [')[0]

	def save_dot(self, path, state: bool = True, executed_time: bool = False, diff: bool = True):
		with open(path, 'w') as file:
			file.write(self.init_dot_graph(state=state, executed_time=executed_time, diff=diff))

	def save_pdf(self, path, state: bool = True, executed_time: bool = False, diff: bool = True):
		Source(self.init_dot_graph(state=state, executed_time=executed_time, diff=diff),
			   format='pdf').render(path, cleanup=True)

	def to_json(self) -> str:
		return json.dumps(self.to_dict(), indent=2)

	@staticmethod
	def create_tree(node_data: dict, tree_type:str, parseTree:'ParseTree', parseTreeNodes:dict, impacts_names:list, explained_choices:dict[ParseNode:Bdd]={}, parent = None) -> 'ExecutionTree':
		id = node_data['id']
		states = States.from_dict(node_data['states'], parseTreeNodes)
		decisions = tuple([parseTreeNodes[decision] for decision in node_data['decisions']])
		choices = tuple([parseTreeNodes[choice] for choice in node_data['choices']])
		pending_choices = set([parseTreeNodes[choice] for choice in node_data['pending_choices']])
		pending_natures = set([parseTreeNodes[nature] for nature in node_data['pending_natures']])
		natures = tuple([parseTreeNodes[nature] for nature in node_data['natures']])
		is_final_state = node_data['is_final_state']
		probability = np.float64(node_data['probability'])
		impacts = np.array(node_data['impacts'], dtype=np.float64)

		if tree_type == "ExecutionViewPoint":
			viewPoint = ExecutionViewPoint(
				id=id, states=states, decisions=decisions, choices=choices,
				natures=natures, is_final_state=is_final_state, parent=parent,
				probability=probability, impacts=impacts,
				cei_top_down=np.array(node_data['cei_top_down'], dtype=np.float64),
				cei_bottom_up=np.array(node_data['cei_bottom_up'], dtype=np.float64),
				pending_choices=pending_choices, pending_natures=pending_natures
			)

		elif tree_type == "StrategyViewPoint":
			viewPoint = StrategyViewPoint(bpmn_root=parseTree.root,
				id=id, states=states, decisions=decisions, choices=choices,
				natures=natures, is_final_state=is_final_state, parent=parent,
				probability=probability, impacts=impacts,
				expected_impacts=np.array(node_data['expected_impacts'], dtype=np.float64),
				expected_time=np.float64(node_data['expected_time']),
				pending_choices=pending_choices, pending_natures=pending_natures,
				explained_choices ={choice: bdd
									for choice, bdd in explained_choices.items() if choice in choices}
			)

		else:
			raise ValueError(f"Unsupported type: {tree_type}")

		tree = ExecutionTree(viewPoint)
		viewPoint.transitions = {}
		for key, transition_data in node_data.get("transitions", {}).items():
			viewPoint.add_child(
				ExecutionTree.create_tree(transition_data, tree_type, parseTree, parseTreeNodes, impacts_names, explained_choices, tree))

		return tree

	@staticmethod
	def from_json(parseTree: 'ParseTree', explained_choices:dict[ParseNode:Bdd], data, impacts_names: list) -> 'ExecutionTree':
		if isinstance(data, str):
			data = json.loads(data)
		#TODO validation
		#validate_json(data)
		parseTreeNodes = parseTree.root.to_dict_id_node()

		return ExecutionTree.create_tree(data, data['type'], parseTree, parseTreeNodes, impacts_names, explained_choices)



	def create_dot_graph(self, root: 'ExecutionViewPoint|StrategyViewPoint', state: bool, executed_time: bool, diff: bool,
						 previous_node: States = None):
		if not diff:# print all nodes
			previous_node = None

		nodes_id = root.dot_str(state=state, executed_time=executed_time, previous_node=previous_node)
		transitions_id = ""

		impact_id, impact_label = root.dot_info_str()
		transitions_id += f"{root.dot_str(full=False)} -> {impact_id} [label=\"\" color=red];\n"  #style=invis
		nodes_id += impact_id + impact_label

		for transition in root.transitions.keys():
			next_node = root.transitions[transition].root
			x = ""
			for t in transition:
				next = get_sequential_first_task(t[1])
				x += str(t[0].name) + '->' + str(next.id if (isinstance(next, Parallel) or isinstance(next, Sequential)) else next.name) + ';'
			#x += str(t[0].id) + '->' + str(t[1].id) + ';'
			#x += str(t)[1:-1].replace(',', '->') + ";"

			transitions_id += f"{root.dot_str(full=False)} -> {next_node.dot_str(full=False)} [label=\"{x[:-1]}\"];\n"

			ids = self.create_dot_graph(next_node, state=state, executed_time=executed_time, diff=diff,
										previous_node=root.states)
			nodes_id += ids[0]
			transitions_id += ids[1]

		return nodes_id, transitions_id


	def init_dot_graph(self, state: bool, executed_time: bool, diff: bool):
		result = "digraph automa {\n"

		node, transition = self.create_dot_graph(self.root, state=state, executed_time=executed_time,
												 diff=diff)

		result += node
		result += transition
		result += "__start0 [label=\"\", shape=none];\n"

		starting_node_names = ""
		for n in self.root.decisions:
			n = get_sequential_first_task(n)
			node_name = n.id if (isinstance(n, Parallel) or isinstance(n, Sequential)) else n.name
			starting_node_names += f"{node_name};"

		if len(self.root.choices) + len(self.root.natures) > 0:  #Just if we don't have decisions
			starting_node_names = starting_node_names[:-1] + "->"
			for c in self.root.choices:
				starting_node_names += f"{c.name if c.name else c.id};"
			for n in self.root.natures:
				starting_node_names += f"{n.name if n.name else n.id};"

		result += f"__start0 -> {self.root.dot_str(full=False)}  [label=\"{starting_node_names[:-1]}\"];\n" + "}"
		return result


def get_sequential_first_task(node: ParseNode):
	if isinstance(node, Sequential):
		return get_sequential_first_task(node.sx_child)

	return node


def validate_json(data: dict):
	schema = {
		"type": "object",
		"properties": {
			"id": {"type": "integer"},
			"type": {"type": "string", "enum": ["Task", "Sequential", "Parallel", "Choice", "Nature"]},
			"decisions": {"type": "array", "items": {"type": "integer"}},
			"transitions": {
				"type": "object",
				"additionalProperties": {"type": "object"}
			},
			"natures": {"type": "array", "items": {"type": "integer"}},
			"choices": {"type": "array", "items": {"type": "integer"}},
			"pending_natures": {"type": "array", "items": {"type": "integer"}},
			"pending_choices": {"type": "array", "items": {"type": "integer"}},
			"is_final_state": {"type": "boolean"}
		},
		"required": ["id", "type", "decisions", "transitions", "natures", "choices", "is_final_state"]
	}

	try:
		validate(instance=data, schema=schema)
	except ValidationError as e:
		raise ValueError(f"Validation error: {e.message}")

	for transition_key, transition_node in data.get("transitions", {}).items():
		if isinstance(transition_node, dict):
			validate_json(transition_node)

	return True
