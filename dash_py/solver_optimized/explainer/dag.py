import os

import graphviz
import numpy as np
import pandas as pd
from solver_optimized.explainer.node import Node


class Dag:
	def __init__(self, df:pd.DataFrame):
		self.root = Node(df)
		self.nodes = {self.root}

	def __str__(self):
		result = "{"
		for node in self.nodes:
			result += str(node) + ", "

		return result[:-2] + "}"

	def transitions_str(self):
		result = ""
		for node in self.nodes:
			for target_node in node.edges:
				result += node.transition_str(target_node) + "\n"
		return result

	def get_splittable_leaves(self):
		return [node for node in self.nodes if len(node.edges) == 0 and node.splittable]

	@staticmethod
	def find_thresholds(df):
		thresholds = {}
		for c in df.columns:
			if c == 'class':
				continue
			l = sorted(set(df[c]))
			thresholds[c] = [(l[i+1] + l[i])/2 for i in range(len(l)-1)]
		return thresholds

	@staticmethod
	def generate_tests(df, t):
		unique_tests, seen_indices = [], []
		for feature, thresholds in t.items():
			#print(f"feature: {feature}, thresholds: {thresholds}")
			for threshold in thresholds:
				d1 = df[df[feature] < threshold] #d1 = df[df[feature]] < threshold
				d2 = df[df[feature] >= threshold] #d2 = df[df[feature]] >= threshold
				#print(f"df[k]: {df[feature]}, v: {threshold}, df[k]<v: {df[feature]<threshold}, d1: {d1}, d2: {d2}")

				if len(d1) > 0 and len(d2) > 0:
					if not any(d1.index.equals(seen) for seen in seen_indices):
						seen_indices.append(d1.index)
						unique_tests.append((feature, threshold, True, d1))
					if not any(d2.index.equals(seen) for seen in seen_indices):
						seen_indices.append(d2.index)
						unique_tests.append((feature, threshold, False, d2))

		return unique_tests

	def expand(self, node:Node):
		thresholds = Dag.find_thresholds(node.df)
		#print("thresholds:",  thresholds)
		for feature, threshold, lt, df in Dag.generate_tests(node.df, thresholds):
			#print(f"{Node.test_str((feature, threshold, lt))}, index: {index}")
			index = frozenset(df.index.to_list())
			target_node = None
			for n in self.nodes:
				if n.index == index:
					target_node = n
					break

			if target_node is None:
				target_node = Node(df)
				self.nodes.add(target_node)

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

	def search(self, node: Node):
		if not node.splittable:
			return
		if node.best_test is None:
			best_height = np.inf
			best_test = None

			for test, child in node.tests:
				for n in self.nodes:
					if n.index == child.index:
						height = node.best_height + 1
						if height < best_height:
							best_height = height
							best_test = test

			node.best_test = best_test
			node.best_height = best_height

			child_sx, child_dx = node.next_children(node.best_test)
			self.search(child_sx)
			self.search(child_dx)

	def run(self, file_path: str = None):
		print(self)
		i = 0
		while not self.step():
			i += 1
			print(f"step {i}\n", self)
			if file_path is not None:
				self.to_file(f'{file_path}{i}')

		self.search(self.root)
		self.to_file(f'{file_path}{i+1}', full=True)

	def to_file(self, file_path: str, full=False):
		dot = graphviz.Digraph()
		for node in self.nodes:
			# Prepare the label for the node, including best_test and best_height
			node_name = str(node)
			label = f"{node_name}"
			if full and node.best_test is not None:
				label += f"\nBest Test: {Node.test_str(node.best_test)}\nBest Height: {node.best_height}"

			if node.splittable:
				dot.node(node_name, label=label)
			else:
				dot.node(node_name, label=label, style='filled', fillcolor='green')

			for target_node, edge in node.edges.items():
				dot.edge(node_name, str(target_node), label=Node.edge_str(edge))

		dot.save(file_path + '.dot')
		dot.render(filename=file_path, format='svg')
		os.remove(file_path)  # tmp dot file