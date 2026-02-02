"""
StoreManager - COMPLETE Centralized State Management
FINAL VERSION: Handles ALL store mutations
NO allow_duplicate - StoreManager is the SOLE writer!
"""
import dash
from dash import Output, Input, State, ALL, ctx, no_update
import dash_bootstrap_components as dbc
from gui.src.model.etl import load_bpmn_dot
from gui.src.env import DURATIONS, EXPRESSION, BOUND

# Action Modules
from gui.src.model.actions.duration_actions import update_durations_logic
from gui.src.model.actions.impact_actions import update_impacts_logic
from gui.src.model.actions.gateway_actions import update_gateway_logic
from gui.src.model.actions.column_actions import add_impact_column_logic, remove_impact_column_logic
from gui.src.model.actions.chat_actions import resolve_llm_response
from gui.src.model.actions.expression_actions import evaluate_expression_logic
from gui.src.model.actions.upload_actions import upload_json_bpmn_logic
from gui.src.model.actions.simulation_actions import step_simulation_logic, refresh_petri_logic
from gui.src.model.actions.bound_actions import update_bound_logic, update_bound_from_selection_logic
from gui.src.model.actions.strategy_actions import find_strategy_logic
from gui.src.model.actions.example_load_actions import load_example_logic
from gui.src.model.actions.reset_actions import reset_chat_logic, acknowledge_reset_logic

# Total outputs: 18
OUTPUT_COUNT = 18


def register_store_manager_callbacks(callback_provider):
    """
    FINAL StoreManager: Handles ALL mutations.
    18 Outputs - No Duplicates
    """
    @callback_provider(
        # === OUTPUTS (18 Total) ===
        Output('bpmn-store', 'data'),                                    # 0
        Output({"type": "bpmn-svg-store", "index": "main"}, "data"),     # 1
        Output({"type": "petri-svg-store", "index": "main"}, "data"),    # 2
        Output('simulation-store', 'data'),                               # 3
        Output('bound-store', 'data'),                                    # 4
        Output('bpmn-alert', 'children'),                                 # 5
        Output('task-impacts-table', 'children'),                         # 6
        Output('task-durations-table', 'children'),                       # 7
        Output('choice-table', 'children'),                               # 8
        Output('nature-table', 'children'),                               # 9
        Output('loop-table', 'children'),                                 # 10
        Output('chat-history', 'data'),                                   # 11
        Output('pending-message', 'data'),                                # 12
        Output('reset-trigger', 'data'),                                  # 13
        Output('expression-bpmn', 'value'),                               # 14
        Output('strategy_output', 'children'),                            # 15
        Output('strategy-alert', 'children'),                             # 16
        Output('chat-input', 'value'),                                    # 17

        # === INPUTS ===
        Input({'type': ALL, 'index': ALL}, 'value'),
        Input({'type': ALL, 'index': ALL}, 'n_clicks'),
        Input('add-impact-button', 'n_clicks'),
        Input('pending-message', 'data'),
        Input('generate-bpmn-btn', 'n_clicks'),
        Input('upload-data', 'contents'),
        Input('btn-back', 'n_clicks'),
        Input('btn-forward', 'n_clicks'),
        Input('view-mode', 'data'),
        Input('chat-clear-btn', 'n_clicks'),
        Input('reset-trigger', 'data'),
        Input('chat-send-btn', 'n_clicks'),
        Input('find-strategy-button', 'n_clicks'),
        Input('url', 'search'),

        # === STATES ===
        State({'type': ALL, 'index': ALL}, 'id'),
        State('new-impact-name', 'value'),
        State('bpmn-store', 'data'),
        State('bound-store', 'data'),
        State('chat-history', 'data'),
        State('expression-bpmn', 'value'),
        State('upload-data', 'filename'),
        State('simulation-store', 'data'),
        State({'type': 'gateway', 'id': ALL}, 'value'),
        State('time-input', 'value'),
        State('llm-provider', 'value'),
        State('llm-model', 'value'),
        State('llm-model-custom', 'value'),
        State('llm-api-key', 'value'),
        State('chat-input', 'value'),
        
        prevent_initial_call=True
    )
    def central_store_manager(
        all_values, all_clicks, add_btn, pending_msg, generate_btn,
        upload_contents, btn_back, btn_forward, view_mode,
        chat_clear, reset_trigger, chat_send, find_strategy, url_search,
        all_ids_state, new_impact_name, bpmn_store, bound_store, chat_history,
        expression_value, upload_filename, sim_store, gateway_values, time_step,
        llm_provider, llm_model, llm_model_custom, llm_api_key, chat_input
    ):
        trigger = ctx.triggered_id
        if not trigger:
            return (no_update,) * OUTPUT_COUNT
        
        def no_updates():
            return (no_update,) * OUTPUT_COUNT

        # ========= CHAT CLEAR =========
        if trigger == 'chat-clear-btn':
            res = reset_chat_logic()
            return (
                no_update, no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, no_update,
                res[0], res[1], res[2], no_update, no_update, no_update, no_update
            )

        # ========= RESET TRIGGER =========
        if trigger == 'reset-trigger':
            res = acknowledge_reset_logic(reset_trigger)
            if res is None:
                return no_updates()
            return (
                no_update, no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, res, no_update, no_update, no_update, no_update
            )

        # ========= CHAT SEND =========
        if trigger == 'chat-send-btn':
            if not chat_input or not chat_input.strip():
                return no_updates()
            import uuid
            loading_id = str(uuid.uuid4())
            history = chat_history or []
            history.append({'type': 'user', 'text': chat_input.strip()})
            history.append({'type': 'ai', 'text': '...', 'id': loading_id})
            return (
                no_update, no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, no_update,
                history, loading_id, no_update, no_update, no_update, no_update, ''
            )

        # ========= FIND STRATEGY =========
        if trigger == 'find-strategy-button':
            res = find_strategy_logic(bpmn_store, bound_store)
            # res: (output, alert)
            return (
                no_update, no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, res[0], res[1], no_update
            )

        # ========= EXAMPLE LOAD =========
        if trigger == 'url':
            res = load_example_logic(url_search, bound_store)
            # res: 10 values (bpmn, bound, svg, 5 tables, expr, alert)
            return (
                res[0], res[2], no_update, no_update, res[1], res[9],
                res[3], res[4], res[5], res[6], res[7],
                no_update, no_update, no_update, res[8], no_update, no_update, no_update
            )

        # ========= UPLOAD =========
        if trigger == 'upload-data':
            res = upload_json_bpmn_logic(upload_contents, upload_filename, bound_store)
            # res: 12 values
            return (
                res[0], res[2], res[3], res[4], res[1], res[11],
                res[5], res[6], res[7], res[8], res[9],
                no_update, no_update, no_update, res[10], no_update, no_update, no_update
            )

        # ========= GENERATE BPMN =========
        if trigger == 'generate-bpmn-btn':
            res = evaluate_expression_logic(expression_value, bpmn_store, bound_store)
            # res: 11 values
            return res + (no_update,) * 7

        # ========= CHAT PENDING MESSAGE =========
        if trigger == 'pending-message':
            res = resolve_llm_response(
                pending_msg, chat_history, bpmn_store, bound_store,
                llm_provider, llm_model, llm_model_custom, llm_api_key
            )
            return (
                res[2], res[4], no_update, no_update, res[3], no_update,
                res[5], res[6], res[7], res[8], res[9],
                res[0], res[1], no_update, no_update, no_update, no_update, no_update
            )

        # ========= SIMULATION CONTROLS =========
        if trigger == 'btn-back':
            sim_res = step_simulation_logic(-1, bpmn_store, gateway_values, sim_store, None, None, time_step, bound_store)
            return (
                no_update, sim_res[1], sim_res[2], sim_res[0], no_update, no_update,
                no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, no_update, no_update, no_update
            )

        if trigger == 'btn-forward':
            sim_res = step_simulation_logic(1, bpmn_store, gateway_values, sim_store, None, None, time_step, bound_store)
            return (
                no_update, sim_res[1], sim_res[2], sim_res[0], no_update, no_update,
                no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, no_update, no_update, no_update
            )

        if trigger == 'view-mode':
            petri = refresh_petri_logic(view_mode, bpmn_store)
            return (
                no_update, no_update, petri, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, no_update, no_update, no_update
            )

        # ========= ADD COLUMN =========
        if trigger == 'add-impact-button':
            res = add_impact_column_logic(new_impact_name, bpmn_store, bound_store)
            if res[0] is no_update:
                return (no_update,) * 5 + (res[3],) + (no_update,) * 12
            return (res[0], res[1], no_update, no_update, res[2], res[3], res[4]) + (no_update,) * 11

        # ========= PATTERN MATCHING =========
        if isinstance(trigger, dict):
            t_type = trigger.get('type')
            t_index = trigger.get('index')
            
            if t_type and t_type.startswith('impact-'):
                try:
                    trigger_idx = next(i for i, v in enumerate(all_ids_state) 
                                       if v['type'] == t_type and v['index'] == t_index)
                    val = all_values[trigger_idx]
                    res = update_impacts_logic(trigger, val, bpmn_store)
                    return (res[0], res[1], no_update, no_update, no_update, res[2]) + (no_update,) * 12
                except StopIteration:
                    return no_updates()

            if t_type in ['choice-delay', 'nature-prob', 'loop-prob', 'loop-round']:
                try:
                    trigger_idx = next(i for i, v in enumerate(all_ids_state) 
                                       if v['type'] == t_type and v['index'] == t_index)
                    val = all_values[trigger_idx]
                    res = update_gateway_logic(trigger, val, bpmn_store)
                    return (res[0], res[1], no_update, no_update, no_update, res[2]) + (no_update,) * 12
                except:
                    pass

            if t_type == 'remove-impact':
                res = remove_impact_column_logic(trigger, bpmn_store, bound_store)
                return (res[0], res[1], no_update, no_update, res[2], res[3], res[4]) + (no_update,) * 11
            
            if t_type in ['min-duration', 'max-duration']:
                try:
                    trigger_idx = next(i for i, v in enumerate(all_ids_state) 
                                       if v['type'] == t_type and v['index'] == t_index)
                    val = all_values[trigger_idx]
                    task = t_index
                    if DURATIONS not in bpmn_store:
                        bpmn_store[DURATIONS] = {}
                    current_pair = list(bpmn_store.get(DURATIONS, {}).get(task, [0, 1]))
                    if t_type == 'min-duration':
                        current_pair[0] = val or 0
                    else:
                        current_pair[1] = val or 1
                    bpmn_store[DURATIONS][task] = current_pair
                    bpmn_dot = load_bpmn_dot(bpmn_store)
                    return (bpmn_store, bpmn_dot, no_update, no_update, no_update, '') + (no_update,) * 12
                except Exception as e:
                    return (no_update, no_update, no_update, no_update, no_update, dbc.Alert(str(e), color="danger")) + (no_update,) * 12

            if t_type == 'bound-input':
                res = update_bound_logic(trigger, all_values, all_ids_state, bound_store)
                if res is not no_update:
                    return (no_update, no_update, no_update, no_update, res, no_update) + (no_update,) * 12
                return no_updates()

            if t_type == 'selected_bound':
                table_type = trigger.get('table')
                res = update_bound_from_selection_logic(trigger, all_clicks, bound_store, bpmn_store, table_type)
                if res is not no_update:
                    return (no_update, no_update, no_update, no_update, res, no_update) + (no_update,) * 12
                return no_updates()

        return no_updates()
