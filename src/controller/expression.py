import dash
from dash import Output, Input, State
import dash_bootstrap_components as dbc
from src.controller.db import load_bpmn_dot
from src.env import EXPRESSION, SESE_PARSER


def register_expression_callbacks(expression_callbacks):
    @expression_callbacks(
        Output('bpmn-store', 'data'),
        Output("dot-store", "data"),
        Output('bpmn-alert', 'children'),
        Input('input-bpmn', 'value'),
        State('bpmn-store', 'data'),
        prevent_initial_call=True
    )
    def update_expression(current_expression, bpmn_store):
        alert = ''
        if current_expression is None:
            return dash.no_update, dash.no_update, alert

        current_expression = current_expression.replace("\n", "").replace("\t", "").strip().replace(" ", "")
        if current_expression == '':
            return bpmn_store, dash.no_update, dbc.Alert("The expression is empty.", color="warning", dismissable=True)

        if current_expression != bpmn_store.get(EXPRESSION, ''):
            try:
                SESE_PARSER.parse(current_expression)
            except Exception as e:
                return dash.no_update, dash.no_update, dbc.Alert(f"Parsing error: {str(e)}", color="danger", dismissable=True)
            bpmn_store[EXPRESSION] = current_expression

        if bpmn_store[EXPRESSION] == '':
            return dash.no_update, dash.no_update, alert

        try:
            bpmn_dot = load_bpmn_dot(bpmn_store[EXPRESSION])
            return bpmn_store, {"bpmn" : bpmn_dot}, alert
        except Exception as exception:
            alert = dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

        return bpmn_store, dash.no_update, alert


    @expression_callbacks(
        Output('input-bpmn', 'value', allow_duplicate=True),
        Input('bpmn-store', 'data'),
        State('input-bpmn', 'value'),
        prevent_initial_call='initial_duplicate'
    )
    def sync_input_with_store(store_data, current_value):
        if not current_value:#if empty
            return store_data[EXPRESSION]
        return dash.no_update
