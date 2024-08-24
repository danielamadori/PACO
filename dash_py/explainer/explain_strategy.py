import pandas as pd
from explainer.dag import Dag


def explain_strategy(strategy, impacts_names):
	for choice in strategy:
		s = f"Strategy for Choice: {choice}:"

		impacts = []
		decision_labels = []
		decisions = []
		for decision in strategy[choice]:
			s += f"\n\tDecision {decision}: {strategy[choice][decision]}"
			decisions.append(decision)
			for state in strategy[choice][decision]:
				impacts.append(state)
				decision_labels.append(decision.id)
		print(s)

		if len(strategy[choice]) == 1:
			print(f"\tNo choice in this case")
			continue
			# TODO ask how to manage this case

		#print("Impacts:", impacts)
		#print("Labels:", decision_labels)
		#print("Impacts size:", vector_size)

		df = pd.DataFrame(impacts, columns=impacts_names)
		df['class'] = decision_labels

		dag = Dag(id=choice, classes=decisions, df=df)
		dag.explore(write=True)
		dag.bdd_to_file()
