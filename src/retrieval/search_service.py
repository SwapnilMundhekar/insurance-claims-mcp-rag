import json
from pathlib import Path
from typing import Any

from src.retrieval.embedding_model import LocalEmbeddingModel
from src.retrieval.vector_store import (
    create_chroma_client,
    get_or_create_collection,
    query_collection,
)


class RetrievalSearchService:
    """
    Search service for semantic retrieval over insurance policy chunks.

    This class hides the embedding and ChromaDB details from higher-level code.
    """

    def __init__(
        self,
        vector_db_dir: Path,
        top_k: int = 5,
    ) -> None:
        self.vector_db_dir = Path(vector_db_dir)
        self.top_k = top_k
        self.embedding_model = LocalEmbeddingModel()

        self.client = create_chroma_client(self.vector_db_dir)
        self.collection = get_or_create_collection(self.client)

        if self.collection.count() == 0:
            raise ValueError(
                "Vector store is empty. Run python scripts\\build_vector_store.py first."
            )

    def search(
        self,
        query: str,
        top_k: int | None = None,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Runs semantic search and returns normalized retrieval results.
        """
        query_embedding = self.embedding_model.embed_query(query)

        raw_results = query_collection(
            collection=self.collection,
            query_embedding=query_embedding,
            top_k=top_k or self.top_k,
            where=where,
        )

        documents = raw_results["documents"][0]
        metadatas = raw_results["metadatas"][0]
        distances = raw_results["distances"][0]

        normalized_results: list[dict[str, Any]] = []

        for rank, (document, metadata, distance) in enumerate(
            zip(documents, metadatas, distances),
            start=1,
        ):
            source_references = metadata.get("source_references", "[]")

            try:
                source_references = json.loads(source_references)
            except json.JSONDecodeError:
                source_references = [str(source_references)]

            normalized_results.append(
                {
                    "rank": rank,
                    "distance": distance,
                    "document_name": metadata["document_name"],
                    "document_type": metadata["document_type"],
                    "provider_or_regulator": metadata["provider_or_regulator"],
                    "product_type": metadata["product_type"],
                    "source_category": metadata["source_category"],
                    "section_title": metadata["section_title"],
                    "chunk_type": metadata["chunk_type"],
                    "start_page": metadata["start_page"],
                    "end_page": metadata["end_page"],
                    "source_references": source_references,
                    "text_preview": document[:1200],
                    "full_text": document,
                }
            )

        return normalized_results
