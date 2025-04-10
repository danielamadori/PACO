import dash
from dash import Output, Input, State
from src.model.bpmn import validate_expression_and_update
from src.env import EXPRESSION


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
        bpmn_store, bpmn_dot, alert = validate_expression_and_update(current_expression, bpmn_store)
        if bpmn_dot is None:
            bpmn_dot = dash.no_update

        return bpmn_store, bpmn_dot, alert


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
