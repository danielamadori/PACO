import os
import graphviz

from explainer.dag import Dag
from explainer.node import Node


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
		left_child, right_child = node.get_targets(node.best_test)
		left_bdd = self.build_bdd_recursively(left_child)
		right_bdd = self.build_bdd_recursively(right_child)

		return f"({node.best_test[0]} < {node.best_test[1]} ? {left_bdd} : {right_bdd})"

	def bdd_to_dot(self, dot, node: Node):
		if not node.splittable:
			class_label = list(node.df['class'])[0]
			color = "lightblue" if class_label == 0 else "lightgreen"
			dot.node(str(node), label=f"Class: {class_label}", shape="box", style="filled", color=color)
		elif node.best_test is None:
			dot.node(str(node), label="Undetermined", shape="box", style="filled", color="red")
		else:
			dot.node(str(node), label=f"{node.best_test[0]} < {node.best_test[1]}", shape="ellipse")

			left_child, right_child = node.get_targets(node.best_test)
			dot.edge(str(node), self.bdd_to_dot(dot, left_child), label="True")
			dot.edge(str(node), self.bdd_to_dot(dot, right_child), label="False")

		return str(node)

	def to_file(self, file_path: str):
		dot = graphviz.Digraph()
		self.bdd_to_dot(dot, self.dag.root)
		dot.save(file_path + '.dot')
		dot.render(filename=file_path, format='svg')
		os.remove(file_path)# tmp file

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

min_tree = BDD(dag)
print(min_tree.build())
min_tree.to_file("out/bdd_tree")
'''