from dash import Input, Output, State, ctx, ALL

from model.etl import bpmn_to_dot, dot_to_base64svg, update_bpmn_dot, load_execution_tree, set_actual_execution, \
    execute_decisions, get_simulation_data
from model.execution_tree import get_prev_execution_node


def register_simulator_callbacks(callback):
    @callback(
        Output("simulation-store", "data", allow_duplicate=True),
        Output({"type": "bpmn-svg-store", "index": "main"}, 'data', allow_duplicate=True),
        Input("btn-back", "n_clicks"),
        Input("btn-forward", "n_clicks"),
        State("bpmn-store", "data"),
        State({"type": "gateway", "id": ALL}, "value"),
        State("simulation-store", "data"),
        State({"type": "bpmn-svg-store", "index": "main"}, 'data'),
        prevent_initial_call=True
    )
    def run_simulation_on_step(btn_back_clicks, btn_forward_clicks, bpmn_store, gateway_values, sim_data, bpmn_svg_store):
        triggered = ctx.triggered_id
        step = -1 if triggered == "btn-back" else 1 if triggered == "btn-forward" else 0

        match (step):
            case -1:
                # Go back in the simulation
                execution_tree, actual_execution = load_execution_tree(bpmn_store)
                prev_exec_node = get_prev_execution_node(execution_tree, actual_execution)
                if prev_exec_node is None:
                    return sim_data, bpmn_svg_store

                set_actual_execution(bpmn_store, prev_exec_node['id'])
                bpmn_dot = bpmn_to_dot(bpmn_store)
                dot_svg = dot_to_base64svg(bpmn_dot)
                update_bpmn_dot(bpmn_store, dot_svg)

                return get_simulation_data(bpmn_store), dot_svg
            case 1:
                # Go forward in the simulation
                new_sim_data = execute_decisions(bpmn_store, gateway_values, step)
                bpmn_dot = bpmn_to_dot(bpmn_store)
                dot_svg = dot_to_base64svg(bpmn_dot)

                update_bpmn_dot(bpmn_store, dot_svg)

                return new_sim_data, dot_svg
            case _:
                return sim_data, bpmn_svg_store
