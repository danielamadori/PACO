import dash
from dash import Output, Input, State
import dash_bootstrap_components as dbc
from dash import ctx
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.model.etl import reset_simulation_state
from gui.src.env import EXPRESSION, SESE_PARSER, extract_nodes, IMPACTS_NAMES, BOUND, IMPACTS
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table


def register_expression_callbacks(expression_callbacks):
    @expression_callbacks(
        Output('bpmn-store', 'data'),
        Output({"type": "bpmn-svg-store", "index": "main"}, "data"),
        Output({"type": "petri-svg-store", "index": "main"}, "data"),
        Output("simulation-store", "data", allow_duplicate=True),
        Output("bound-store", "data", allow_duplicate=True),
        Output('bpmn-alert', 'children'),
        Output('task-impacts-table', 'children', allow_duplicate=True),
        Output('task-durations-table', 'children'),
        Output('choice-table', 'children'),
        Output('nature-table', 'children'),
        Output('loop-table', 'children'),
        Input('generate-bpmn-btn', 'n_clicks'),
        State('expression-bpmn', 'value'),
        State('bpmn-store', 'data'),
        State('bound-store', 'data'),
        prevent_initial_call=True
    )
    def evaluate_expression(n_clicks, current_expression, bpmn_store, bound_store):
        if ctx.triggered_id != 'generate-bpmn-btn':
             raise dash.exceptions.PreventUpdate

        alert = ''
        tasks_impacts_table = dash.no_update
        tasks_duration_table = dash.no_update
        choices_table = dash.no_update
        natures_table = dash.no_update
        loops_table = dash.no_update

        if current_expression is None:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, alert, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table

        current_expression = current_expression.replace("\n", "").replace("\t", "").strip().replace(" ", "")
        if current_expression == '':
            return bpmn_store, dash.no_update, dash.no_update, dash.no_update, sync_bound_store_from_bpmn(bpmn_store, bound_store), dbc.Alert("The expression is empty", color="warning", dismissable=True), tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table

        if current_expression != bpmn_store.get(EXPRESSION, ''):
            try:
                SESE_PARSER.parse(current_expression)
            except Exception as e:
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dbc.Alert(f"Parsing error: {str(e)}", color="danger", dismissable=True), tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table
            bpmn_store[EXPRESSION] = current_expression


        if bpmn_store[EXPRESSION] == '':
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, sync_bound_store_from_bpmn(bpmn_store, bound_store), alert, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table

        tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))

        if not bpmn_store[IMPACTS_NAMES]:
            impacts_names = 'kWh'
            bound_store[BOUND][impacts_names]= 0.0
            bpmn_store[IMPACTS_NAMES] = [impacts_names]

        tasks_impacts_table = create_tasks_impacts_table(bpmn_store, tasks)
        tasks_duration_table = create_tasks_duration_table(bpmn_store, tasks)
        choices_table = create_choices_table(bpmn_store, choices)
        natures_table = create_natures_table(bpmn_store, natures)
        loops_table = create_loops_table(bpmn_store, loops)

        try:
            updated_bound_store = sync_bound_store_from_bpmn(bpmn_store, bound_store)
            bpmn_dot, petri_svg, sim_data = reset_simulation_state(bpmn_store, updated_bound_store)

            return bpmn_store, bpmn_dot, petri_svg, sim_data, updated_bound_store, alert, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table
        except Exception as exception:
            alert = dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

        return bpmn_store, dash.no_update, dash.no_update, dash.no_update, sync_bound_store_from_bpmn(bpmn_store, bound_store), alert, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table


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
