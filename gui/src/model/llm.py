import uuid

import requests

from gui.src.env import (
	URL_SERVER,
	extract_nodes,
	SESE_PARSER,
	EXPRESSION,
	IMPACTS,
	IMPACTS_NAMES,
	H,
	LLM_DEFAULT_MODEL_BY_PROVIDER,
	LLM_DEFAULT_PROVIDER,
)
from gui.src.model.etl import filter_bpmn

EXPECTED_FIELDS = {"bpmn", "message", "session_id"}

SESSION_ID = str(uuid.uuid4())


def _resolve_provider_model(
	provider: str | None,
	model: str | None,
	custom_model: str | None,
) -> tuple[str, str]:
	provider = (provider or LLM_DEFAULT_PROVIDER).strip()
	model = (model or LLM_DEFAULT_MODEL_BY_PROVIDER.get(provider, "")).strip()
	custom_model = (custom_model or "").strip()
	if custom_model:
		model = custom_model
	return provider, model


def llm_response(
	bpmn_store: dict,
	user_message: str,
	provider: str | None,
	model_choice: str | None,
	custom_model: str | None,
	api_key: str | None,
) -> dict:
	tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
	bpmn = filter_bpmn(bpmn_store, tasks, choices, natures, loops)

	converted = {}
	for task in tasks:
		impact = bpmn[IMPACTS][task]
		converted[task] = dict(zip(bpmn[IMPACTS_NAMES], impact))
	bpmn[IMPACTS] = converted
	provider, model = _resolve_provider_model(provider, model_choice, custom_model)
	if not model:
		return f"Error: Missing model for {provider}.", bpmn_store
	api_key = (api_key or "").strip()
	if provider in {"openai", "anthropic", "gemini", "openrouter"} and not api_key:
		return f"Error: Missing API key for {provider}.", bpmn_store

	payload = {
		"bpmn": bpmn,
		"message": user_message,
		"session_id": SESSION_ID,
		"max_attempts": 7,
		"provider": provider,
		"model": model,
		"api_key": api_key or None,
	}

	try:
		response = requests.post(f"{URL_SERVER}llm_bpmn_chat", json=payload)
		if not response.ok:
			raise RuntimeError(f"API Error [{response.status_code}]: {response.text}")

		data = response.json()
		missing = EXPECTED_FIELDS - data.keys()
		if missing:
			raise ValueError(f"Missing fields in response: {missing}")

		return data["message"], data["bpmn"]

	except Exception as e:
		return f"Error: {str(e)}", bpmn_store
