from abc import ABC, abstractmethod
import numpy as np


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

	@abstractmethod
	def to_dict(self) -> dict:
		return {"id": self.id, "type": self.__class__.__name__}

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

	def to_dict(self) -> dict:
		base = super().to_dict()
		base.update({
			"sx_child": self.sx_child.to_dict() if self.sx_child else None,
			"dx_child": self.dx_child.to_dict() if self.dx_child else None,
		})
		return base


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

	@abstractmethod
	def to_dict(self) -> dict:
		base = super().to_dict()
		base.update({"name": self.name})
		return base


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

	def to_dict(self) -> dict:
		base = super().to_dict()
		base.update({"max_delay": self.max_delay})
		return base


class Nature(ExclusiveGateway):
	def __init__(self, parent:Gateway, index_in_parent:int, id:int, name:str, probability:float) -> None:
		super().__init__(parent, index_in_parent, id, name)
		self.probability = np.float64(probability) #of the sx_child

	def dot(self):
		return f'\n node_{self.id}[shape=diamond label="{self.name} id:{self.id}" style="filled" fillcolor=yellowgreen];'

	def copy(self) -> 'Nature':
		root_copy = Nature(self.parent.copy(), self.index_in_parent, self.id, self.name, self.probability)
		root_copy.set_children(self.root.sx_child.copy(), self.root.dx_child.copy())
		return root_copy

	def to_dict(self) -> dict:
		base = super().to_dict()
		base.update({"probability": self.probability})
		return base


class Task(ParseNode):
	def __init__(self, parent:'Gateway', index_in_parent:int, id:int, name:str, impact:list, non_cumulative_impact:list, duration:int) -> None:
		super().__init__(parent, index_in_parent, id)
		self.name = name
		self.impact = np.array(impact, dtype=np.float64)
		self.non_cumulative_impact = np.array(non_cumulative_impact, dtype=np.float64)
		self.duration = duration

	def dot(self):
		return f'\n node_{self.id}[label="{self.name}\n{self.impact}\ndur:{self.duration} id:{self.id}" shape=rectangle style="rounded, filled" fillcolor=lightblue];'

	def copy(self) -> 'Task':
		return Task(self.parent.copy(), self.index_in_parent, self.id, self.name, self.impact.copy(), self.non_cumulative_impact.copy(), self.duration)

	def to_dict(self) -> dict:
		base = super().to_dict()
		base.update({
			"name": self.name,
			"impact": self.impact.tolist(),
			"non_cumulative_impact": self.non_cumulative_impact.tolist(),
			"duration": self.duration,
		})
		return base
