import json
import ast
from copy import deepcopy
from model.sqlite import fetch_strategy, save_strategy
from model.sqlite import fetch_bpmn, save_parse_and_execution_tree
import base64
import graphviz
import requests
from model.sqlite import save_bpmn_dot
from env import URL_SERVER, HEADERS, SESE_PARSER, EXPRESSION, IMPACTS_NAMES, IMPACTS, DURATIONS, DELAYS, PROBABILITIES, \
	LOOP_PROBABILITY, LOOP_ROUND, extract_nodes, BOUND


def load_bpmn_dot(bpmn):
	tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn[EXPRESSION]))
	bpmn = filter_bpmn(bpmn, tasks, choices, natures, loops)
	#print(f"Data: {bpmn}")

	record = fetch_bpmn(bpmn)
	if record and record.bpmn_dot:
		return record.bpmn_dot

	try:
		resp = requests.get(URL_SERVER + "create_bpmn", json={'bpmn': bpmn}, headers=HEADERS)
		resp.raise_for_status()
		dot = resp.json().get('bpmn_dot', '')
	except requests.exceptions.RequestException as e:
		raise RuntimeError(f"Failed to fetch BPMN dot: {e}")

	svg = graphviz.Source(dot).pipe(format='svg')
	bpmn_dot = f"data:image/svg+xml;base64,{base64.b64encode(svg).decode('utf-8')}"
	save_bpmn_dot(bpmn, bpmn_dot)
	return bpmn_dot


def load_parse_and_execution_tree(bpmn):#BPMN must be filtered
	record = fetch_bpmn(bpmn)
	if record and record.execution_tree and record.parse_tree:
		return record.parse_tree, record.execution_tree

	resp = requests.get(URL_SERVER + "create_execution_tree", json={"bpmn": bpmn}, headers=HEADERS)
	resp.raise_for_status()

	r = resp.json()
	parse_tree = r["parse_tree"]
	execution_tree = r["execution_tree"]
	save_parse_and_execution_tree(bpmn, json.dumps(parse_tree), json.dumps(execution_tree))

	return parse_tree, execution_tree


def load_strategy(bpmn_store, bound_store):
	tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
	bpmn = filter_bpmn(bpmn_store, tasks, choices, natures, loops)

	bound = [float(bound_store[BOUND][impact_name]) for impact_name in bpmn[IMPACTS_NAMES]]#Already sorted

	record = fetch_strategy(bpmn, bound)
	#if record and record.bdds:
	#	return record.bdds

	parse_tree, execution_tree = load_parse_and_execution_tree(bpmn)

	resp = requests.get(URL_SERVER + "create_strategy",
						json={"bpmn": bpmn, "bound": bound,
							  "parse_tree": parse_tree, "execution_tree": execution_tree},
						headers=HEADERS)

	resp.raise_for_status()
	response = resp.json()

	expected_impacts = []
	if "expected_impacts" in response: # Solution found
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
	if "bdds_dot" in response:# Solution Explained
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
	bpmn[PROBABILITIES] = {nature: bpmn_store[PROBABILITIES][nature] for nature in natures if nature in bpmn_store[PROBABILITIES]}
	bpmn[LOOP_PROBABILITY] = {loop: bpmn_store[LOOP_PROBABILITY][loop] for loop in loops if loop in bpmn_store[LOOP_PROBABILITY]}
	bpmn[LOOP_ROUND] = {loop: bpmn_store[LOOP_ROUND][loop] for loop in loops if loop in bpmn_store[LOOP_ROUND]}

	return bpmn
