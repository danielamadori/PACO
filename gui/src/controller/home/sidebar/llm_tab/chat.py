from dash import Input, Output, State
import random, dash

from gui.src.controller.home.sidebar.llm_tab.effects import register_llm_effects_callbacks
from gui.src.controller.home.sidebar.llm_tab.model_selector import register_llm_model_selector_callbacks
from gui.src.controller.home.sidebar.llm_tab.reset import register_llm_reset_callbacks
from gui.src.model.etl import load_bpmn_dot
from gui.src.model.llm import llm_response
from gui.src.view.home.sidebar.llm_tab.chat import get_message
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from gui.src.env import EXPRESSION, SESE_PARSER, extract_nodes


def register_llm_callbacks(callback, clientside_callback):
	register_llm_reset_callbacks(callback)
	register_llm_effects_callbacks(callback, clientside_callback)
	register_llm_model_selector_callbacks(callback)

	# ------------------------------------------------------------------
	# NOTE: send_message callback migrated to store_manager.py
	# The chat-send-btn trigger is now handled centrally.
	# ------------------------------------------------------------------

	# ------------------------------------------------------------------
	# NOTE: resolve_response callback has been migrated to store_manager.py
	# The logic is now in gui/src/model/actions/chat_actions.py
	# Keeping this comment block for reference.
	# ------------------------------------------------------------------
	# @callback(
	# 	Output('chat-history', 'data', allow_duplicate=True),
	# 	... (see store_manager.py for full implementation)
	# )
	# def resolve_response(...): ...
	# ------------------------------------------------------------------


	@callback(
		Output('chat-output', 'children'),
		Input('chat-history', 'data'),
		prevent_initial_call=True
	)
	def render_chat(history):
		if not history:
			return []
		return [ get_message(msg) for msg in history ]

