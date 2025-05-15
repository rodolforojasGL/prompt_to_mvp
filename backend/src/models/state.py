from typing import List
from typing_extensions import TypedDict


class architect_code_review_graph_state(TypedDict):
    error: bool
    messages: List
    generation: str
    iterations: int
    requirements: str
    specs: str
    confidence_score: int