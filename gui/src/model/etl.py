import ast
import base64
from copy import deepcopy
from typing import TYPE_CHECKING

import graphviz
import requests

from env import URL_SERVER, HEADERS, SESE_PARSER, EXPRESSION, IMPACTS_NAMES, IMPACTS, DURATIONS, DELAYS, PROBABILITIES, \
    LOOP_PROBABILITY, LOOP_ROUND, extract_nodes, BOUND, SIMULATOR_SERVER
from model.sqlite import fetch_bpmn
from model.sqlite import fetch_strategy, save_strategy, save_bpmn_record

if TYPE_CHECKING:
    from model.sqlite import BPMN


def load_all_bpmn_data(bpmn: dict) -> BPMN:
    bpmn = keep_relevant_bpmn(bpmn)
    if bpmn is None:
        raise ValueError("BPMN expression is empty")

    record = fetch_bpmn(bpmn)
    if record:
        return record

    resp = requests.get(URL_SERVER + "create_parse_tree", json={"bpmn": bpmn}, headers=HEADERS)
    resp.raise_for_status()

    r = resp.json()
    parse_tree = r["parse_tree"]

    # Get all info from simulator
    resp = requests.post(SIMULATOR_SERVER + 'execute', json={"bpmn": parse_tree}, headers=HEADERS)
    resp.raise_for_status()
    resp_json = resp.json()

    if 'error' in resp_json:
        raise ValueError(f"Simulator error: {resp_json['error']}")

    resp_bpmn = resp_json.get('bpmn', None)
    if resp_bpmn is None:
        raise ValueError("Simulator error: No BPMN returned")
    resp_petri_net = resp_json.get('petri_net', None)
    if resp_petri_net is None:
        raise ValueError("Simulator error: No Petri net returned")
    resp_petri_net_dot = resp_json.get('petri_net_dot', None)
    if resp_petri_net_dot is None:
        raise ValueError("Simulator error: No Petri net dot returned")
    resp_execution_tree_raw = resp_json.get('execution_tree', None)
    if resp_execution_tree_raw is None:
        raise ValueError("Simulator error: No execution tree returned")

    execution_tree = resp_execution_tree_raw.get('root', None)
    if execution_tree is None:
        raise ValueError("Simulator error: No execution tree root returned")
    current_execution_node = resp_execution_tree_raw.get('current_node', None)
    if current_execution_node is None:
        raise ValueError("Simulator error: No execution tree current node returned")

    # Create BPMN DOT
    from .helpers.dot import get_bpmn_dot_from_parse_tree, get_active_region_by_pn
    active_regions = get_active_region_by_pn(resp_petri_net, resp_petri_net_dot)
    bpmn_dot_str = get_bpmn_dot_from_parse_tree(parse_tree, bpmn[IMPACTS] if IMPACTS_NAMES in bpmn else [],
                                                active_regions)
    bpmn_svg = graphviz.Source(bpmn_dot_str).pipe(format='svg')
    bpmn_svg_base64 = f"data:image/svg+xml;base64,{base64.b64encode(bpmn_svg).decode('utf-8')}"

    # Save bpmn record with all info
    save_bpmn_record(bpmn=bpmn,
                     bpmn_dot=bpmn_svg_base64,
                     parse_tree=parse_tree,
                     execution_tree=execution_tree,
                     petri_net=resp_petri_net,
                     petri_net_dot=resp_petri_net_dot,
                     execution_petri_net={},  # TODO: What is this?
                     actual_execution=current_execution_node)

    return fetch_bpmn(bpmn)


def load_bpmn_dot(bpmn: dict) -> str:
    record = load_all_bpmn_data(bpmn)
    return record.bpmn_dot


def load_parse_tree(bpmn: dict) -> dict:
    record = load_all_bpmn_data(bpmn)
    return record.parse_tree


def load_execution_tree(bpmn: dict) -> dict:
    record = load_all_bpmn_data(bpmn)
    return record.execution_tree


def get_petri_net(bpmn: dict, step: int) -> tuple[dict, str, dict, dict]:
    record = load_all_bpmn_data(bpmn)
    return record.petri_net, record.petri_net_dot, record.execution_tree_petri_net, record.actual_execution_tree_petri_net


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


def keep_relevant_bpmn(bpmn):
    """
    Keep only the relevant parts of the BPMN.
    Remove tasks, choices, natures, and loops that are not present in the expression.
    :param bpmn: The BPMN to filter.
    :return: The filtered BPMN or None if bpmn expression is empty.
    """
    if bpmn[EXPRESSION] == '':
        return None

    tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn[EXPRESSION]))
    bpmn = filter_bpmn(bpmn, tasks, choices, natures, loops)

    return bpmn
