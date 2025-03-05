import pydot
import json
from abc import ABC

from paco.parser.json_schema.json_validator import validate_json
from paco.parser.parse_node import Gateway, Sequential, Parallel, Choice, Nature, Task
from utils.env import PATH_PARSE_TREE

class ParseTree:
	def __init__(self, root: 'ParseNode(ABC)') -> None:
		self.root = root

	def copy(self) -> 'ParseTree':
		return ParseTree(self.root.copy())

	def dot_tree(self, root: 'ParseNode(ABC)' = None):
		if root is None:
			root = self.root

		if isinstance(root, Task):
			return root.dot()

		dot_code = self.dot_tree(root.sx_child)
		dot_code += self.dot_tree(root.dx_child)
		dot_code += root.dot()

		sx_edge_label = ''
		dx_edge_label = ''
		if isinstance(root, Nature):
			sx_edge_label = f'{root.probability}'
			dx_edge_label = f'{round((1 - root.probability), 2)}'

		dot_code += f'\n node_{root.id} -> node_{root.sx_child.id} [label="{sx_edge_label}"];'
		dot_code += f'\n node_{root.id} -> node_{root.dx_child.id} [label="{dx_edge_label}"];'

		return dot_code

	def print(self, outfile=PATH_PARSE_TREE):
		dot_string = "digraph my_graph{"+ self.dot_tree() +"}"
		graph = pydot.graph_from_dot_data(dot_string)[0]
		graph.write_svg(outfile + '.svg')
		#graph.write_png(outfile)

	def to_json(self) -> str:
		return json.dumps(self.root.to_dict(), indent=2)

	def to_dict(self) -> dict:
		return self.root.to_dict()

	def to_dict_id_node(self) -> dict:
		return self.root.to_dict_id_node()

	@staticmethod
	def create_node(node_data: dict, parent: 'ParseNode' = None, impact_size = -1, non_cumulative_impact = -1) -> 'ParseNode':
		node_type = node_data['type']
		node_id = node_data['id']
		index_in_parent = node_data.get('index_in_parent', -1)
		pending_choice, pending_natures = set(), set()

		if node_type == "Task":
			return Task(
				parent=parent,
				index_in_parent=index_in_parent,
				id=node_id,
				name=node_data['name'],
				impact=node_data['impact'],
				non_cumulative_impact=node_data['non_cumulative_impact'],
				duration=node_data['duration']
			), pending_choice, pending_natures

		if node_type == "Sequential":
			node = Sequential(parent=parent, index_in_parent=index_in_parent, id=node_id)
		elif node_type == "Parallel":
			node = Parallel(parent=parent, index_in_parent=index_in_parent, id=node_id)
		elif node_type == "Choice":
			node = Choice(
				parent=parent,
				index_in_parent=index_in_parent,
				id=node_id,
				name=node_data['name'],
				max_delay=node_data['max_delay']
			)
			pending_choice.add(node)
		elif node_type == "Nature":
			node = Nature(
				parent=parent,
				index_in_parent=index_in_parent,
				id=node_id,
				name=node_data['name'],
				probability=node_data['probability']
			)
			pending_natures.add(node)
		else:
			raise ValueError(f"Unsupported node type: {node_type}")

		# Recursively create children if they exist
		if isinstance(node, Gateway):
			sx_child_data = node_data.get('sx_child')
			dx_child_data = node_data.get('dx_child')

			if sx_child_data:
				node.sx_child, sx_pending_choice, sx_pending_natures = ParseTree.create_node(sx_child_data, parent=node, impact_size=impact_size, non_cumulative_impact=non_cumulative_impact)
				pending_choice.update(sx_pending_choice)
				pending_natures.update(sx_pending_natures)
			if dx_child_data:
				node.dx_child, dx_pending_choice, dx_pending_natures = ParseTree.create_node(dx_child_data, parent=node, impact_size=impact_size, non_cumulative_impact=non_cumulative_impact)
				pending_natures.update(dx_pending_natures)
				pending_choice.update(dx_pending_choice)

		return node, pending_choice, pending_natures

	@staticmethod
	def from_json(data, impact_size: int = -1, non_cumulative_impact_size: int = -1) -> 'ParseTree':
		if isinstance(data, str):
			data = json.loads(data)

		validate_json(data, impact_size, non_cumulative_impact_size)
		root, pending_choice, pending_natures = ParseTree.create_node(data)
		return ParseTree(root), pending_choice, pending_natures
