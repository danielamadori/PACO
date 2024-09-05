import enum
import numpy as np
from explainer.dag import Dag
from explainer.strategy_type import current_impacts, unavoidable_impacts, stateful
from solver.tree_lib import CNode, CTree
from solver_optimized.execution_tree import ExecutionTree


class TypeStrategy(enum.IntEnum):
	CURRENT_IMPACTS = 0
	UNAVOIDABLE_IMPACTS = 1
	STATEFUL = 2

	def __str__(self):
		return str(self.value)


def explain_choice(choice:CNode, decisions:list[CNode], impacts:list[np.array], labels:list, features_names:list) -> Dag:
	decisions = list(decisions)
	decision_0 = decisions[0]
	decision_1 = None
	is_unavoidable_decision = len(decisions) == 1
	if not is_unavoidable_decision:
		decision_1 = decisions[1]

	dag = Dag(choice, decision_0, decision_1, impacts, labels, features_names)

	success = True
	if not is_unavoidable_decision:
		success = dag.build(write=True)
	if success:
		dag.bdd_to_file()
	else:
		dag = None

	return dag


def explain_strategy(region_tree: CTree, strategy: dict[CNode, dict[CNode, set[ExecutionTree]]], impacts_names: list[str], typeStrategy: TypeStrategy = TypeStrategy.CURRENT_IMPACTS) -> (TypeStrategy, dict[CNode, Dag]):
	bdds = dict[CNode, Dag]()
	for choice, decisions in strategy.items():
		print("Explaining: choice", choice)

		if typeStrategy == TypeStrategy.CURRENT_IMPACTS:
			print("Current impacts:")
			impacts, impacts_labels = current_impacts(decisions)
			for i in range(len(impacts)):
				print(f"I({impacts_labels[i]}): {impacts[i]}")

			bdd = explain_choice(choice, list(decisions.keys()), impacts, impacts_labels, impacts_names)
			if bdd is not None:
				bdds[choice] = bdd
				continue

			return explain_strategy(region_tree, strategy, impacts_names, TypeStrategy.UNAVOIDABLE_IMPACTS)

		elif typeStrategy == TypeStrategy.UNAVOIDABLE_IMPACTS:
			print("Unavoidable impacts:")
			unavoidableImpacts, unavoidableImpacts_labels = unavoidable_impacts(region_tree, decisions)
			for i in range(len(unavoidableImpacts)):
				print(f"I({unavoidableImpacts_labels[i]}): {unavoidableImpacts[i]}")

			bdd = explain_choice(choice, list(decisions.keys()), unavoidableImpacts, unavoidableImpacts_labels, impacts_names)

			if bdd is not None:
				bdds[choice] = bdd
				continue

			return explain_strategy(region_tree, strategy, impacts_names, TypeStrategy.STATEFUL)

		# if typeStrategy == TypeStrategy.STATEFUL:
		print("Stateful impacts")
		all_nodes, states_vectors, labels = stateful(decisions)
		bdd = explain_choice(choice, list(decisions.keys()), states_vectors, labels, all_nodes)

		if bdd is not None:
			bdds[choice] = bdd
		else:
			raise Exception("No explanation found")

	return typeStrategy, bdds
