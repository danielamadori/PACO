import copy
import random
from itertools import product

from evaluations.evaluate_execution_path import find_all_decisions, evaluate_execution_path
from evaluations.evaluate_impacts import evaluate_expected_impacts, evaluate_unavoidable_impacts
from explainer.bdd import Bdd
from explainer.strategy_tree import StrategyTree, saturate_execution, StrategyViewPoint, tree_node_info
from explainer.strategy_type import TypeStrategy, decision_based
from saturate_execution.states import States, ActivityState
from parser.tree_lib import CTree, CNode


def full_strategy(region_tree: CTree, typeStrategy: TypeStrategy, explainers: dict[CNode, Bdd], impacts_size: int,
				  states: States = None, decisions_taken: tuple[CNode] = None, id: int = 0) -> (StrategyTree, int):
	if states is None:
		states = States(region_tree.root, ActivityState.WAITING, 0)
		decisions_taken = (region_tree.root,)

	states, is_final, choices, natures = saturate_execution(region_tree, states)
	probability, impacts = evaluate_expected_impacts(states, impacts_size)

	strategyViewPoint = StrategyViewPoint(bpmn_root=region_tree.root, id=id, states=states,
										  decisions=decisions_taken,
										  choices={choice: None for choice in choices},  # Each choice is a key and the value is the bdd,
										  natures=natures, is_final_state=is_final,
										  impacts=impacts, probability=probability)

	strategyTree = StrategyTree(strategyViewPoint)
	print(tree_node_info(strategyViewPoint), f"Impacts: {impacts}\n")


	if is_final:
		return strategyTree, id

	chosen_states: States = copy.deepcopy(states)
	next_decisions = []

	if len(strategyViewPoint.choices) > 0:
		print("typeStrategy: ", typeStrategy)
		if typeStrategy <= TypeStrategy.UNAVOIDABLE_IMPACTS:
			vector = impacts # Current impacts
			if typeStrategy == TypeStrategy.UNAVOIDABLE_IMPACTS:
				vector = evaluate_unavoidable_impacts(region_tree.root, states, vector)
				print("Unavoidable impacts: ", vector)
		elif typeStrategy == TypeStrategy.DECISION_BASED:
			decisions, decisions_names = find_all_decisions(region_tree)
			vector, label = evaluate_execution_path(decisions, strategyViewPoint.states.activityState)
			print("Decisions:", decisions_names)
			print(f"{label}: {vector}")
		else:
			raise Exception("TypeStrategy not implemented: " + str(typeStrategy))

		for choice in strategyViewPoint.choices.keys():
			arbitrary = choice not in explainers

			if arbitrary:
				print(f"Choice not explained: {str(choice)}, random decision")
				random.seed()
				random_decision = random.choice([0, 1])
				opposite_decision = 1 - random_decision

				decision_true = choice.children[random_decision].root
				decision_false = choice.children[opposite_decision].root
			else:
				print("Explaining choice: ", choice.name)
				bdd = explainers[choice]
				strategyViewPoint.choices[choice] = bdd

				decision_true = bdd.choose(vector)
				decision_false = choice.children[1].root if decision_true == choice.children[0].root else choice.children[0].root

			next_decisions.append(decision_true)
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
					activeNode = node.children[0].root
					inactiveNode = node.children[1].root
				else:
					activeNode = node.children[1].root
					inactiveNode = node.children[0].root

				branch_states.activityState[activeNode] = ActivityState.ACTIVE
				branch_states.activityState[inactiveNode] = ActivityState.WILL_NOT_BE_EXECUTED

				branch_decisions.append(activeNode)

			branches[tuple(branch_decisions)] = branch_states


	for next_decisions, branch_states in branches.items():
		sub_tree, id = full_strategy(region_tree, typeStrategy, explainers, impacts_size, branch_states, tuple(next_decisions), id + 1)
		strategyViewPoint.add_child(sub_tree)

	return strategyTree, id
