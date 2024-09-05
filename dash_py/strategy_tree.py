import copy
import os
from itertools import product

from explainer.dag import Dag
from explainer.explain_strategy import TypeStrategy
from explainer.impacts import current_impacts, unavoidable_impacts, stateful, evaluate_unavoidable_impacts, \
	evaluate_execution_path
from saturate_execution.next_state import next_state
from saturate_execution.states import States, ActivityState, states_info
from saturate_execution.step_to_saturation import steps_to_saturation
from solver.tree_lib import CNode, CTree
from solver_optimized.execution_tree import ExecutionTree, ExecutionViewPoint, write_image, evaluate_expected_impacts
from utils.env import PATH_STRATEGY_TREE, PATH_STRATEGY_TREE_STATE_DOT, PATH_STRATEGY_TREE_STATE_IMAGE_SVG, \
	PATH_STRATEGY_TREE_STATE_TIME_DOT, PATH_STRATEGY_TREE_STATE_TIME_IMAGE_SVG, \
	PATH_STRATEGY_TREE_STATE_TIME_EXTENDED_DOT, PATH_STRATEGY_TREE_STATE_TIME_EXTENDED_IMAGE_SVG, \
	PATH_STRATEGY_TREE_TIME_DOT, PATH_STRATEGY_TREE_TIME_IMAGE_SVG

def saturate_execution(region_tree: CTree, states: States) -> States:
	while states.activityState[region_tree.root] < ActivityState.COMPLETED:
		#print("step_to_saturation:")
		#print("start:", states_info(states))

		k = steps_to_saturation(region_tree, states)
		#print('step_to_saturation:k:', k, states_info(states))

		updatedStates, k = next_state(region_tree, states, k)
		states.update(updatedStates)

		#print('next_state:k:', k, states_info(states))
		if k > 0:
			raise Exception("StepsException" + str(k))

		choices, natures = [], []
		node: CNode
		for node in list(states.activityState.keys()):
			if (node.type == 'choice'
					and states.activityState[node] == ActivityState.ACTIVE
					and states.executed_time[node] == node.max_delay
					and states.activityState[node.childrens[0].root] == ActivityState.WAITING
					and states.activityState[node.childrens[1].root] == ActivityState.WAITING):

				choices.append(node)

			if (node.type == 'natural'
					and states.activityState[node] == ActivityState.ACTIVE
					and states.activityState[node.childrens[0].root] == ActivityState.WAITING
					and states.activityState[node.childrens[1].root] == ActivityState.WAITING):

				natures.append(node)

		if len(choices) > 0 or len(natures) > 0:
			return states, False, choices, natures

	return states, True, [], []



def full_strategy(region_tree: CTree, typeStrategy: TypeStrategy, explainers: dict [CNode, Dag], impacts_size: int, states: States = None) -> set[States]:
	if states is None:
		states = States(region_tree.root, ActivityState.WAITING, 0)

	states, is_final, choices, natures = saturate_execution(region_tree, states)

	print(states_info(states))

	if is_final:
		return {states}

	print("typeStrategy: ", typeStrategy)
	if typeStrategy <= TypeStrategy.UNAVOIDABLE_IMPACTS: # Current impacts
		_, vector = evaluate_expected_impacts(states, impacts_size)
		print("Current impacts: ", vector)
		if typeStrategy == TypeStrategy.UNAVOIDABLE_IMPACTS:
			vector = evaluate_unavoidable_impacts(region_tree.root, states, vector)#TODO create function
			print("Unavoidable impacts: ", vector)
	elif typeStrategy == TypeStrategy.STATEFUL:
		all_nodes, vectors = evaluate_execution_path([states.activityState])
		vector = vectors[0]
		print("Stateful impacts: ", vector)
		#print("All nodes: ", all_nodes)
	else:
		raise Exception("TypeStrategy not implemented: " + str(typeStrategy))

	choices_dict = {CNode: Dag}
	chose_states = copy.deepcopy(states)
	for choice in choices:
		if choice not in explainers:
			raise Exception("Choice not explained: " + str(choice))

		explainer = explainers[choice]
		choices_dict[choice] = explainer
		print("Explaining choice: ", choice.id)

		decision_true = explainer.choose(vector)
		decision_false = choice.childrens[1].root if decision_true == choice.childrens[0].root else choice.childrens[0].root

		print("Decision True: ", decision_true.id)
		print("Decision False: ", decision_false.id)
		chose_states.activityState[decision_true] = ActivityState.ACTIVE
		chose_states.activityState[decision_false] = ActivityState.WILL_NOT_BE_EXECUTED

	branches_states = []
	if len(natures) == 0:
		branches_states.append(chose_states)
	else:
		branches_decisions = list(product([True, False], repeat=len(natures)))
		#print(f"combinations:{branches_decisions}")
		for branch_choices in branches_decisions:
			branch_states = copy.deepcopy(chose_states)

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

			branches_states.append(branch_states)


	full_strategy(region_tree, typeStrategy, explainers, impacts_size, branches_states[0])













class StrategyTree(ExecutionTree):
	def __init__(self, executionTree: ExecutionTree, bdds: list[Dag]):
		self.root = copy.copy(executionTree.root)
		self.choices = {CNode: Dag}
		self.natures = []
		sat_decisions = []
		#s = ""
		for node in self.root.choices_natures:
			#print("Node: ", node.id, node.type)
			if node.type == "natural":
				self.natures.append(node)
				continue

			for bdd in bdds:
				if bdd.choice == node:
					self.choices[node] = bdd
					sat_decisions.append(bdd.class_0)
					if bdd.class_1 is not None:
						sat_decisions.append(bdd.class_1)

		#TODO print attribute choices, nature and sat_decisions on the edge

		#for nature in self.natures:
		#	s += str(nature.id) + ", "
		#print("Natures: ", s)

		isOnlyNatures = len(self.natures) == len(self.root.choices_natures)

		##s = ""
		#for decision in sat_decisions:
		#	s += str(decision.id) + ", "
		#print("Sat Decisions: ", s[:-2])

		sat_transition: dict[tuple, StrategyTree] = {}
		for transition, subTree in self.root.transitions.items():
			#s = ""
			#for d in subTree.root.decisions:
			#	s += str(d.id) + ", "
			#print("decisions: " + s[:-2])
			# TODO: if there are just nature keep all the children
			if all(sat_decision not in subTree.root.decisions for sat_decision in sat_decisions) and not isOnlyNatures:
				#print("Pruning node with ID: ", subTree.root.id)
				continue

			sat_transition[transition] = StrategyTree(subTree, bdds)

		self.root.transitions = sat_transition


def write_strategy_tree(solution_tree: StrategyTree, frontier: list[StrategyTree] = []):
	if not os.path.exists(PATH_STRATEGY_TREE):
		os.makedirs(PATH_STRATEGY_TREE)

	solution_tree.save_dot(PATH_STRATEGY_TREE_STATE_DOT)
	write_image(frontier, PATH_STRATEGY_TREE_STATE_DOT, svgPath=PATH_STRATEGY_TREE_STATE_IMAGE_SVG)#, PATH_STRATEGY_TREE_STATE_IMAGE_SVG)

	solution_tree.save_dot(PATH_STRATEGY_TREE_STATE_TIME_DOT, executed_time=True)
	write_image(frontier, PATH_STRATEGY_TREE_STATE_TIME_DOT, svgPath=PATH_STRATEGY_TREE_STATE_TIME_IMAGE_SVG)#, PATH_STRATEGY_TREE_STATE_TIME_IMAGE_SVG)

	solution_tree.save_dot(PATH_STRATEGY_TREE_STATE_TIME_EXTENDED_DOT, executed_time=True, diff=False)
	write_image(frontier, PATH_STRATEGY_TREE_STATE_TIME_EXTENDED_DOT, svgPath=PATH_STRATEGY_TREE_STATE_TIME_EXTENDED_IMAGE_SVG)#, PATH_STRATEGY_TREE_STATE_TIME_EXTENDED_IMAGE_SVG)

	solution_tree.save_dot(PATH_STRATEGY_TREE_TIME_DOT, state=False, executed_time=True)
	write_image(frontier, PATH_STRATEGY_TREE_TIME_DOT, svgPath=PATH_STRATEGY_TREE_TIME_IMAGE_SVG)#, PATH_STRATEGY_TREE_TIME_IMAGE_SVG)
