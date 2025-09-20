def get_prev_execution_node(execution_tree: dict, current_execution_id) -> dict | None:
    current_node = get_execution_node(execution_tree, current_execution_id)
    if not current_node:
        return None

    return get_parent_node(execution_tree, current_node['id'])


def get_parent_node(root: dict, node_id: str) -> dict | None:
    if root is None:
        return None
    if root['id'] == node_id:
        return None

    for child in root.get('children', []):
        if child['id'] == node_id:
            return root
        result = get_parent_node(child, node_id)
        if result:
            return result

    return None


def get_current_marking_from_execution_tree(execution_tree: dict, current_pointer: str) -> dict:
    if execution_tree['id'] == current_pointer:
        return execution_tree['snapshot']['marking']
    for child in execution_tree.get('children', []):
        result = get_current_marking_from_execution_tree(child, current_pointer)
        if result:
            return result
    return {}


def get_execution_node(root: dict, node_id: str) -> dict | None:
    if root['id'] == node_id:
        return root
    for child in root.get('children', []):
        result = get_execution_node(child, node_id)
        if result:
            return result
    return None

def get_execution_impacts(execution_tree: dict, node_id: str) -> list[float]:
    node = get_execution_node(execution_tree, node_id)
    if node:
        return __get_execution_impacts(node)
    return []

def __get_execution_impacts(node: dict) -> list[float]:
    if 'snapshot' in node and 'impacts' in node['snapshot']:
        return node['snapshot']['impacts']
    return []

def get_execution_probability(execution_tree: dict, node_id: str) -> float:
    node = get_execution_node(execution_tree, node_id)
    if node:
        return __get_execution_probability(node)
    return 0.0

def __get_execution_probability(node: dict) -> float:
    if 'snapshot' in node and 'probability' in node['snapshot']:
        return node['snapshot']['probability']
    return 0.0

def get_execution_time(execution_tree: dict, node_id: str) -> float:
    node = get_execution_node(execution_tree, node_id)
    if node:
        return __get_execution_time(node)
    return 0.0

def __get_execution_time(node: dict) -> float:
    if 'snapshot' in node and 'execution_time' in node['snapshot']:
        return node['snapshot']['execution_time']
    return 0.0