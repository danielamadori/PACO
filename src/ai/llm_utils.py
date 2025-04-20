
import json
from langchain_openai import ChatOpenAI
from ai.prompt import define_role
from utils.check_syntax import check_bpmn_syntax

def run_llm_on_bpmn(
    bpmn_dict: dict,
    message: str,
    model: str = "phi-3.5-mini-instruct",
    temperature: float = 0.7,
    url: str = "http://localhost:1234/v1",
    api_key: str = "lm-studio",
    max_attempts: int = 3,
    verbose: bool = False
) -> dict:
    """
    Invoca un LLM per modificare un dizionario BPMN dato un messaggio utente.
    Ritorna un nuovo dizionario BPMN valido e un messaggio spiegato.

    Parameters:
    - bpmn_dict: dict BPMN iniziale
    - message: messaggio dell'utente
    - model, temperature, url, api_key: parametri LLM
    - max_attempts: numero massimo di retry in caso di output non valido
    """
    llm = ChatOpenAI(
        openai_api_base=url,
        openai_api_key=api_key,
        model=model,
        temperature=temperature,
        verbose=verbose
    )

    prompt = (
        f"{define_role}

"
        f"You are given the following BPMN JSON:
{json.dumps(bpmn_dict, indent=2)}

"
        f"Instruction: {message}

"
        f"Return ONLY a valid JSON with two keys:
"
        f"- 'bpmn': the updated BPMN dictionary
"
        f"- 'message': an explanation of the modification
"
    )

    for attempt in range(max_attempts):
        try:
            response = llm.invoke(prompt)
            text = response.content.strip()
            parsed = json.loads(text)

            if "bpmn" not in parsed or "message" not in parsed:
                raise ValueError("Missing keys in LLM output.")

            # Validazione BPMN
            check_bpmn_syntax(parsed["bpmn"])
            return parsed

        except Exception as e:
            if attempt == max_attempts - 1:
                raise RuntimeError(f"LLM failed to produce valid BPMN after {max_attempts} attempts: {e}")
            continue
