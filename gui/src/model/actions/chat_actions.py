"""
Chat Actions Module
Handles LLM response processing logic, separated from Dash callbacks.
"""
import dash
from gui.src.model.etl import load_bpmn_dot, reset_simulation_state
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
        return (NO_UPDATE,) * 13
    
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
        return (NO_UPDATE,) * 13

    # Default no-updates
    tasks_impacts_table = NO_UPDATE
    tasks_duration_table = NO_UPDATE
    choices_table = NO_UPDATE
    natures_table = NO_UPDATE
    loops_table = NO_UPDATE
    bpmn_dot = NO_UPDATE

    if EXPRESSION not in new_bpmn:
        history[msg_index]['text'] += "\nNo expression found in the BPMN"
        return history, None, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, None

    new_bpmn[EXPRESSION] = new_bpmn[EXPRESSION].replace("\n", "").replace("\t", "").strip().replace(" ", "")
    if new_bpmn[EXPRESSION] == '':
        history[msg_index]['text'] += "\nEmpty expression found in the BPMN"
        return history, None, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, None

    try:
        SESE_PARSER.parse(new_bpmn[EXPRESSION])
    except Exception as e:
        history[msg_index]['text'] += f"\nParsing error: {str(e)}"
        history[msg_index]['text'] += f"\nParsing error: {str(e)}"
        return history, None, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, NO_UPDATE, None

    # Proposal Mode: Do NOT generate tables or reset simulation yet.
    # Just validate parsing and return proposal.
    
    # Update History with Proposal Flag
    new_history = [msg.copy() for msg in history]
    if new_history:
        new_history[-1]['is_proposal'] = True
        new_history[-1]['text'] += "\n\n💡 **Proposal Ready**. Review and Accept."

    # Return 13 values:
    # 0: history
    # 1: pending
    # 2: bpmn_store (NO UPDATE)
    # 3: bound_store (NO UPDATE)
    # 4: bpmn_svg (NO UPDATE)
    # 5: petri_svg (NO UPDATE)
    # 6: sim_data (NO UPDATE)
    # 7-11: Tables (NO UPDATE)
    # 12: proposed_bpmn (NEW)

    return (
        new_history, 
        None, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE, 
        NO_UPDATE,
        new_bpmn # proposed_bpmn
    )
