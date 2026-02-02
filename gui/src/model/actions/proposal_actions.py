"""
Proposal Actions Module
Handles logic for Accepting or Rejecting BPMN proposals.
"""
from dash import no_update
from gui.src.model.etl import reset_simulation_state
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from gui.src.env import EXPRESSION, SESE_PARSER, extract_nodes

def accept_proposal_logic(proposed_bpmn, history, bound_store):
    """
    Promote proposed BPMN to active BPMN, reset simulation, clear proposal.
    """
    if not proposed_bpmn or not history:
        return (no_update,) * 13

    # Update history: remove buttons, add "Accepted" status
    new_history = [msg.copy() for msg in history]
    if new_history:
        last_msg = new_history[-1]
        if last_msg.get('is_proposal'):
            del last_msg['is_proposal']
            last_msg['text'] += "\n\n✅ **Proposal Accepted**"

    # Generate all artifacts (Sim, SVG, Tables)
    bpmn_dot, petri_svg, sim_data = reset_simulation_state(proposed_bpmn, bound_store)
    
    tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(proposed_bpmn[EXPRESSION]))
    
    return (
        None,           # proposed-bpmn-store (Clear it)
        no_update,      # pending-message
        proposed_bpmn,  # bpmn-store (Update)
        sync_bound_store_from_bpmn(proposed_bpmn, bound_store), # bound-store
        bpmn_dot,       # bpmn-svg
        petri_svg,      # petri-svg
        sim_data,       # sim-store
        create_tasks_impacts_table(proposed_bpmn, tasks),
        create_tasks_duration_table(proposed_bpmn, tasks),
        create_choices_table(proposed_bpmn, choices),
        create_natures_table(proposed_bpmn, natures),
        create_loops_table(proposed_bpmn, loops),
        new_history     # chat-history
    )

def reject_proposal_logic(history):
    """
    Clear proposal, update history.
    """
    if not history:
        return (no_update,) * 13

    new_history = [msg.copy() for msg in history]
    if new_history:
        last_msg = new_history[-1]
        if last_msg.get('is_proposal'):
            del last_msg['is_proposal']
            last_msg['text'] += "\n\n❌ **Proposal Rejected**"

    return (
        None,           # proposed-bpmn-store (Clear it)
        no_update,      # pending-message
        no_update,      # bpmn-store
        no_update,      # bound-store
        no_update,      # bpmn-svg
        no_update,      # petri-svg
        no_update,      # sim-store
        no_update, no_update, no_update, no_update, no_update, # Tables
        new_history     # chat-history
    )
