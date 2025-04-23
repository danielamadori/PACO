import random
import time
import uuid
import requests
from env import extract_nodes, SESE_PARSER, EXPRESSION, IMPACTS, IMPACTS_NAMES
from model.etl import filter_bpmn

EXPECTED_FIELDS = {"bpmn", "message", "session_id"}

SESSION_ID = str(uuid.uuid4())

def llm_response(bpmn_store: dict, user_message: str) -> dict:
	tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
	bpmn = filter_bpmn(bpmn_store, tasks, choices, natures, loops)

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

		#, data["session_id"]
		named_impacts = {
			name: {
				impact_name: value
				for impact_name, value in zip(data["bpmn"][IMPACTS_NAMES], vector)
			}
			for name, vector in data["bpmn"][IMPACTS].items()
		}

		data["bpmn"][IMPACTS] = named_impacts
		#TODO sync to GUI
		return data["message"], data["bpmn"]

	except Exception as e:
		data["message"] = f"Error: {str(e)}", data["bpmn"]
