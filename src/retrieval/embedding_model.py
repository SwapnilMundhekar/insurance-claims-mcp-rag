import os
from typing import Any

import requests


DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"


class LocalEmbeddingModel:
    """
    Local embedding wrapper using Ollama.

    This avoids PyTorch/SentenceTransformers dependency issues on Windows.
    """

    def __init__(
        self,
        model_name: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.model_name = model_name or os.getenv("OLLAMA_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)).rstrip("/")
        self.embed_url = f"{self.base_url}/api/embed"

    def _embed(self, input_text: str | list[str]) -> list[list[float]]:
        """
        Calls Ollama's local embedding endpoint.

        input_text can be a single string or a list of strings.
        """
        payload: dict[str, Any] = {
            "model": self.model_name,
            "input": input_text,
        }

        response = requests.post(self.embed_url, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()

        if "embeddings" not in data:
            raise ValueError(f"Ollama embedding response missing 'embeddings': {data}")

        return data["embeddings"]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embeds document chunks in small batches.

        texts: list of chunk texts.
        returns: list of embedding vectors.
        """
        all_embeddings: list[list[float]] = []
        batch_size = 16

        for start_index in range(0, len(texts), batch_size):
            end_index = start_index + batch_size
            batch = texts[start_index:end_index]

            print(f"Embedding batch {start_index + 1} to {min(end_index, len(texts))} of {len(texts)}")
            batch_embeddings = self._embed(batch)
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    def embed_query(self, query: str) -> list[float]:
        """
        Embeds one search query.

        query: user question or search phrase.
        returns: one embedding vector.
        """
        embeddings = self._embed(query)

        if not embeddings:
            raise ValueError("No embedding returned for query.")

        return embeddings[0]
