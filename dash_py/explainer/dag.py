import math
import os
import graphviz
import pandas as pd

from explainer.dag_node import DagNode
from solver.tree_lib import CNode
from utils.env import PATH_EXPLAINER_DECISION_TREE


class Dag:
	def __init__(self, choice: CNode, class_0: CNode, class_1: CNode, impacts:list, impacts_label:list, impacts_names):
		self.choice = choice
		self.class_0 = class_0
		self.class_1 = class_1

		if class_1 is not None:
			df = pd.DataFrame(impacts, columns=impacts_names)
			df['class'] = impacts_label
			self.root = DagNode(df)
			self.nodes = {self.root}
		else:
			self.df = None
			self.root = None
			self.nodes = None

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
		while True:
			open_leaves = self.get_splittable_leaves()
			if len(open_leaves) == 0:
				break

			for node in open_leaves:
				self.expand(node)

			#print(f"step {i}\n", self)
			#print(self.transitions_str())
			if write:
				self.dag_to_file(f'{PATH_EXPLAINER_DECISION_TREE}_{str(self.choice.name)}_{i}')
			i += 1

			if len(open_leaves) <= len(self.get_splittable_leaves()):#Is not expanding (not separable)
				return False


		#print(f"computed tree: {i}\n", self)
		self.compute_tree(self.root)
		if write:
			self.dag_to_file(f'{PATH_EXPLAINER_DECISION_TREE}_{str(self.choice.name)}_{i}_final')

		return True

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

		dot.node(str(self.choice), label=f"{self.choice.name}, ID:{self.choice}", shape="box", style="filled", color="orange")
		if self.class_1 is not None:
			dot.edge(str(self.choice), str(self.root))
			self.bdd_to_file_recursively(dot, self.root)
		else:
			label, color = self.get_decision(self.class_0)
			node = str(self.class_0)
			dot.node(node, label=label, shape="box", style="filled", color=color)
			dot.edge(str(self.choice), node, label="True", style="dashed")

		file_path = PATH_EXPLAINER_DECISION_TREE + "_" + str(self.choice.name)
		dot.save(file_path + '.dot')
		dot.render(filename=file_path, format='svg')
		os.remove(file_path)# tmp file


	@staticmethod
	def get_decision(decision: CNode):
		if decision.type == 'nature' or decision.type == 'choice': #TODO loop (color for loops found in print_sese_diagram is 'yellow')
			color = 'orange'
		elif decision.type == 'parallel':
			color = 'yellowgreen'
		elif decision.type == 'task':
			color = 'lightblue'
		elif decision.type == 'sequential':
			return Dag.get_decision(decision.childrens[0].root)
		else:
			raise Exception(f"Decision type {decision.type} not recognized")

		return "ID:" + str(decision.id), color


	def bdd_to_file_recursively(self, dot, node: DagNode):
		if not node.splittable:
			label, color = Dag.get_decision(self.class_0 if list(node.df['class'])[0] == self.class_0.id else self.class_1)
			dot.node(str(node), label=label, shape="box", style="filled", color=color)
		elif node.best_test is None:
			dot.node(str(node), label="Undetermined", shape="box", style="filled", color="red")
		else:
			dot.node(str(node), label=f"{node.best_test[0]} < {node.best_test[1]}", shape="ellipse")

			left_child, right_child = node.get_targets(node.best_test)
			dot.edge(str(node), self.bdd_to_file_recursively(dot, left_child), label="True", style="dashed")
			dot.edge(str(node), self.bdd_to_file_recursively(dot, right_child), label="False")

		return str(node)

