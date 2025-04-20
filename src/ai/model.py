from datetime import timedelta

from pydantic import BaseModel

chat_histories = {}
SESSION_TIMEOUT = timedelta(days=1)


class LLMChatRequest(BaseModel):
    bpmn: dict
    message: str
    session_id: str | None = None
    reset: bool = False
    url: str = "http://localhost:1234/v1"
    api_key: str = "lm-studio"
    model: str = "deepseek-r1-distill-llama-8b"
    temperature: float = 0.7
    verbose: bool = False
