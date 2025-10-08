from .__bpmn import wrap_to_dot
from .__execution_tree import wrapper_execution_tree_to_dot


def get_bpmn_dot_from_parse_tree(parse_tree: dict, impacts_names: list[str], active_regions: set[str] = None,
                                 is_initial: bool = False, is_final: bool = False):
    """
    Wrapper to create the dot representation of the BPMN from its parse tree.

    :param parse_tree: Parse tree object
    :param impacts_names: Impacts names to display
    :param active_regions: Active regions to highlight
    :param is_initial: True if the marking is initial
    :param is_final: True if the marking is final
    :return: Dot representation of the BPMN
    """
    if active_regions is None:
        active_regions = set()
    if isinstance(active_regions, list):
        active_regions = set(active_regions)

    return wrap_to_dot(parse_tree.root, impacts_names, active_regions, is_initial, is_final)


def get_execution_tree_dot(execution_tree: dict, impacts_names: list[str], path: list[str] = None):
    """
    Wrapper to create the dot representation of the execution tree.

    :param execution_tree: Execution tree object
    :param impacts_names: Impacts names to display
    :param path: Ids of the nodes in the path to highlight
    :return: Dot representation of the execution tree
    """
    if path is None:
        path = []
    return wrapper_execution_tree_to_dot(execution_tree, impacts_names, path)
