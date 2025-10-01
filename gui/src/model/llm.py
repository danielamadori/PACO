import uuid
import requests
from gui.src.env import extract_nodes, SESE_PARSER, EXPRESSION, IMPACTS, IMPACTS_NAMES, H
from gui.src.model.etl import filter_bpmn

EXPECTED_FIELDS = {"bpmn", "message", "session_id"}

SESSION_ID = str(uuid.uuid4())

def llm_response(bpmn_store: dict, user_message: str) -> dict:
	tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
	bpmn = filter_bpmn(bpmn_store, tasks, choices, natures, loops)

	converted = {}
	for task in tasks:
		impact = bpmn[IMPACTS][task]
		converted[task] = dict(zip(bpmn[IMPACTS_NAMES], impact))
	bpmn[IMPACTS] = converted

	payload = {
		"bpmn": bpmn,
		"message": user_message,
		"session_id": SESSION_ID,
		"max_attempts": 3,
	}

	try:
		response = requests.post("http://localhost:8000/llm_bpmn_chat", json=payload)
		if not response.ok:
			raise RuntimeError(f"API Error [{response.status_code}]: {response.text}")

		data = response.json()
		missing = EXPECTED_FIELDS - data.keys()
		if missing:
			raise ValueError(f"Missing fields in response: {missing}")

		return data["message"], data["bpmn"]

	except Exception as e:
		return f"Error: {str(e)}", bpmn_store
