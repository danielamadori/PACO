import json

from src.model.sqlite import fetch_diagram_by_bpmn, save_parse_and_execution_tree
import base64
import graphviz
import requests
from src.model.sqlite import save_bpmn_dot
from env import URL_SERVER, HEADERS


def load_bpmn_dot(bpmn):
	record = fetch_diagram_by_bpmn(bpmn)
	if record and record.bpmn_dot:
		return record.bpmn_dot, None

	try:
		resp = requests.get(URL_SERVER + "create_bpmn", json={'bpmn': bpmn}, headers=HEADERS)
		resp.raise_for_status()
		dot = resp.json().get('bpmn_dot', '')
	except requests.exceptions.RequestException as e:
		return None, e

	svg = graphviz.Source(dot).pipe(format='svg')
	bpmn_dot = f"data:image/svg+xml;base64,{base64.b64encode(svg).decode('utf-8')}"
	save_bpmn_dot(bpmn, bpmn_dot)
	return bpmn_dot, None


def load_parse_and_execution_tree(bpmn):
	record = fetch_diagram_by_bpmn(bpmn)
	if record and record.execution_tree and record.parse_tree:
		return record.parse_tree, record.execution_tree

	resp = requests.get(URL_SERVER + "create_execution_tree", json={"bpmn": bpmn}, headers=HEADERS)
	resp.raise_for_status()

	r = resp.json()
	parse_tree = r["parse_tree"]
	execution_tree = r["execution_tree"]
	save_parse_and_execution_tree(bpmn, json.dumps(parse_tree), json.dumps(execution_tree))

	return parse_tree, execution_tree