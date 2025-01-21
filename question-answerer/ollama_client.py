import os
import requests
from typing_extensions import List, TypedDict


OLLAMA_URL = os.getenv("OLLAMA_SERVICE_URL")

class OllamaResponse(TypedDict):
    model: str
    created_at: str
    response: str
    done: bool
    done_reason: str
    context: List[int]
    total_duration: int
    load_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int


def prompt_ollama(prompt: str) -> OllamaResponse:
    data = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(f"{OLLAMA_URL}/api/generate", json=data)
    response.raise_for_status()
    return response.json()
