import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.retrieval.search_service import RetrievalSearchService


def score_result(
    result: dict,
    expected_document_type: str,
    expected_chunk_types: list[str],
) -> dict:
    document_type_match = result["document_type"] == expected_document_type
    chunk_type_match = result["chunk_type"] in expected_chunk_types

    score = 0

    if document_type_match:
        score += 1

    if chunk_type_match:
        score += 1

    return {
        "document_type_match": document_type_match,
        "chunk_type_match": chunk_type_match,
        "metadata_score": score,
    }


def build_markdown_report(results: list[dict]) -> str:
    lines = [
        "# Retrieval Test Report",
        "",
        f"Generated at UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "This report checks whether semantic search returns useful insurance policy or regulatory chunks before LLM integration.",
        "",
        "## Summary",
        "",
    ]

    total_queries = len(results)
    top1_document_matches = sum(1 for item in results if item["top1_document_type_match"])
    top3_any_document_matches = sum(1 for item in results if item["top3_any_document_type_match"])

    lines.extend(
        [
            f"- Total test queries: {total_queries}",
            f"- Top 1 document type matches: {top1_document_matches}/{total_queries}",
            f"- Top 3 any document type matches: {top3_any_document_matches}/{total_queries}",
            "",
            "## Detailed Results",
            "",
        ]
    )

    for item in results:
        lines.extend(
            [
                f"### {item['query_id']}",
                "",
                f"**Query:** {item['query']}",
                "",
                f"**Expected document type:** `{item['expected_document_type']}`",
                "",
                f"**Top 1 document type match:** `{item['top1_document_type_match']}`",
                "",
                "| Rank | Document | Document Type | Chunk Type | Pages | Distance |",
                "|---:|---|---|---|---|---:|",
            ]
        )

        for result in item["results"]:
            lines.append(
                f"| {result['rank']} | {result['document_name']} | {result['document_type']} | "
                f"{result['chunk_type']} | {result['start_page']}-{result['end_page']} | "
                f"{round(result['distance'], 4)} |"
            )

        lines.extend(["", "**Top result preview:**", "", "```text"])

        if item["results"]:
            lines.append(item["results"][0]["text_preview"][:1000])

        lines.extend(["```", ""])

    return "\n".join(lines)


def main() -> None:
    print("Retrieval evaluation script started.", flush=True)

    load_dotenv()

    vector_db_dir = Path(os.getenv("VECTOR_DB_DIR", "./vector_store/chroma"))
    processed_output_dir = Path(os.getenv("PROCESSED_OUTPUT_DIR", "./data/processed"))
    query_config_path = PROJECT_ROOT / "config" / "retrieval_test_queries.json"

    results_path = processed_output_dir / "retrieval_test_results.json"
    report_path = processed_output_dir / "retrieval_test_report.md"

    print(f"Project root: {PROJECT_ROOT}", flush=True)
    print(f"Vector DB dir: {vector_db_dir}", flush=True)
    print(f"Query config path: {query_config_path}", flush=True)

    if not query_config_path.exists():
        raise FileNotFoundError(f"Missing query config: {query_config_path}")

    if not vector_db_dir.exists():
        raise FileNotFoundError(
            f"Vector DB folder missing: {vector_db_dir}. Run python scripts\\build_vector_store.py first."
        )

    print("Loading retrieval test queries...", flush=True)

    with query_config_path.open("r", encoding="utf-8-sig") as file:
        test_queries = json.load(file)

    print(f"Test queries loaded: {len(test_queries)}", flush=True)

    processed_output_dir.mkdir(parents=True, exist_ok=True)

    print("Initializing retrieval search service...", flush=True)

    search_service = RetrievalSearchService(
        vector_db_dir=vector_db_dir,
        top_k=5,
    )

    print("Retrieval search service initialized.", flush=True)
    print("Starting retrieval evaluation...", flush=True)

    evaluation_results = []

    for test_case in test_queries:
        query_id = test_case["query_id"]
        query = test_case["query"]
        expected_document_type = test_case["expected_document_type"]
        expected_chunk_types = test_case["expected_chunk_types"]

        print(f"Running query: {query_id}", flush=True)

        search_results = search_service.search(query=query, top_k=5)

        scored_results = []

        for result in search_results:
            score = score_result(
                result=result,
                expected_document_type=expected_document_type,
                expected_chunk_types=expected_chunk_types,
            )

            scored_results.append(
                {
                    **result,
                    **score,
                }
            )

        top1_document_type_match = bool(
            scored_results and scored_results[0]["document_type_match"]
        )

        top3_any_document_type_match = any(
            result["document_type_match"] for result in scored_results[:3]
        )

        evaluation_results.append(
            {
                "query_id": query_id,
                "query": query,
                "expected_document_type": expected_document_type,
                "expected_chunk_types": expected_chunk_types,
                "top1_document_type_match": top1_document_type_match,
                "top3_any_document_type_match": top3_any_document_type_match,
                "results": scored_results,
            }
        )

    output_payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "vector_db_dir": str(vector_db_dir),
        "total_queries": len(test_queries),
        "results": evaluation_results,
    }

    with results_path.open("w", encoding="utf-8") as file:
        json.dump(output_payload, file, ensure_ascii=False, indent=2)

    markdown_report = build_markdown_report(evaluation_results)

    with report_path.open("w", encoding="utf-8") as file:
        file.write(markdown_report)

    total_queries = len(evaluation_results)
    top1_matches = sum(1 for item in evaluation_results if item["top1_document_type_match"])
    top3_matches = sum(1 for item in evaluation_results if item["top3_any_document_type_match"])

    print("Retrieval evaluation completed.", flush=True)
    print(f"Top 1 document type matches: {top1_matches}/{total_queries}", flush=True)
    print(f"Top 3 any document type matches: {top3_matches}/{total_queries}", flush=True)
    print(f"Results saved to: {results_path}", flush=True)
    print(f"Report saved to: {report_path}", flush=True)


if __name__ == "__main__":
    main()
