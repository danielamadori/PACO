import pydot
from utils.env import PATH_PARSE_TREE
from abc import ABC, abstractmethod

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

class ParseNode(ABC):
	# types = ['task', 'sequential', 'parallel', 'natural', 'choice', 'loop', 'loop_probability']
	def __init__(self, parent, index_in_parent, id:int) -> None:
		self.id = id
		self.parent = parent
		self.index_in_parent = index_in_parent

	@abstractmethod
	def dot(self):
		pass

	@abstractmethod
	def copy(self) -> 'ParseNode(ABC)':
		pass

	def __eq__(self, other: 'ParseNode(ABC)') -> bool:
		if isinstance(other, Task) or isinstance(other, Sequential) or isinstance(other, Parallel) or isinstance(other, Nature) or isinstance(other, Choice):
			return self.id == other.id
		return False

	def __lt__(self, other: 'ParseNode(ABC)') -> bool:
		if isinstance(other, Task) or isinstance(other, Sequential) or isinstance(other, Parallel) or isinstance(other, Nature) or isinstance(other, Choice):
			return self.id < other.id
		return False

	def __hash__(self):
		return hash(self.id)

	def __str__(self) -> str:
		return str(self.id)


class Gateway(ParseNode, ABC):
	def __init__(self, parent:'Gateway', index_in_parent:int, id:int) -> None:
		super().__init__(parent, index_in_parent, id)
		self.sx_child = None
		self.dx_child = None

	def set_children(self, sx_child:ParseNode, dx_child:ParseNode) -> None:
		self.sx_child = sx_child
		self.dx_child = dx_child


class Sequential(Gateway):
	def __init__(self, parent:Gateway, index_in_parent:int, id:int) -> None:
		super().__init__(parent, index_in_parent, id)

	def dot(self):
		return f'\n node_{self.id}[label="Sequential id: {self.id}"];'

	def copy(self) -> 'Sequential':
		root_copy = Sequential(self.parent.copy(), self.index_in_parent, self.id)
		root_copy.set_children(self.root.sx_child.copy(), self.root.dx_child.copy())
		return root_copy


class Parallel(Gateway):
	def __init__(self, parent:Gateway, index_in_parent:int, id:int) -> None:
		super().__init__(parent, index_in_parent, id)

	def dot(self):
		return f'\n node_{self.id}[shape=diamond label="Parallel id:{self.id}"];'

	def copy(self) -> 'Parallel':
		root_copy = Parallel(self.parent.copy(), self.index_in_parent, self.id)
		root_copy.set_children(self.root.sx_child.copy(), self.root.dx_child.copy())
		return root_copy


class ExclusiveGateway(Gateway, ABC):
	def __init__(self, parent:Gateway, index_in_parent:int, id:int, name:str) -> None:
		super().__init__(parent, index_in_parent, id)
		self.name = name


class Choice(ExclusiveGateway):
	def __init__(self, parent:Gateway, index_in_parent:int, id:int, name:str, max_delay:int) -> None:
		super().__init__(parent, index_in_parent, id, name)
		self.max_delay = max_delay

	def dot(self):
		return f'\n node_{self.id}[shape=diamond label="{self.name} id:{self.id} dly:{self.max_delay}" style="filled" fillcolor=orange];'

	def copy(self) -> 'Choice':
		root_copy = Choice(self.parent.copy(), self.index_in_parent, self.id, self.name, self.max_delay)
		root_copy.set_children(self.root.sx_child.copy(), self.root.dx_child.copy())
		return root_copy


class Nature(ExclusiveGateway):
	def __init__(self, parent:Gateway, index_in_parent:int, id:int, name:str, probability:float) -> None:
		super().__init__(parent, index_in_parent, id, name)
		self.probability = probability #of the sx_child

	def dot(self):
		return f'\n node_{self.id}[shape=diamond label="{self.name} id:{self.id}" style="filled" fillcolor=yellowgreen];'

	def copy(self) -> 'Nature':
		root_copy = Nature(self.parent.copy(), self.index_in_parent, self.id, self.name, self.probability)
		root_copy.set_children(self.root.sx_child.copy(), self.root.dx_child.copy())
		return root_copy


class Task(ParseNode):
	def __init__(self, parent:'Gateway', index_in_parent:int, id:int, name:str, impact:list, non_cumulative_impact:list, duration:int) -> None:
		super().__init__(parent, index_in_parent, id)
		self.name = name
		self.impact = impact
		self.non_cumulative_impact = non_cumulative_impact
		self.duration = duration

	def dot(self):
		return f'\n node_{self.id}[label="{self.name}\n{self.impact}\ndur:{self.duration} id:{self.id}" shape=rectangle style="rounded, filled" fillcolor=lightblue];'

	def copy(self) -> 'Task':
		return Task(self.parent.copy(), self.index_in_parent, self.id, self.name, self.impact.copy(), self.non_cumulative_impact.copy(), self.duration)


def print_parse_tree(tree, outfile=PATH_PARSE_TREE):
	tree = tree.dot_tree()
	dot_string = "digraph my_graph{"+ tree +"}"
	graph = pydot.graph_from_dot_data(dot_string)[0]
	graph.write_svg(outfile + '.svg')
	#graph.write_png(outfile)