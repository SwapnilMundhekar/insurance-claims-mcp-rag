import json
from pathlib import Path
from typing import Any

import numpy as np


def create_vector_store_dir(vector_db_dir: Path) -> Path:
    vector_db_dir = Path(vector_db_dir)
    vector_db_dir.mkdir(parents=True, exist_ok=True)
    return vector_db_dir


def normalize_embeddings(embeddings: list[list[float]]) -> np.ndarray:
    matrix = np.array(embeddings, dtype=np.float32)

    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0

    return matrix / norms


def save_vector_store(
    vector_db_dir: Path,
    chunks: list[dict[str, Any]],
    embeddings: list[list[float]],
) -> None:
    vector_db_dir = create_vector_store_dir(vector_db_dir)

    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings must have the same length")

    normalized_embeddings = normalize_embeddings(embeddings)

    chunks_path = vector_db_dir / "chunks.json"
    embeddings_path = vector_db_dir / "embeddings.npy"

    with chunks_path.open("w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)

    np.save(embeddings_path, normalized_embeddings)

    print(f"Saved chunks to: {chunks_path}", flush=True)
    print(f"Saved embeddings to: {embeddings_path}", flush=True)


def load_vector_store(vector_db_dir: Path) -> tuple[list[dict[str, Any]], np.ndarray]:
    vector_db_dir = Path(vector_db_dir)

    chunks_path = vector_db_dir / "chunks.json"
    embeddings_path = vector_db_dir / "embeddings.npy"

    if not chunks_path.exists():
        raise FileNotFoundError(f"Missing chunks file: {chunks_path}")

    if not embeddings_path.exists():
        raise FileNotFoundError(f"Missing embeddings file: {embeddings_path}")

    with chunks_path.open("r", encoding="utf-8") as file:
        chunks = json.load(file)

    embeddings = np.load(embeddings_path)

    return chunks, embeddings


def search_vector_store(
    vector_db_dir: Path,
    query_embedding: list[float],
    top_k: int = 5,
    where: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    chunks, embeddings = load_vector_store(vector_db_dir)

    query_vector = np.array(query_embedding, dtype=np.float32)
    query_norm = np.linalg.norm(query_vector)

    if query_norm == 0:
        raise ValueError("Query embedding has zero norm.")

    query_vector = query_vector / query_norm

    scores = embeddings @ query_vector

    ranked_indices = np.argsort(scores)[::-1]

    results: list[dict[str, Any]] = []

    for index in ranked_indices:
        chunk = chunks[int(index)]

        if where:
            should_keep = True

            for key, expected_value in where.items():
                if chunk.get(key) != expected_value:
                    should_keep = False
                    break

            if not should_keep:
                continue

        results.append(
            {
                "score": float(scores[int(index)]),
                "chunk": chunk,
            }
        )

        if len(results) >= top_k:
            break

    return results
