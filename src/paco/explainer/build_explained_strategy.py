from datetime import datetime
from paco.explainer.explain_strategy import explain_strategy
from paco.explainer.full_strategy import full_strategy
from paco.explainer.strategy_tree import write_strategy_tree
from paco.explainer.explanation_type import ExplanationType
from paco.parser.parse_tree import ParseTree
from paco.parser.parse_node import ParseNode
from paco.execution_tree.execution_tree import ExecutionTree
from utils.env import PATH_STRATEGY_TREE


def build_explained_strategy(parse_tree:ParseTree, strategy: dict[ParseNode, dict[ParseNode, set[ExecutionTree]]], type_strategy: ExplanationType, impacts_names: list,  pending_choices:set, pending_natures:set):
    print(f'{datetime.now()} Explain Strategy: ')
    t = datetime.now()
    worst_type_strategy, bdds = explain_strategy(parse_tree, strategy, impacts_names, type_strategy)
    t1 = datetime.now()
    time_explain_strategy = (t1 - t).total_seconds()*1000
    print(f"{t1} Explain Strategy:completed: {time_explain_strategy} ms")

    s = f": {worst_type_strategy}"
    if type_strategy == ExplanationType.HYBRID:
        s = f"with worst type of choice{s}\n"
    print(f"{t1} Strategy {s}"+ "".join(f"{choice.name}:\t{bdd.typeStrategy}\n" for choice, bdd in bdds.items()))

    print(f'{t1} StrategyTree: ')
    t = datetime.now()
    strategy_tree, children, expected_impacts, expected_time, pending_choices, pending_natures, _ = full_strategy(parse_tree, bdds, len(impacts_names), pending_choices, pending_natures)
    t1 = datetime.now()
    strategy_tree_time = (t1 - t).total_seconds()*1000
    print(f"{t1} StrategyTree:completed: {strategy_tree_time} ms\n")
    print(f"Strategy Expected Impacts: {expected_impacts}\nStrategy Expected Time: {expected_time}")
    strategy_tree.to_json(PATH_STRATEGY_TREE[:-1])
    write_strategy_tree(strategy_tree)

    return strategy_tree, expected_impacts, expected_time, [choice.name for choice in bdds.keys()], time_explain_strategy, strategy_tree_time
