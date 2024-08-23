import pandas as pd


class Node:
	# root ---- {('a', 2.5, True), ('b', 3.5, True)} ---->  index = {0,1,2}
	def __init__(self, df: pd.DataFrame):
		self.df = df
		self.index = frozenset(df.index.to_list())
		# edge: n --{(feature, threshold, lt),('a', 3.5, True)}--> n'
		self.edges = {}

		self.tests = []
		self.splittable = len(set(df['class'])) > 1
		self.best_test = None
		self.best_height = 0

	def __hash__(self):
		return hash(self.index)

	def __eq__(self, other):
		return self.index == other.index

	def __str__(self):
		return f"{set(self.index)}" # To print '{0, 1, 2}' instead of 'frozenset({0, 1, 2}'

	@staticmethod
	def test_str(test):
		feature, threshold, lt = test
		return f"{feature} {'<' if lt else '>='} {threshold}"

	@staticmethod
	def edge_str(edge: set):
		result = "{"
		for test in edge:
			result += Node.test_str(test) + ", "
		return result[:-2] + "}"

	def transition_str(self, target_node: 'Node', new_test=False):
		return f'{("*" if new_test else "")}{self} --{Node.edge_str(self.edges[target_node])}--> {target_node}'

	def add_node(self, target_node: 'Node', new_edge: tuple):
		self.tests.append((new_edge, target_node))
		edge = self.edges.get(target_node, None)#The edge is a test
		changed = False
		if edge is not None:
			edge.add(new_edge)
			changed = True
		else:
			edge = {new_edge}
		self.edges[target_node] = edge
		return changed

	def next_children(self, test):
		feature, threshold, lt = test
		child_sx, child_dx = None, None
		for target_node, edge in self.edges.items():
			if (feature, threshold) in [(f, t) for f, t, _ in edge]:
				if child_sx is None:
					child_sx = target_node
				else:
					child_dx = target_node
					return child_sx, child_dx

		raise ValueError("Not enough children found")
