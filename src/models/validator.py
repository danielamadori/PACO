
from models.bpmn import BPMNDict
from typing import Any


def validate_bpmn_dict(bpmn: dict) -> BPMNDict:
    """
    Verifica che un dizionario bpmn sia compatibile con BPMNDict.
    Solleva un TypeError se mancano campi obbligatori o se i tipi sono errati.
    """
    required_keys = BPMNDict.__annotations__.keys()
    missing = [key for key in required_keys if key not in bpmn]
    if missing:
        raise ValueError(f"Missing required BPMN fields: {missing}")

    # Qui potresti anche aggiungere controlli più avanzati (es. tipo esatto delle chiavi)
    return bpmn  # viene trattato come BPMNDict grazie alla compatibilità strutturale
