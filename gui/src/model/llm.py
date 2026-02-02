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
	# Allow empty API key for Gemini 2.5-flash-lite (system provides it)
	if provider in {"openai", "anthropic", "openrouter"} and not api_key:
		return f"Error: Missing API key for {provider}.", bpmn_store
	if provider == "gemini" and not api_key and model != "gemini-2.5-flash-lite":
		return f"Error: Missing API key for Gemini model {model}.", bpmn_store

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
		print(f"DEBUG: Sending LLM request to {URL_SERVER}llm_bpmn_chat")
		print(f"DEBUG: Payload keys: {list(payload.keys())}")
		print(f"DEBUG: Model: {model}, Provider: {provider}")
		
		response = requests.post(f"{URL_SERVER}llm_bpmn_chat", json=payload)
		
		print(f"DEBUG: Response Status: {response.status_code}")
		if not response.ok:
			print(f"DEBUG: Response Text: {response.text}")
			raise RuntimeError(f"API Error [{response.status_code}]: {response.text}")

		data = response.json()
		# print(f"DEBUG: Response Data keys: {list(data.keys())}")
		missing = EXPECTED_FIELDS - data.keys()
		if missing:
			raise ValueError(f"Missing fields in response: {missing}")

		return data["message"], data["bpmn"]

	except Exception as e:
		import traceback
		traceback.print_exc()
		return f"Error: {str(e)}", bpmn_store
