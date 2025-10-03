import ast
import base64
import json
from copy import deepcopy

import graphviz
import requests

from gui.src.env import (
    URL_SERVER,
    HEADERS,
    SESE_PARSER,
    EXPRESSION,
    IMPACTS_NAMES,
    IMPACTS,
    DURATIONS,
    DELAYS,
    PROBABILITIES,
    LOOP_PROBABILITY,
    LOOP_ROUND,
    extract_nodes,
    BOUND,
    SIMULATOR_SERVER,
)
from gui.src.model.execution_tree import (
    get_execution_node,
    get_current_marking_from_execution_tree,
    get_execution_probability,
    get_execution_time,
    get_execution_impacts,
)
from gui.src.model.petri_net import (
    get_pending_decisions,
    is_final_marking,
    is_initial_marking,
)
from gui.src.model.sqlite import (
    fetch_bpmn,
    save_execution_tree,
    save_parse_tree,
    fetch_strategy,
    save_strategy,
    save_petri_net,
    save_bpmn_dot,
    update_bpmn_dot as _update_bpmn_record,
)



def load_bpmn_dot(bpmn: dict) -> str:
    """
    Given a BPMN process, return its DOT representation as an SVG base64 string.
    If the DOT representation is already stored in the database, retrieve it from there.
    Otherwise, generate it, store it in the database, and return it.

    :param bpmn: BPMN dictionary
    :return: SVG base64 string of the BPMN DOT representation
    """
    bpmn = keep_relevant_bpmn(bpmn)
    record = fetch_bpmn(bpmn)
    if record and record.bpmn_dot:
        return record.bpmn_dot

    bpmn_dot = bpmn_to_dot(bpmn)
    bpmn_svg_base64 = dot_to_base64svg(bpmn_dot)

    save_bpmn_dot(bpmn, bpmn_svg_base64)

    return bpmn_svg_base64


def dot_to_base64svg(dot: str) -> str:
    """
    Convert a DOT string to an SVG base64 string.

    :param dot: DOT string
    :return: SVG base64 string
    """
    svg = graphviz.Source(dot).pipe(format='svg')
    svg_base64 = f"data:image/svg+xml;base64,{base64.b64encode(svg).decode('utf-8')}"
    return svg_base64


def bpmn_to_dot(bpmn) -> str:
    """
    Given a BPMN process, return its DOT representation.

    :param bpmn: BPMN dictionary
    :return: BPMN DOT string
    """
    parse_tree = load_parse_tree(bpmn)
    petri_net, _ = get_petri_net(bpmn, step=0)
    execution_tree, current_execution_node = load_execution_tree(bpmn)

    from .helpers.dot import get_bpmn_dot_from_parse_tree, get_active_region_by_pn
    current_node = get_execution_node(execution_tree, current_execution_node)
    current_marking = current_node['snapshot']['marking']
    is_initial = is_initial_marking(current_marking, petri_net)
    is_final = is_final_marking(current_marking, petri_net)
    active_regions = get_active_region_by_pn(petri_net, current_marking)
    bpmn_dot_str = get_bpmn_dot_from_parse_tree(parse_tree,
                                                bpmn[IMPACTS_NAMES] if IMPACTS_NAMES in bpmn else [],
                                                active_regions,
                                                is_initial=is_initial,
                                                is_final=is_final)
    return bpmn_dot_str


def update_bpmn_dot(bpmn: dict, bpmn_dot: str):
    """
    Update the BPMN DOT representation in the database for the given BPMN process.

    :param bpmn: BPMN dictionary
    :param bpmn_dot: BPMN DOT string
    :return: None
    """
    bpmn = keep_relevant_bpmn(bpmn)
    _update_bpmn_record(bpmn, bpmn_dot)


def load_parse_tree(bpmn: dict, *, force_refresh: bool = False) -> dict:
    """
    Given a BPMN process, return its parse tree.
    If the parse tree is already stored in the database, retrieve it from there.
    Otherwise, request it from the server and store it in the database.

    :param bpmn: BPMN dictionary
    :return: Parse tree dictionary
    """
    bpmn = keep_relevant_bpmn(bpmn)
    if bpmn is None:
        raise ValueError("BPMN expression is empty")

    record = fetch_bpmn(bpmn)
    if not force_refresh and record and record.parse_tree:
        return json.loads(record.parse_tree)

    resp = requests.get(URL_SERVER + "create_parse_tree", json={"bpmn": bpmn}, headers=HEADERS)
    resp.raise_for_status()

    resp_json = resp.json()
    if 'error' in resp_json:
        raise ValueError(f"Error from server: {resp_json['error']}")

    parse_tree = resp_json["parse_tree"]
    save_parse_tree(bpmn, json.dumps(parse_tree))

    return parse_tree


def load_execution_tree(bpmn: dict, *, force_refresh: bool = False) -> tuple[dict, str]:
    """
    Given a BPMN process, return its execution tree and the current execution node.
    If the execution tree is already stored in the database, retrieve it from there.
    Otherwise, request it from the simulator server and store it in the database.

    :param bpmn: BPMN dictionary
    :return: Tuple of execution tree dictionary and current execution node ID
    """
    bpmn = keep_relevant_bpmn(bpmn)
    record = fetch_bpmn(bpmn)
    if (not force_refresh and record and record.execution_tree and record.actual_execution):
        return json.loads(record.execution_tree), record.actual_execution

    parse_tree = load_parse_tree(bpmn, force_refresh=force_refresh)

    try:
        resp = requests.post(SIMULATOR_SERVER + 'execute', json={"bpmn": parse_tree}, headers=HEADERS)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        if exc.response is None or exc.response.status_code != 422:
            raise

        parse_tree = load_parse_tree(bpmn, force_refresh=True)
        resp = requests.post(SIMULATOR_SERVER + 'execute', json={"bpmn": parse_tree}, headers=HEADERS)
        resp.raise_for_status()
    resp_json = resp.json()

    if 'error' in resp_json:
        raise ValueError(f"Simulator error: {resp_json['error']}")

    execution_tree = resp_json.get('execution_tree', None)
    if execution_tree is None:
        raise ValueError("Simulator error: No execution tree returned")

    execution_tree_root = execution_tree.get('root', None)
    current_execution_node = execution_tree.get('current_node', None)

    if execution_tree_root is None or current_execution_node is None:
        raise ValueError("Simulator error: Incomplete execution tree data")

    save_execution_tree(bpmn, json.dumps(execution_tree_root), current_execution_node)

    return execution_tree_root, current_execution_node


def get_petri_net(bpmn: dict, step: int, *, force_refresh: bool = False) -> tuple[dict, str]:
    """
    Given a BPMN process, return its Petri net representation and its DOT format.
    If the Petri net is already stored in the database, retrieve it from there.
    Otherwise, request it from the simulator server and store it in the database.

    :param bpmn: BPMN dictionary
    :param step: Step number (currently unused)
    :return: Tuple of Petri net dictionary and DOT string
    """
    bpmn = keep_relevant_bpmn(bpmn)
    record = fetch_bpmn(bpmn)
    if not force_refresh and record and record.petri_net and record.petri_net_dot:
        return json.loads(record.petri_net), record.petri_net_dot

    parse_tree = load_parse_tree(bpmn, force_refresh=force_refresh)

    try:
        resp = requests.post(SIMULATOR_SERVER + 'execute', json={"bpmn": parse_tree}, headers=HEADERS)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        if exc.response is None or exc.response.status_code != 422:
            raise

        parse_tree = load_parse_tree(bpmn, force_refresh=True)
        resp = requests.post(SIMULATOR_SERVER + 'execute', json={"bpmn": parse_tree}, headers=HEADERS)
        resp.raise_for_status()
    resp_json = resp.json()

    if 'error' in resp_json:
        raise ValueError(f"Simulator error: {resp_json['error']}")

    petri_net = resp_json.get('petri_net', None)
    petri_net_dot = resp_json.get('petri_net_dot', None)

    if petri_net is None or petri_net_dot is None:
        raise ValueError("Simulator error: Incomplete Petri net data")

    save_petri_net(bpmn, json.dumps(petri_net, sort_keys=True), petri_net_dot)

    return petri_net, petri_net_dot


def load_strategy(bpmn_store, bound_store):
    if bpmn_store[EXPRESSION] == '':
        raise ValueError("The expression is empty")
    if BOUND not in bound_store or not bound_store[BOUND]:
        raise ValueError("Bound is empty")

    tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
    bpmn = filter_bpmn(bpmn_store, tasks, choices, natures, loops)

    bound = [float(bound_store[BOUND][impact_name]) for impact_name in bpmn[IMPACTS_NAMES]]  # Already sorted

    record = fetch_strategy(bpmn, bound)
    # if record and record.bdds:
    #	return record.bdds

    parse_tree = load_parse_tree(bpmn)
    execution_tree = load_execution_tree(bpmn)

    resp = requests.get(URL_SERVER + "create_strategy",
                        json={"bpmn": bpmn, "bound": bound,
                              "parse_tree": parse_tree, "execution_tree": execution_tree},
                        headers=HEADERS)

    resp.raise_for_status()
    response = resp.json()

    expected_impacts = []
    if "expected_impacts" in response:  # Solution found
        expected_impacts = [float(x) for x in response["expected_impacts"].strip('[]').split()]

    guaranteed_bounds = [
        [float(x) for x in s.strip('[]').split()]
        for s in ast.literal_eval(response['guaranteed_bounds'])
    ]

    possible_min_solution = [
        [float(x) for x in s.strip('[]').split()]
        for s in ast.literal_eval(response['possible_min_solution'])
    ]

    bdds = {}
    if "bdds_dot" in response:  # Solution Explained
        for choice, v in response["bdds_dot"].items():
            type_strategy, bdd_dot = v
            bdds[choice] = (
                type_strategy,
                f"data:image/svg+xml;base64,{base64.b64encode(graphviz.Source(bdd_dot).pipe(format='svg')).decode('utf-8')}"
            )

    save_strategy(bpmn, bound, response["result"],
                  str(expected_impacts), response['guaranteed_bounds'],
                  response['possible_min_solution'], bdds)

    return response["result"], expected_impacts, guaranteed_bounds, possible_min_solution, bdds


def filter_bpmn(bpmn_store, tasks, choices, natures, loops):
    # Filter the data to keep only the relevant tasks, choices, natures, and loops
    bpmn = deepcopy(bpmn_store)
    bpmn[IMPACTS_NAMES] = sorted(bpmn_store[IMPACTS_NAMES])
    bpmn[IMPACTS] = {
        task: [float(bpmn_store[IMPACTS][task][impact_name]) for impact_name in bpmn[IMPACTS_NAMES]]
        for task in tasks if task in bpmn_store[IMPACTS]
    }

    bpmn[DURATIONS] = {task: bpmn_store[DURATIONS][task] for task in tasks if task in bpmn_store[DURATIONS]}
    bpmn[DELAYS] = {choice: bpmn_store[DELAYS][choice] for choice in choices if choice in bpmn_store[DELAYS]}
    bpmn[PROBABILITIES] = {nature: bpmn_store[PROBABILITIES][nature] for nature in natures if
                           nature in bpmn_store[PROBABILITIES]}
    bpmn[LOOP_PROBABILITY] = {loop: bpmn_store[LOOP_PROBABILITY][loop] for loop in loops if
                              loop in bpmn_store[LOOP_PROBABILITY]}
    bpmn[LOOP_ROUND] = {loop: bpmn_store[LOOP_ROUND][loop] for loop in loops if loop in bpmn_store[LOOP_ROUND]}

    return bpmn


def can_filter(bpmn):
    """
    Check if the BPMN can be filtered.
    A BPMN can be filtered if it has impacts defined as dictionaries.
    Useful for keep_relevant_bpmn function.

    :param bpmn: The BPMN to check.
    :return: True if the BPMN can be filtered, False otherwise.
    """
    impacts = bpmn[IMPACTS]
    for key in impacts:
        current = impacts[key]
        if isinstance(current, dict):
            return True

    return False


def keep_relevant_bpmn(bpmn):
    """
    Keep only the relevant parts of the BPMN.
    Remove tasks, choices, natures, and loops that are not present in the expression.
    :param bpmn: The BPMN to filter.
    :return: The filtered BPMN or None if bpmn expression is empty.
    """
    if not can_filter(bpmn):
        return bpmn

    if bpmn[EXPRESSION] == '':
        return bpmn

    tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn[EXPRESSION]))
    bpmn = filter_bpmn(bpmn, tasks, choices, natures, loops)

    return bpmn


def set_actual_execution(bpmn: dict, actual_execution: str):
    """
    Set the actual execution node in the database for the given BPMN process.

    :param bpmn: BPMN dictionary
    :param actual_execution: Current execution node ID
    :return: None
    """
    bpmn = keep_relevant_bpmn(bpmn)
    record = fetch_bpmn(bpmn)
    if not record or not record.execution_tree:
        return

    save_execution_tree(bpmn, record.execution_tree, actual_execution)


def get_current_state(bpmn):
    """
    Given a BPMN process, return the current marking from its execution tree.

    :param bpmn: BPMN dictionary
    :return: Current marking dictionary
    """
    execution_tree, current_execution = load_execution_tree(bpmn)
    return get_current_marking_from_execution_tree(execution_tree, current_execution)


def get_simulation_data(bpmn):
    """
    Get the simulation data for the given BPMN process.
    This includes pending gateway decisions, impacts, expected impacts, probability, and execution time.

    :param bpmn: BPMN dictionary
    :return: Simulation data dictionary
    """
    bpmn = keep_relevant_bpmn(bpmn)

    petri_net, _ = get_petri_net(bpmn, 0)
    current_state = get_current_state(bpmn)
    pending_decisions = get_pending_decisions(petri_net, current_state)

    execution_tree, current_execution = load_execution_tree(bpmn)
    probability = get_execution_probability(execution_tree, current_execution)
    execution_time = get_execution_time(execution_tree, current_execution)

    raw_impacts = get_execution_impacts(execution_tree, current_execution)

    impacts = {name: round(value, 2) for name, value in zip(bpmn[IMPACTS_NAMES], raw_impacts)}
    expected_impacts = {name: round(value * probability, 2) for name, value in zip(bpmn[IMPACTS_NAMES], raw_impacts)}

    return {
        "gateway_decisions": pending_decisions,
        "impacts": impacts,
        "expected_impacts": expected_impacts,
        "probability": probability,
        "execution_time": execution_time
    }


def execute_decisions(bpmn, gateway_decisions: list[str], step: int | None = None):
    """
    Execute the given gateway decisions on the BPMN process.
    Update the Petri net and execution tree in the database.
    Return the updated simulation data.

    :param bpmn: BPMN dictionary
    :param gateway_decisions: List of gateway decision IDs
    :param step: Optional step number. Ignored in current implementation.
    :return: Updated simulation data dictionary or None if error occurs
    """
    filtered_bpmn = keep_relevant_bpmn(bpmn)
    decisions = list(gateway_decisions)

    parse_tree = load_parse_tree(filtered_bpmn)
    petri_net, petri_net_dot = get_petri_net(filtered_bpmn, step)
    execution_tree, current_execution = load_execution_tree(filtered_bpmn)

    request = {
        "bpmn": parse_tree,
        "petri_net": petri_net,
        "petri_net_dot": petri_net_dot,
        "execution_tree": {"root": execution_tree, "current_node": current_execution},
        "choices": decisions,
    }

    try:
        response = requests.post(SIMULATOR_SERVER + "execute", json=request, headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        if exc.response is None or exc.response.status_code != 422:
            raise

        parse_tree = load_parse_tree(filtered_bpmn, force_refresh=True)
        petri_net, petri_net_dot = get_petri_net(filtered_bpmn, step, force_refresh=True)
        execution_tree, current_execution = load_execution_tree(filtered_bpmn, force_refresh=True)

        request = {
            "bpmn": parse_tree,
            "petri_net": petri_net,
            "petri_net_dot": petri_net_dot,
            "execution_tree": {"root": execution_tree, "current_node": current_execution},
            "choices": decisions,
        }

        response = requests.post(SIMULATOR_SERVER + "execute", json=request, headers=HEADERS)
        response.raise_for_status()

    resp_json = response.json()
    if 'error' in resp_json:
        raise ValueError(f"Simulator error: {resp_json['error']}")

    petri_net = resp_json['petri_net']
    petri_net_dot = resp_json['petri_net_dot']
    execution_tree = resp_json['execution_tree']['root']
    current_execution = resp_json['execution_tree']['current_node']

    save_petri_net(filtered_bpmn, json.dumps(petri_net, sort_keys=True), petri_net_dot)
    save_execution_tree(filtered_bpmn, json.dumps(execution_tree), current_execution)

    return get_simulation_data(filtered_bpmn)
