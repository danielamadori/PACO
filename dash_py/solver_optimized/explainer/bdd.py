import os
import graphviz

from solver_optimized.explainer.dag import Dag
from solver_optimized.explainer.node import Node


class BDD:
	def __init__(self, dag: Dag):
		self.dag = dag

	def build(self):
		return self.build_bdd_recursively(self.dag.root)

	def build_bdd_recursively(self, node: Node):
		if not node.splittable:
			return f"Class: {list(node.df['class'])[0]}"
		if node.best_test is None:
			return "Undetermined"
		left_child, right_child = node.next_children(node.best_test)
		left_bdd = self.build_bdd_recursively(left_child)
		right_bdd = self.build_bdd_recursively(right_child)
		return f"({Node.test_str(node.best_test)} ? {left_bdd} : {right_bdd})"

	def bdd_to_dot(self, dot, node: Node):
		if not node.splittable:
			class_label = list(node.df['class'])[0]
			color = "lightblue" if class_label == 0 else "lightgreen"
			dot.node(str(node), label=f"Class: {class_label}", shape="box", style="filled", color=color)
		elif node.best_test is None:
			dot.node(str(node), label="Undetermined", shape="box", style="filled", color="red")
		else:
			dot.node(str(node), label=Node.test_str(node.best_test), shape="ellipse")

			left_child, right_child = node.next_children(node.best_test)
			dot.edge(str(node), self.bdd_to_dot(dot, left_child), label="True")
			dot.edge(str(node), self.bdd_to_dot(dot, right_child), label="False")

		return str(node)

	def to_file(self, file_path: str):
		dot = graphviz.Digraph()
		self.bdd_to_dot(dot, self.dag.root)
		dot.save(file_path + '.dot')
		dot.render(filename=file_path, format='svg')
		os.remove(file_path)# tmp file
