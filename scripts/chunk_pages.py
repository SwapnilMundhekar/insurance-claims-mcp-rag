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


from src.chunking.chunk_builder import build_chunks


def main() -> None:
    """
    Builds section-aware semantic chunks from cleaned page records.
    """
    load_dotenv()

    processed_output_dir = Path(os.getenv("PROCESSED_OUTPUT_DIR", "./data/processed"))
    chunk_output_dir = Path(os.getenv("CHUNK_OUTPUT_DIR", "./data/chunks"))

    clean_pages_path = processed_output_dir / "clean_pages.json"
    chunks_path = chunk_output_dir / "policy_chunks.json"
    summary_path = chunk_output_dir / "chunking_summary.json"

    if not clean_pages_path.exists():
        raise FileNotFoundError(
            f"Missing {clean_pages_path}. Run python scripts\\clean_pages.py first."
        )

    chunk_output_dir.mkdir(parents=True, exist_ok=True)

    with clean_pages_path.open("r", encoding="utf-8") as file:
        clean_pages = json.load(file)

    print("Starting section-aware semantic chunking...")
    print(f"Input pages: {len(clean_pages)}")

    chunks = build_chunks(
        clean_pages=clean_pages,
        min_tokens=120,
        max_tokens=650,
        overlap_units=1,
    )

    with chunks_path.open("w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)

    document_counter = Counter(chunk["document_name"] for chunk in chunks)
    chunk_type_counter = Counter(chunk["chunk_type"] for chunk in chunks)
    document_type_counter = Counter(chunk["document_type"] for chunk in chunks)

    token_counts = [chunk["estimated_tokens"] for chunk in chunks]

    summary = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_chunks": len(chunks),
        "min_tokens": min(token_counts) if token_counts else 0,
        "max_tokens": max(token_counts) if token_counts else 0,
        "average_tokens": round(sum(token_counts) / len(token_counts), 2) if token_counts else 0,
        "chunking_strategy": {
            "name": "section_aware_semantic_chunking",
            "description": "Paragraph-level semantic units grouped by detected document sections, with estimated token guardrails and paragraph overlap.",
            "min_tokens": 120,
            "max_tokens": 650,
            "overlap_units": 1,
        },
        "chunks_by_document": dict(sorted(document_counter.items())),
        "chunks_by_document_type": dict(sorted(document_type_counter.items())),
        "chunks_by_chunk_type": dict(sorted(chunk_type_counter.items())),
        "output_files": {
            "chunks": str(chunks_path),
            "summary": str(summary_path),
        },
    }

    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    print("Chunking completed.")
    print(f"Total chunks created: {summary['total_chunks']}")
    print(f"Average estimated tokens: {summary['average_tokens']}")
    print(f"Max estimated tokens: {summary['max_tokens']}")
    print(f"Chunks saved to: {chunks_path}")
    print(f"Summary saved to: {summary_path}")

    print("\nChunks by type:")
    for chunk_type, count in summary["chunks_by_chunk_type"].items():
        print(f"- {chunk_type}: {count}")


if __name__ == "__main__":
    main()
