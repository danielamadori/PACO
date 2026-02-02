"""
Chat Actions Module
Handles LLM response processing logic, separated from Dash callbacks.
"""
import dash
from gui.src.model.etl import load_bpmn_dot
from gui.src.model.llm import llm_response
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from gui.src.env import EXPRESSION, SESE_PARSER, extract_nodes


def resolve_llm_response(pending_id, history, bpmn_store, bound_store, 
                         provider, model_choice, custom_model, api_key):
    """
    Process LLM response and update BPMN model.
    
    Note (Bug #3 - By Design): The LLM generates a complete new BPMN model.
    This will REPLACE the current bpmn-store entirely, not merge with it.
    
    Returns tuple of 10 values:
    (chat_history, pending_message, bpmn_store, bound_store, bpmn_svg,
     impacts_table, durations_table, choices_table, natures_table, loops_table)
    """
    NO_UPDATE = dash.no_update
    
    if not pending_id or not history:
        return (NO_UPDATE,) * 10
    
    replaced = False
    msg_index = -1
    
    for i in range(len(history) - 1, -1, -1):
        if history[i].get('id') == pending_id:
            history[i]['text'], new_bpmn = llm_response(
                bpmn_store,
                history[i - 1]['text'],
                provider,
                model_choice,
                custom_model,
                api_key,
            )
            del history[i]['id']
            replaced = True
            msg_index = i
            break

    if not replaced:
        return (NO_UPDATE,) * 10

    # Default no-updates
    tasks_impacts_table = NO_UPDATE
    tasks_duration_table = NO_UPDATE
    choices_table = NO_UPDATE
    natures_table = NO_UPDATE
    loops_table = NO_UPDATE
    bpmn_dot = NO_UPDATE

    if EXPRESSION not in new_bpmn:
        history[msg_index]['text'] += "\nNo expression found in the BPMN"
        return history, None, bpmn_store, bound_store, bpmn_dot, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table

    new_bpmn[EXPRESSION] = new_bpmn[EXPRESSION].replace("\n", "").replace("\t", "").strip().replace(" ", "")
    if new_bpmn[EXPRESSION] == '':
        history[msg_index]['text'] += "\nEmpty expression found in the BPMN"
        return history, None, bpmn_store, bound_store, bpmn_dot, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table

    try:
        SESE_PARSER.parse(new_bpmn[EXPRESSION])
    except Exception as e:
        history[msg_index]['text'] += f"\nParsing error: {str(e)}"
        return history, None, bpmn_store, bound_store, bpmn_dot, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table

    tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(new_bpmn[EXPRESSION]))
    tasks_impacts_table = create_tasks_impacts_table(new_bpmn, tasks)
    tasks_duration_table = create_tasks_duration_table(new_bpmn, tasks)
    choices_table = create_choices_table(new_bpmn, choices)
    natures_table = create_natures_table(new_bpmn, natures)
    loops_table = create_loops_table(new_bpmn, loops)

    try:
        bpmn_dot = load_bpmn_dot(new_bpmn)
        return history, None, new_bpmn, sync_bound_store_from_bpmn(new_bpmn, bound_store), bpmn_dot, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table
    except Exception as exception:
        history[msg_index]['text'] += f"\nProcessing bpmn image error: {str(exception)}"
        return history, None, new_bpmn, sync_bound_store_from_bpmn(new_bpmn, bound_store), bpmn_dot, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table
