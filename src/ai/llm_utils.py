import json
import re

import requests
from langchain_openai import ChatOpenAI
from src.ai.prompt import define_role, examples_bpmn
from src.utils.check_syntax import check_bpmn_syntax

CHAT_MEMORY = {}

def build_few_shot_prompt(bpmn_dict: dict, message: str) -> str:
    examples = "\n".join([
        f"User: {ex['input'].strip()}\nTranslation: {ex['answer'].strip()}"
        for ex in examples_bpmn
    ])

    return (
        f"{define_role}\n"
        f"Here are a few examples:\n"
        f"{examples}\n\n"
        f"Now respond with a valid JSON object in this format:\n"
        f"{{ \"bpmn\": <updated_bpmn_dict>, \"message\": <explanation> }}\n"
        f"Respond ONLY with JSON. No comments. No code blocks. No explanations outside the JSON."
        f"\n\nInstruction: {message}\n"
        f"Current BPMN:\n{json.dumps(bpmn_dict, indent=2)}"
    )

def build_followup_prompt(history: list, message: str) -> str:
    prompt_lines = []
    for msg in history:
        prompt_lines.append(f"User: {msg['user']}")
        prompt_lines.append(f"Assistant: {msg['assistant']['message']}")
    prompt_lines.append(f"User: {message}")
    return "\n".join(prompt_lines)

def run_llm_on_bpmn(
    bpmn_dict: dict,
    message: str,
    session_id: str,
    max_attempts: int
) -> dict:
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=max_attempts)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {
            "bpmn": bpmn_dict,
            "message": "I'm offline"
        }

    if session_id not in CHAT_MEMORY:
        CHAT_MEMORY[session_id] = []

    is_first_message = len(CHAT_MEMORY[session_id]) == 0
    prompt = build_few_shot_prompt(bpmn_dict, message) if is_first_message else build_followup_prompt(CHAT_MEMORY[session_id], message)

    llm = ChatOpenAI(
        openai_api_base="http://localhost:1234/v1",
        openai_api_key="lm-studio",
        model="deepseek-r1-distill-llama-8b",
        temperature=0.7,
        verbose=False
    )

    for attempt in range(max_attempts):
        try:
            response = llm.invoke(prompt)
            text = response.content.strip()

            # Clean known formatting problems
            text = re.sub(r"```json|```", "", text)
            text = re.sub(r"(const|let|var)\s+\w+\s*=\s*", "", text)
            text = re.sub(r"^[^{]*", "", text)
            text = re.sub(r"[^}]*$", "", text)

            parsed = json.loads(text)

            if "bpmn" not in parsed or "message" not in parsed:
                raise ValueError("Missing keys in LLM response")

            check_bpmn_syntax(parsed["bpmn"])

            CHAT_MEMORY[session_id].append({
                "user": message,
                "assistant": parsed
            })

            return parsed

        except Exception as e:
            if attempt == max_attempts - 1:
                raise RuntimeError(f"LLM failed to produce valid BPMN after {max_attempts} attempts: {e}")
            continue
