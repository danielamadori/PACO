import base64
import json
import dash
from dash import Input, Output, State, no_update
import dash_bootstrap_components as dbc

from gui.src.env import EXPRESSION, IMPACTS, IMPACTS_NAMES
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.model.bpmn import validate_bpmn_dict
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table
from gui.src.model.etl import load_bpmn_dot
from gui.src.env import SESE_PARSER, extract_nodes


def register_upload_callbacks(callback):
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
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("bound-store", "data"),
        prevent_initial_call=True
    )
    def upload_json_bpmn(contents, filename, bound_store):
        if not contents:
            raise dash.exceptions.PreventUpdate

        try:
            content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string).decode("utf-8")
            data = json.loads(decoded)

            new_bpmn = validate_bpmn_dict(data.get("bpmn", {}))

            if EXPRESSION not in new_bpmn:
                return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, dbc.Alert("Missing 'expression' in BPMN", color="danger", dismissable=True)

            new_bpmn[EXPRESSION] = new_bpmn[EXPRESSION].replace("\n", "").replace("\t", "").strip().replace(" ", "")
            if new_bpmn[EXPRESSION] == '':
                return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, dbc.Alert("Empty expression in BPMN", color="danger", dismissable=True)

            SESE_PARSER.parse(new_bpmn[EXPRESSION])
            tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(new_bpmn[EXPRESSION]))

            task_impacts = create_tasks_impacts_table(new_bpmn, tasks)
            task_durations = create_tasks_duration_table(new_bpmn, tasks)
            choice_table = create_choices_table(new_bpmn, choices)
            nature_table = create_natures_table(new_bpmn, natures)
            loop_table = create_loops_table(new_bpmn, loops)

            try:
                bpmn_dot = load_bpmn_dot(new_bpmn)
            except Exception as exception:
                alert = dbc.Alert(
                    f"Processing error: {str(exception)}",
                    color="danger",
                    dismissable=True,
                )
                return (
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    alert,
                )

            return new_bpmn, sync_bound_store_from_bpmn(new_bpmn, bound_store), bpmn_dot, task_impacts, task_durations, choice_table, nature_table, loop_table, new_bpmn[EXPRESSION], dbc.Alert(f"{filename} uploaded successfully", color="success", dismissable=True)

        except Exception as e:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, dbc.Alert(f"Upload error: {e}", color="danger", dismissable=True)
