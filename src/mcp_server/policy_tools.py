import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.retrieval.search_service import RetrievalSearchService


load_dotenv()


def get_vector_db_dir() -> Path:
    return Path(os.getenv("VECTOR_DB_DIR", "./vector_store/local"))


def build_search_service(top_k: int = 5) -> RetrievalSearchService:
    return RetrievalSearchService(
        vector_db_dir=get_vector_db_dir(),
        top_k=top_k,
    )


def search_policy_documents(query: str, top_k: int = 5) -> dict[str, Any]:
    """
    Searches insurance policy and regulatory documents using semantic retrieval.
    """
    search_service = build_search_service(top_k=top_k)
    results = search_service.search(query=query, top_k=top_k)

    return {
        "query": query,
        "top_k": top_k,
        "result_count": len(results),
        "results": results,
    }


def get_complaint_obligations(query: str, top_k: int = 5) -> dict[str, Any]:
    """
    Searches complaint handling and dispute resolution obligations.
    """
    search_service = build_search_service(top_k=top_k)

    results = search_service.search(
        query=query,
        top_k=top_k,
    )

    filtered_results = [
        result
        for result in results
        if result["document_type"] in ["regulatory_guidance", "industry_code"]
        or result["chunk_type"] == "complaint_obligation"
    ]

    return {
        "query": query,
        "top_k": top_k,
        "result_count": len(filtered_results),
        "results": filtered_results,
    }


def get_claim_requirements(query: str, top_k: int = 5) -> dict[str, Any]:
    """
    Searches claim evidence, claim documents, and claim handling requirements.
    """
    search_service = build_search_service(top_k=top_k)

    results = search_service.search(
        query=query,
        top_k=top_k,
    )

    filtered_results = [
        result
        for result in results
        if result["chunk_type"] in ["claims_requirement", "coverage_clause", "exclusion"]
    ]

    return {
        "query": query,
        "top_k": top_k,
        "result_count": len(filtered_results),
        "results": filtered_results,
    }
