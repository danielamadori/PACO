import copy
from itertools import product
from evaluations.evaluate_execution_path import evaluate_execution_path
from evaluations.evaluate_impacts import evaluate_expected_impacts, evaluate_unavoidable_impacts
from explainer.bdd import Bdd
from explainer.strategy_tree import StrategyTree, saturate_execution, StrategyViewPoint, tree_node_info
from explainer.strategy_type import TypeStrategy
from saturate_execution.states import States, ActivityState
from solver.tree_lib import CTree, CNode


def full_strategy(region_tree: CTree, typeStrategy: TypeStrategy, explainers: dict[CNode, Bdd], impacts_size: int,
				  states: States = None, decisions: tuple[CNode] = None, id: int = 0) -> (StrategyTree, int):
	if states is None:
		states = States(region_tree.root, ActivityState.WAITING, 0)
		decisions = (region_tree.root,)

	states, is_final, choices, natures = saturate_execution(region_tree, states)
	probability, impacts = evaluate_expected_impacts(states, impacts_size)

	strategyViewPoint = StrategyViewPoint(bpmn_root=region_tree.root, id=id, states=states,
										  decisions=decisions, choices=choices, natures=natures,
										  is_final_state=states.activityState[region_tree.root] >= ActivityState.COMPLETED,
										  impacts=impacts, probability=probability)

	strategyTree = StrategyTree(strategyViewPoint)
	print(tree_node_info(strategyViewPoint), f"Current impacts: {impacts}\n")


	if is_final:
		return strategyTree, id

	chosen_states: States = copy.deepcopy(states)
	next_decisions = []

	if len(choices) > 0:
		#print("typeStrategy: ", typeStrategy)
		if typeStrategy <= TypeStrategy.UNAVOIDABLE_IMPACTS:
			vector = impacts # Current impacts
			if typeStrategy == TypeStrategy.UNAVOIDABLE_IMPACTS:
				vector = evaluate_unavoidable_impacts(region_tree.root, states, vector)
				print("Unavoidable impacts: ", vector)
		elif typeStrategy == TypeStrategy.STATEFUL:
			vector = None
		else:
			raise Exception("TypeStrategy not implemented: " + str(typeStrategy))

		for choice in choices:
			if choice not in explainers:
				raise Exception("Choice not explained: " + str(choice))

			if vector is None: # Stateful
				all_nodes, vectors = evaluate_execution_path([states.activityState], explainers[choice].root.df.columns[:-1])
				vector = vectors[0]
				s = 'All decisions:\t   ['
				for n in all_nodes:
					s += str(n.id) + ' '
				print(s + "]")
				print("Stateful impacts: ", vector)

			print("Explaining choice: ", choice.id)

			decision_true = explainers[choice].choose(vector)
			next_decisions.append(decision_true)
			decision_false = choice.childrens[1].root if decision_true == choice.childrens[0].root else choice.childrens[0].root

			print("Decision True: ", decision_true.id)
			print("Decision False: ", decision_false.id)
			chosen_states.activityState[decision_true] = ActivityState.ACTIVE
			chosen_states.activityState[decision_false] = ActivityState.WILL_NOT_BE_EXECUTED

	branches = dict[tuple, States]()
	if len(natures) == 0:
		branches[tuple(next_decisions)] = chosen_states
	else:
		branches_decisions = list(product([True, False], repeat=len(natures)))
		#print(f"combinations:{branches_decisions}")
		for branch_choices in branches_decisions:
			branch_states = copy.deepcopy(chosen_states)
			branch_decisions = copy.deepcopy(next_decisions)

			for i in range(len(natures)):
				node = natures[i]

				if branch_choices[i]:
					activeNode = node.childrens[0].root
					inactiveNode = node.childrens[1].root
				else:
					activeNode = node.childrens[1].root
					inactiveNode = node.childrens[0].root

				branch_states.activityState[activeNode] = ActivityState.ACTIVE
				branch_states.activityState[inactiveNode] = ActivityState.WILL_NOT_BE_EXECUTED

				branch_decisions.append(activeNode)

			branches[tuple(branch_decisions)] = branch_states


	for next_decisions, branch_states in branches.items():
		sub_tree, id = full_strategy(region_tree, typeStrategy, explainers, impacts_size, branch_states, tuple(next_decisions), id + 1)
		strategyViewPoint.add_child(sub_tree)

	return strategyTree, id
