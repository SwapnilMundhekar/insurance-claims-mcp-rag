from pathlib import Path
from typing import Any

from src.retrieval.embedding_model import LocalEmbeddingModel
from src.retrieval.vector_store import search_vector_store


class RetrievalSearchService:
    """
    Search service for semantic retrieval over insurance policy chunks.

    This version uses a local NumPy vector store for stable Windows development.
    """

    def __init__(
        self,
        vector_db_dir: Path,
        top_k: int = 5,
    ) -> None:
        self.vector_db_dir = Path(vector_db_dir)
        self.top_k = top_k
        self.embedding_model = LocalEmbeddingModel()

    def search(
        self,
        query: str,
        top_k: int | None = None,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        query_embedding = self.embedding_model.embed_query(query)

        raw_results = search_vector_store(
            vector_db_dir=self.vector_db_dir,
            query_embedding=query_embedding,
            top_k=top_k or self.top_k,
            where=where,
        )

        normalized_results: list[dict[str, Any]] = []

        for rank, item in enumerate(raw_results, start=1):
            chunk = item["chunk"]

            normalized_results.append(
                {
                    "rank": rank,
                    "distance": round(1 - item["score"], 6),
                    "score": item["score"],
                    "document_name": chunk["document_name"],
                    "document_type": chunk["document_type"],
                    "provider_or_regulator": chunk["provider_or_regulator"],
                    "product_type": chunk["product_type"],
                    "source_category": chunk["source_category"],
                    "section_title": chunk["section_title"],
                    "chunk_type": chunk["chunk_type"],
                    "start_page": chunk["start_page"],
                    "end_page": chunk["end_page"],
                    "source_references": chunk["source_references"],
                    "text_preview": chunk["text"][:1200],
                    "full_text": chunk["text"],
                }
            )

        return normalized_results
