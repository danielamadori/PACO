import pydot
import json
from abc import ABC

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

	def to_json(self, filename:str = PATH_PARSE_TREE) -> None:
		dictionary = self.root.to_dict()
		open(filename + '.json', 'w').write(json.dumps(dictionary, indent=2))

	@staticmethod
	def create_node(node_data: dict, parent: 'ParseNode' = None, impact_size = -1, non_cumulative_impact = -1) -> 'ParseNode':
		node_type = node_data['type']
		node_id = node_data['id']
		index_in_parent = node_data.get('index_in_parent', -1)

		if node_type == "Task":
			new_impact_size = len(node_data['impact'])
			new_non_cumulative_impact = len(node_data['non_cumulative_impact'])

			if impact_size == -1:
				impact_size = new_impact_size
			elif impact_size != new_impact_size:
				raise ValueError(f"Task {node_id} has different impact size")
			if non_cumulative_impact == -1:
				non_cumulative_impact = new_non_cumulative_impact
			elif non_cumulative_impact != new_non_cumulative_impact:
				raise ValueError(f"Task {node_id} has different non_cumulative_impact size")

			node = Task(
				parent=parent,
				index_in_parent=index_in_parent,
				id=node_id,
				name=node_data['name'],
				impact=node_data['impact'],
				non_cumulative_impact=node_data['non_cumulative_impact'],
				duration=node_data['duration']
			)

		elif node_type == "Sequential":
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
		elif node_type == "Nature":
			node = Nature(
				parent=parent,
				index_in_parent=index_in_parent,
				id=node_id,
				name=node_data['name'],
				probability=node_data['probability']
			)
		else:
			raise ValueError(f"Unsupported node type: {node_type}")

		# Recursively create children if they exist
		if isinstance(node, Gateway):
			sx_child_data = node_data.get('sx_child')
			dx_child_data = node_data.get('dx_child')
			if sx_child_data:
				node.sx_child = ParseTree.create_node(sx_child_data, parent=node, impact_size=impact_size, non_cumulative_impact=non_cumulative_impact)
			if dx_child_data:
				node.dx_child = ParseTree.create_node(dx_child_data, parent=node, impact_size=impact_size, non_cumulative_impact=non_cumulative_impact)

		return node

	@staticmethod
	def from_json(filename: str = PATH_PARSE_TREE) -> 'ParseTree':
		return ParseTree(ParseTree.create_node(json.load(open(filename +'.json', 'r'))))
