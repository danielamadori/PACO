from .__bpmn import wrap_to_dot, get_active_region_by_pn
from .__execution_tree import wrapper_execution_tree_to_dot


def get_bpmn_dot_from_parse_tree(parse_tree: dict, impacts_names: list[str], active_regions: set[str] = None):
    if active_regions is None:
        active_regions = set()

    return wrap_to_dot(parse_tree, impacts_names, active_regions)


def get_execution_tree_dot(execution_tree: dict, impacts_names: list[str], path: list[str] = None):
    if path is None:
        path = []
    return wrapper_execution_tree_to_dot(execution_tree, impacts_names, path)
