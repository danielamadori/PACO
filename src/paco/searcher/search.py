from datetime import datetime
import numpy as np

from paco.searcher.create_execution_tree import write_execution_tree
from paco.execution_tree.execution_tree import ExecutionTree
from paco.searcher.found_strategy import found_strategy
from paco.searcher.build_strategy import build_strategy


def search(execution_tree: ExecutionTree, bound: np.ndarray, impacts_names: list, search_only: bool):
    print(f"{datetime.now()} FoundStrategy:")
    t = datetime.now()
    frontier_solution, expected_impacts, solutions, possible_min_solution = found_strategy([execution_tree], bound)
    t1 = datetime.now()
    found_strategy_time = (t1 - t).total_seconds()*1000
    print(f"{t1} FoundStrategy:completed: {found_strategy_time} ms")

    if frontier_solution is None:
        #TODO plot_pareto_frontier
        return None, possible_min_solution, solutions, [], found_strategy_time, None
    if search_only:
        return expected_impacts, possible_min_solution, solutions, None, found_strategy_time, None

    print(f"Success:\t\t{impacts_names}\nBound Impacts:\t{bound}\nExp. Impacts:\t{expected_impacts}")
    write_execution_tree(execution_tree, frontier_solution)
    
    print(f'{datetime.now()} BuildStrategy:')
    t = datetime.now()
    _, strategy = build_strategy(frontier_solution)
    t1 = datetime.now()
    build_strategy_time = (t1 - t).total_seconds()*1000
    print(f"{t1} Build Strategy:completed: {build_strategy_time} ms")
    return expected_impacts, possible_min_solution, solutions, None if len(strategy) == 0 else strategy, found_strategy_time, build_strategy_time
