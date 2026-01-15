import json
from urllib.parse import parse_qs

import dash
from dash import Input, Output, State, no_update
import dash_bootstrap_components as dbc

from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.env import BOUND, EXPRESSION, SESE_PARSER, extract_nodes
from gui.src.example_registry import EXAMPLE_PATHS
from gui.src.model.bpmn import validate_bpmn_dict
from gui.src.model.etl import load_bpmn_dot
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table


def register_example_load_callbacks(callback):
	@callback(
		Output("bpmn-store", "data", allow_duplicate=True),
		Output("bound-store", "data", allow_duplicate=True),
		Output({"type": "bpmn-svg-store", "index": "main"}, "data", allow_duplicate=True),
		Output("task-impacts-table", "children", allow_duplicate=True),
		Output("task-durations-table", "children", allow_duplicate=True),
		Output("choice-table", "children", allow_duplicate=True),
		Output("nature-table", "children", allow_duplicate=True),
		Output("loop-table", "children", allow_duplicate=True),
		Output("expression-bpmn", "value", allow_duplicate=True),
		Output("bpmn-alert", "children", allow_duplicate=True),
		Input("url", "search"),
		State("bound-store", "data"),
		prevent_initial_call="initial_duplicate",
	)
	def load_example_from_query(search, bound_store):
		if not search:
			raise dash.exceptions.PreventUpdate

		query = parse_qs(search.lstrip("?"))
		example_keys = query.get("example")
		if not example_keys:
			raise dash.exceptions.PreventUpdate

		example_key = example_keys[0]
		example_path = EXAMPLE_PATHS.get(example_key)
		if not example_path:
			alert = dbc.Alert(f"Unknown example '{example_key}'.", color="warning", dismissable=True)
			return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, alert

		try:
			with open(example_path, "r", encoding="utf-8") as file:
				data = json.load(file)

			new_bpmn = validate_bpmn_dict(data.get("bpmn", {}))
			if EXPRESSION not in new_bpmn:
				alert = dbc.Alert("Missing 'expression' in BPMN", color="danger", dismissable=True)
				return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, alert

			new_bpmn[EXPRESSION] = new_bpmn[EXPRESSION].replace("\n", "").replace("\t", "").strip().replace(" ", "")
			if new_bpmn[EXPRESSION] == "":
				alert = dbc.Alert("Empty expression in BPMN", color="danger", dismissable=True)
				return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, alert

			SESE_PARSER.parse(new_bpmn[EXPRESSION])
			tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(new_bpmn[EXPRESSION]))

			task_impacts = create_tasks_impacts_table(new_bpmn, tasks)
			task_durations = create_tasks_duration_table(new_bpmn, tasks)
			choice_table = create_choices_table(new_bpmn, choices)
			nature_table = create_natures_table(new_bpmn, natures)
			loop_table = create_loops_table(new_bpmn, loops)

			bpmn_dot = load_bpmn_dot(new_bpmn)

			if not bound_store or BOUND not in bound_store:
				bound_store = {BOUND: {}}

			return (
				new_bpmn,
				sync_bound_store_from_bpmn(new_bpmn, bound_store),
				bpmn_dot,
				task_impacts,
				task_durations,
				choice_table,
				nature_table,
				loop_table,
				new_bpmn[EXPRESSION],
				dbc.Alert("Example loaded successfully", color="success", dismissable=True),
			)

		except Exception as exception:
			alert = dbc.Alert(f"Example load error: {exception}", color="danger", dismissable=True)
			return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, alert
