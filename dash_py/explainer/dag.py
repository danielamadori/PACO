import math
import os
import graphviz
import pandas as pd
from explainer.dag_node import DagNode
from solver.tree_lib import CNode
from utils.env import PATH_EXPLAINER_DECISION_TREE


class Dag:
	def __init__(self, id: CNode, classes: list[CNode], df: pd.DataFrame):
		self.id = id
		self.class_true = classes[0]
		self.class_false = classes[1]
		self.root = DagNode(df)
		self.nodes = {self.root}

	def __str__(self):
		result = ""
		for node in self.nodes:
			result += str(node) + ", "
		return "{" + result[:-2] + "}"

	def transitions_str(self):
		result = ""
		for node in self.nodes:
			for target_node in node.edges:
				result += node.transition_str(target_node) + "\n"
		return result

	def get_splittable_leaves(self):
		return [node for node in self.nodes if len(node.edges) == 0 and node.splittable]

	@staticmethod
	def generate_test(df):
		thresholds = {}
		for c in df.columns:
			if c == 'class':
				continue
			l = sorted(set(df[c]))
			thresholds[c] = [(l[i+1] + l[i])/2 for i in range(len(l)-1)]
		return thresholds

	@staticmethod
	def generate_tests(df, t):
		tests = []
		for feature, thresholds in t.items():
			#print(f"feature: {feature}, thresholds: {thresholds}")
			for threshold in thresholds:
				d1 = df[df[feature] < threshold] #d1 = df[df[feature]] < threshold
				d2 = df[df[feature] >= threshold] #d2 = df[df[feature]] >= threshold
				#print(f"df[k]: {df[feature]}, v: {threshold}, df[k]<v: {df[feature]<threshold}, d1: {d1}, d2: {d2}")
				if len(d1) > 0 and len(d2) > 0:
					tests.append((feature, threshold, True, d1))
					tests.append((feature, threshold, False, d2))
		return tests

	def expand(self, node: DagNode):
		thresholds = self.generate_test(node.df)
		#print("thresholds:",  thresholds)
		for feature, threshold, lt, df in self.generate_tests(node.df, thresholds):
			#print(f"{Node.test_str((feature, threshold, lt))}, index: {index}")
			index = frozenset(sorted(df.index.to_list()))
			target_node = None
			distances_from_root = node.min_distances_from_root + 1
			for n in self.nodes:
				if n.index == index:
					target_node = n
					if target_node.min_distances_from_root > distances_from_root:
						target_node.min_distances_from_root = distances_from_root
					break

			if target_node is None:
				target_node = DagNode(df)
				self.nodes.add(target_node)
				target_node.min_distances_from_root = distances_from_root

			edge = (feature, threshold, lt)
			changed = node.add_node(target_node, edge)
		#print(node.transition_str(target_node, changed))

	def step(self):
		open_leaves = self.get_splittable_leaves()
		if len(open_leaves) == 0:
			return True
		for node in open_leaves:
			self.expand(node)
		return False

	def compute_tree(self, node: DagNode):
		if node.visited:
			return
		if len(node.edges) == 0: # is leaf
			node.best_height = 0
			node.visited = True
			return

		for child in node.edges.keys():
			self.compute_tree(child)
		for test in node.tests:
			target_t, target_f = node.get_targets(test)
			if (target_t.best_height < math.inf or target_f.best_height < math.inf) and len(node.edges) > 0: # is not leaf
				candidate_max_height = max(target_t.best_height, target_f.best_height) + 1
				if candidate_max_height < node.best_height:
					node.best_height = candidate_max_height
					node.best_test = test
			node.visited = True

	def explore(self, write=False):
		i = 1
		while not self.step():
			print(f"step {i}\n", self)
			#print(self.transitions_str())
			if write:
				self.dag_to_file(f'{PATH_EXPLAINER_DECISION_TREE}_{str(self.id)}_{i}')
			i += 1

		print(f"computed tree: {i}\n", self)
		self.compute_tree(self.root)
		if write:
			self.dag_to_file(f'{PATH_EXPLAINER_DECISION_TREE}_{str(self.id)}_{i}_final')

	def get_minimum_tree_nodes(self, node: DagNode):
		nodes = []
		if node.best_test is not None and len(node.edges) > 0: # is not leaf
			nodes.append(node)
			target_t, target_f = node.get_targets(node.best_test)
			nodes.extend(self.get_minimum_tree_nodes(target_t))
			nodes.extend(self.get_minimum_tree_nodes(target_f))
		return nodes

	def dag_to_file(self, file_path: str):
		dot = graphviz.Digraph()

		minimum_tree_nodes = self.get_minimum_tree_nodes(self.root)
		for node in self.nodes:
			node_name = str(node)
			label = f"{node_name}\nmin_delta(root): {node.min_distances_from_root}\nBest Height: {node.best_height}"

			color = 'white'
			if node.best_test is not None:
				label += f"\nTest: {node.best_test[0]} < {node.best_test[1]}\n"
			if node in minimum_tree_nodes:
				color = 'lightblue'
			elif not node.splittable:
				color = 'green'

			dot.node(node_name, label=label, style='filled', fillcolor=color)

			for target_node, edge in node.edges.items():
				dot.edge(node_name, str(target_node), label=DagNode.edge_str(edge))

		dot.save(file_path + '.dot')
		dot.render(filename=file_path, format='svg')
		os.remove(file_path)  # tmp dot file

	def get_bdd(self):
		return self.get_bdd_recursively(self.root)

	def get_bdd_recursively(self, node: DagNode):
		if not node.splittable:
			return f"Class: {list(node.df['class'])[0]}"
		if node.best_test is None:
			return "Undetermined"
		left_child, right_child = node.get_targets(node.best_test)
		left_bdd = self.get_bdd_recursively(left_child)
		right_bdd = self.get_bdd_recursively(right_child)

		return f"({node.best_test[0]} < {node.best_test[1]} ? {left_bdd} : {right_bdd})"

	def bdd_to_file(self):
		dot = graphviz.Digraph()

		node_name = "root_" + str(self.root)
		dot.node(node_name, label=f"{self.id.name}, ID:{self.id.id}", shape="box", style="filled", color="orange")
		dot.edge(node_name, str(self.root))

		self.bdd_to_file_recursively(dot, self.root)
		file_path = PATH_EXPLAINER_DECISION_TREE + str(self.id)
		dot.save(file_path + '.dot')
		dot.render(filename=file_path, format='svg')
		os.remove(file_path)# tmp file

	def bdd_to_file_recursively(self, dot, node: DagNode):
		if not node.splittable:
			class_, color = self.class_true, "lightblue"
			if list(node.df['class'])[0] == self.class_false.id:
				class_, color = self.class_false, "lightgreen"
			dot.node(str(node), label=f"{class_.name}, ID:{class_.id}", shape="box", style="filled", color=color)
		elif node.best_test is None:
			dot.node(str(node), label="Undetermined", shape="box", style="filled", color="red")
		else:
			dot.node(str(node), label=f"{node.best_test[0]} < {node.best_test[1]}", shape="ellipse")

			left_child, right_child = node.get_targets(node.best_test)
			dot.edge(str(node), self.bdd_to_file_recursively(dot, left_child), label="True")
			dot.edge(str(node), self.bdd_to_file_recursively(dot, right_child), label="False")

		return str(node)

'''
X = [
	[0,1,3,4,5,2,3],
	[1,2,3,4,5,6,7],
	[2,3,4,5,6,7,8],
	[3,4,5,6,7,8,9],
	[4,5,6,7,8,9,10],
]
Y = [0,1,0,1,1]

def create_df(X,Y):
	df = pd.DataFrame(X, columns=['a','b','c','d','e','f','g'])
	df['class'] = Y
	return df


dag = Dag(create_df(X,Y))
dag.explore(file_path="out/output")
#print(dag.transitions_str())
'''