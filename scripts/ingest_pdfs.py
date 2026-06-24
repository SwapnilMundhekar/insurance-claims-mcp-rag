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


from src.ingestion.pdf_loader import extract_pages_from_folder


def main() -> None:
    """
    Main ingestion script.

    It reads the PDF_SOURCE_DIR from .env, extracts all PDF pages,
    and saves structured JSON output into data/processed.
    """
    load_dotenv()

    pdf_source_dir = Path(os.getenv("PDF_SOURCE_DIR", ""))
    processed_output_dir = Path(os.getenv("PROCESSED_OUTPUT_DIR", "./data/processed"))

    if not pdf_source_dir:
        raise ValueError("PDF_SOURCE_DIR is missing from .env")

    processed_output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Project root: {PROJECT_ROOT}")
    print(f"PDF source folder: {pdf_source_dir}")
    print("Starting PDF ingestion...")

    extracted_pages = extract_pages_from_folder(pdf_source_dir)

    extracted_pages_path = processed_output_dir / "extracted_pages.json"
    summary_path = processed_output_dir / "ingestion_summary.json"

    with extracted_pages_path.open("w", encoding="utf-8") as file:
        json.dump(extracted_pages, file, ensure_ascii=False, indent=2)

    document_counter = Counter(page["document_name"] for page in extracted_pages)

    summary = {
        "ingestion_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "pdf_source_dir": str(pdf_source_dir),
        "total_documents": len(document_counter),
        "total_pages": len(extracted_pages),
        "documents": [
            {
                "document_name": document_name,
                "pages_extracted": page_count,
            }
            for document_name, page_count in sorted(document_counter.items())
        ],
        "output_files": {
            "extracted_pages": str(extracted_pages_path),
            "summary": str(summary_path),
        },
    }

    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    print("PDF ingestion completed.")
    print(f"Documents found: {summary['total_documents']}")
    print(f"Pages extracted: {summary['total_pages']}")
    print(f"Saved extracted pages to: {extracted_pages_path}")
    print(f"Saved summary to: {summary_path}")


if __name__ == "__main__":
    main()
