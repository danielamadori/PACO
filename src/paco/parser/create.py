from datetime import datetime
from paco.evaluations.evaluate_cumulative_expected_impacts import evaluate_cumulative_expected_impacts
from paco.execution_tree.execution_tree import ExecutionTree
from paco.parser.bpmn_parser import create_parse_tree
from paco.parser.parse_tree import ParseTree
from paco.searcher.create_execution_tree import create_execution_tree, write_execution_tree
from utils.env import IMPACTS_NAMES, PATH_EXECUTION_TREE


def create(bpmn: dict, parse_tree_from_json=False, execution_tree_from_json=False):
    if parse_tree_from_json:
        print(f'{datetime.now()} Read ParseTree')
        t = datetime.now()
        parse_tree, pending_choice, pending_natures = ParseTree.from_json()
        t1 = datetime.now()
        print(f"{t1} Read ParseTree:completed: {(t1 - t).total_seconds()*1000} ms")
    else:
        print(f"{datetime.now()} Create ParseTree:")
        t = datetime.now()
        parse_tree, pending_choice, pending_natures = create_parse_tree(bpmn)
        t1 = datetime.now()
        print(f"{t1} Create ParseTree:completed: {(t1 - t).total_seconds()*1000} ms")


    parse_tree.to_json()
    parse_tree.print()

    if execution_tree_from_json:
        print(f'{datetime.now()} Read ExecutionTree')
        t = datetime.now()
        execution_tree = ExecutionTree.from_json(parse_tree, bpmn[IMPACTS_NAMES])
        t1 = datetime.now()
        print(f"{t1} Read ExecutionTree:completed: {(t1 - t).total_seconds()*1000} ms")
    else:
        print(f"{datetime.now()} Create ExecutionTree:")
        t = datetime.now()
        execution_tree = create_execution_tree(parse_tree, bpmn[IMPACTS_NAMES], pending_choice, pending_natures)
        t1 = datetime.now()
        print(f"{t1} Create ExecutionTree:completed: {(t1 - t).total_seconds()*1000} ms")
        t = datetime.now()
        evaluate_cumulative_expected_impacts(execution_tree)
        t1 = datetime.now()
        print(f"{t1} Create ExecutionTree:CEI evaluated: {(t1 - t).total_seconds()*1000} ms")

    execution_tree.to_json()
    write_execution_tree(execution_tree)

    return parse_tree, execution_tree
