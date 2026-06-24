import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.retrieval.embedding_model import LocalEmbeddingModel
from src.retrieval.vector_store import save_vector_store


def main() -> None:
    load_dotenv()

    chunk_output_dir = Path(os.getenv("CHUNK_OUTPUT_DIR", "./data/chunks"))
    processed_output_dir = Path(os.getenv("PROCESSED_OUTPUT_DIR", "./data/processed"))
    vector_db_dir = Path(os.getenv("VECTOR_DB_DIR", "./vector_store/local"))

    chunks_path = chunk_output_dir / "policy_chunks.json"
    summary_path = processed_output_dir / "vector_store_summary.json"

    if not chunks_path.exists():
        raise FileNotFoundError(
            f"Missing {chunks_path}. Run python scripts\\chunk_pages.py first."
        )

    with chunks_path.open("r", encoding="utf-8") as file:
        chunks = json.load(file)

    if not chunks:
        raise ValueError("No chunks found. Chunk file is empty.")

    print("Starting vector store build...", flush=True)
    print(f"Chunks loaded: {len(chunks)}", flush=True)
    print("Loading local embedding model...", flush=True)

    embedding_model = LocalEmbeddingModel()
    texts = [chunk["text"] for chunk in chunks]

    print("Generating embeddings...", flush=True)
    embeddings = embedding_model.embed_documents(texts)

    print("Saving local NumPy vector store...", flush=True)
    save_vector_store(vector_db_dir, chunks, embeddings)

    document_counter = Counter(chunk["document_name"] for chunk in chunks)
    chunk_type_counter = Counter(chunk["chunk_type"] for chunk in chunks)
    document_type_counter = Counter(chunk["document_type"] for chunk in chunks)

    summary = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "embedding_model": embedding_model.model_name,
        "vector_store": "local_numpy",
        "vector_db_dir": str(vector_db_dir),
        "total_chunks_indexed": len(chunks),
        "chunks_by_document": dict(sorted(document_counter.items())),
        "chunks_by_document_type": dict(sorted(document_type_counter.items())),
        "chunks_by_chunk_type": dict(sorted(chunk_type_counter.items())),
    }

    processed_output_dir.mkdir(parents=True, exist_ok=True)

    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    print("Vector store build completed.", flush=True)
    print(f"Chunks indexed: {summary['total_chunks_indexed']}", flush=True)
    print(f"Summary saved to: {summary_path}", flush=True)


if __name__ == "__main__":
    main()
