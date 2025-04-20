
from typing import TypedDict, Dict, List

class BPMNDict(TypedDict):
    expression: str
    h: int
    impacts: Dict[str, List[float]]
    durations: Dict[str, List[int]]
    impacts_names: List[str]
    probabilities: Dict[str, float]
    delays: Dict[str, float]
    loop_round: Dict[str, int]
    loop_probability: Dict[str, float]
