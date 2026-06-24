import os
from typing import Any

import requests


DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5:7b"


class OllamaChatClient:
    """
    Small client for calling a local Ollama chat model.

    This class keeps Ollama HTTP details away from the RAG service.
    """

    def __init__(
        self,
        model_name: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int = 180,
    ) -> None:
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)).rstrip("/")
        self.chat_url = f"{self.base_url}/api/chat"
        self.timeout_seconds = timeout_seconds

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> str:
        """
        Calls Ollama chat endpoint and returns assistant response text.
        """
        payload: dict[str, Any] = {
            "model": self.model_name,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        }

        response = requests.post(
            self.chat_url,
            json=payload,
            timeout=self.timeout_seconds,
        )

        response.raise_for_status()

        data = response.json()

        if "message" not in data or "content" not in data["message"]:
            raise ValueError(f"Unexpected Ollama response: {data}")

        return data["message"]["content"].strip()
