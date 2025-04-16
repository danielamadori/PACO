import dash
from dash import Output, Input, State
import dash_bootstrap_components as dbc
from src.controller.db import load_bpmn_dot
from src.env import EXPRESSION, SESE_PARSER, extract_nodes
from view.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from view.sidebar.bpmn_tab.table.tasks_table import create_tasks_table


def register_expression_callbacks(expression_callbacks):
    @expression_callbacks(
        Output('bpmn-store', 'data'),
        Output("dot-store", "data"),
        Output('bpmn-alert', 'children'),
        Output('task-table', 'children', allow_duplicate=True),
        Output('choice-table', 'children'),
        Output('nature-table', 'children'),
        Output('loop-table', 'children'),
        Input('expression-bpmn', 'value'),
        State('bpmn-store', 'data'),
        prevent_initial_call=True
    )
    def evaluate_expression(current_expression, bpmn_store):
        alert = ''
        tasks_table = dash.no_update
        choices_table = dash.no_update
        natures_table = dash.no_update
        loops_table = dash.no_update

        if current_expression is None:
            return dash.no_update, dash.no_update, alert, tasks_table, choices_table, natures_table, loops_table

        current_expression = current_expression.replace("\n", "").replace("\t", "").strip().replace(" ", "")
        if current_expression == '':
            return bpmn_store, dash.no_update, dbc.Alert("The expression is empty.", color="warning", dismissable=True), tasks_table, choices_table, natures_table, loops_table

        if current_expression != bpmn_store.get(EXPRESSION, ''):
            try:
                SESE_PARSER.parse(current_expression)
            except Exception as e:
                return dash.no_update, dash.no_update, dbc.Alert(f"Parsing error: {str(e)}", color="danger", dismissable=True), tasks_table, choices_table, natures_table, loops_table
            bpmn_store[EXPRESSION] = current_expression

        if bpmn_store[EXPRESSION] == '':
            return dash.no_update, dash.no_update, alert, tasks_table, choices_table, natures_table, loops_table


        tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))

        tasks_table = create_tasks_table(bpmn_store, tasks)
        choices_table = create_choices_table(bpmn_store, choices)
        natures_table = create_natures_table(bpmn_store, natures)
        loops_table = create_loops_table(bpmn_store, loops)

        try:
            bpmn_dot = load_bpmn_dot(bpmn_store[EXPRESSION])

            return bpmn_store, {"bpmn" : bpmn_dot}, alert, tasks_table, choices_table, natures_table, loops_table
        except Exception as exception:
            alert = dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

        return bpmn_store, dash.no_update, alert, tasks_table, choices_table, natures_table, loops_table


    @expression_callbacks(
        Output('expression-bpmn', 'value', allow_duplicate=True),
        Input('bpmn-store', 'data'),
        State('expression-bpmn', 'value'),
        prevent_initial_call='initial_duplicate'
    )
    def sync_input_with_store(store_data, current_value):
        if not current_value:#if empty
            return store_data[EXPRESSION]
        return dash.no_update
