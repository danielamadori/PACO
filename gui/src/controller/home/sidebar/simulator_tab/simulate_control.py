from dash import Input, Output, State, ctx, ALL, no_update

from gui.src.model.etl import (
    bpmn_snapshot_to_dot,
    dot_to_base64svg,
    update_bpmn_dot,
    load_execution_tree,
    set_actual_execution,
    execute_decisions,
    get_simulation_data,
)
from gui.src.model.execution_tree import get_prev_execution_node
from gui.src.env import EXPRESSION


def register_simulator_callbacks(callback):
    @callback(
        Output("btn-back", "disabled"),
        Output("btn-forward", "disabled"),
        Input("bpmn-store", "data"),
    )
    def toggle_simulation_controls(bpmn_store):
        is_disabled = not bpmn_store or bpmn_store.get(EXPRESSION, "") == ""
        return is_disabled, is_disabled

    @callback(
        Output("simulation-store", "data", allow_duplicate=True),
        Input("bpmn-store", "data"),
        State("simulation-store", "data"),
        State("bound-store", "data"),
        prevent_initial_call='initial_duplicate'
    )
    def reset_simulation_data(bpmn_store, sim_store, bound_store):
        if not bpmn_store:
            return no_update
        
        current_expr = bpmn_store.get(EXPRESSION)
        saved_expr = sim_store.get("expression") if sim_store else None
        
        if current_expr == saved_expr:
            return no_update

        if not current_expr:
            return {"expression": current_expr}

        data = get_simulation_data(bpmn_store, bound_store)
        data["expression"] = current_expr
        return data

    @callback(
        Output("simulation-store", "data", allow_duplicate=True),
        Output({"type": "bpmn-svg-store", "index": "main"}, 'data', allow_duplicate=True),
        Input("btn-back", "n_clicks"),
        Input("btn-forward", "n_clicks"),
        State("bpmn-store", "data"),
        State({"type": "gateway", "id": ALL}, "value"),
        State("simulation-store", "data"),
        State({"type": "bpmn-svg-store", "index": "main"}, 'data'),
        State("time-input", "value"),
        State("bound-store", "data"),
        prevent_initial_call=True
    )
    def run_simulation_on_step(btn_back_clicks, btn_forward_clicks, bpmn_store, gateway_values, sim_data, bpmn_svg_store, time_step, bound_store):
        try:
            with open("debug.log", "a") as f:
                f.write(f"DEBUG: run_simulation_on_step triggered. bound_store keys: {list(bound_store.keys()) if bound_store else 'None'}\n")
        except:
            pass

        triggered = ctx.triggered_id
        step = -1 if triggered == "btn-back" else 1 if triggered == "btn-forward" else 0

        # Default time_step to 1.0 if not provided
        if time_step is None or time_step <= 0:
            time_step = 1.0

        match (step):
            case -1:
                # Go back in the simulation
                execution_tree, actual_execution = load_execution_tree(bpmn_store)
                prev_exec_node = get_prev_execution_node(execution_tree, actual_execution)
                if prev_exec_node is None:
                    return sim_data, bpmn_svg_store

                set_actual_execution(bpmn_store, prev_exec_node['id'])
                bpmn_dot = bpmn_snapshot_to_dot(bpmn_store)
                dot_svg = dot_to_base64svg(bpmn_dot)
                update_bpmn_dot(bpmn_store, dot_svg)

                update_bpmn_dot(bpmn_store, dot_svg)

                data = get_simulation_data(bpmn_store, bound_store)
                data["expression"] = bpmn_store.get(EXPRESSION)
                return data, dot_svg
            case 1:
                # Go forward in the simulation with time_step
                new_sim_data = execute_decisions(bpmn_store, gateway_values, time_step=time_step, bound_store=bound_store)
                bpmn_dot = bpmn_snapshot_to_dot(bpmn_store)
                dot_svg = dot_to_base64svg(bpmn_dot)

                update_bpmn_dot(bpmn_store, dot_svg)

                new_sim_data["expression"] = bpmn_store.get(EXPRESSION)
                return new_sim_data, dot_svg
            case _:
                return sim_data, bpmn_svg_store
