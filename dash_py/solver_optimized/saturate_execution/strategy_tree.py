import copy
import os

from explainer.dag import Dag
from solver_optimized.execution_tree import ExecutionTree, ExecutionViewPoint, write_image
from utils.env import PATH_STRATEGY_TREE, PATH_STRATEGY_TREE_STATE_DOT, PATH_STRATEGY_TREE_STATE_IMAGE_SVG, \
	PATH_STRATEGY_TREE_STATE_TIME_DOT, PATH_STRATEGY_TREE_STATE_TIME_IMAGE_SVG, \
	PATH_STRATEGY_TREE_STATE_TIME_EXTENDED_DOT, PATH_STRATEGY_TREE_STATE_TIME_EXTENDED_IMAGE_SVG, \
	PATH_STRATEGY_TREE_TIME_DOT, PATH_STRATEGY_TREE_TIME_IMAGE_SVG


class StrategyTree(ExecutionTree):
	def __init__(self, executionTree: ExecutionTree, bdds: list[Dag]):
		self.root = copy.copy(executionTree.root)
		self.bdds = []
		sat_decisions = []
		for choice in self.root.choices_natures:
			for bdd in bdds:
				if bdd.choice == choice:
					self.bdds.append(bdd)
					sat_decisions.append(bdd.class_0)
					if bdd.class_1 is not None:
						sat_decisions.append(bdd.class_1)

		s = ""
		for decision in sat_decisions:
			s += str(decision.id) + ", "
		print("Sat Decisions: ", s[:-2])

		sat_transition: dict[tuple, StrategyTree] = {}
		for transition, subTree in self.root.transitions.items():
			s = ""
			for d in subTree.root.decisions:
				s += str(d.id) + ", "
			print("decisions: " + s[:-2])
			if all(sat_decision not in subTree.root.decisions for sat_decision in sat_decisions):
				print("Pruning node with ID: ", subTree.root.id)
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
