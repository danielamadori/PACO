import pandas as pd
from explainer.dag import Dag
from explainer.bdd import BDD


def explain_strategy(strategy, impacts_names):
	for choice in strategy:
		print(f"strategy[{choice}] {strategy[choice]}")
		impacts = []
		labels = []
		i = 0
		for decision in strategy[choice]:
			print(f"Choice {choice}, Decision {decision}: strategy[{choice}][{decision}] {strategy[choice][decision]}")
			for state in strategy[choice][decision]:
				print(f"\tState: {state}")
				impacts.append(state)
				labels.append(i)
			i += 1

		vector_size = len(impacts[0])
		print("Impacts:", impacts)
		print("Labels:", labels)
		print("Impacts size:", vector_size)

		df = pd.DataFrame(impacts, columns=impacts_names)
		df['class'] = labels

		dag = Dag(df)
		dag.explore(file_path="out/output")
		#print(dag.transitions_str())
		min_tree = BDD(dag)
		print(min_tree.build())
		min_tree.to_file("out/bdd_tree")
