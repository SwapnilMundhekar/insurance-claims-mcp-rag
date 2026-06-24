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


from src.ingestion.metadata_enricher import classify_document, build_source_reference
from src.ingestion.text_cleaner import clean_page_text


def main() -> None:
    """
    Cleans raw extracted PDF pages and adds document-level metadata.
    """
    load_dotenv()

    processed_output_dir = Path(os.getenv("PROCESSED_OUTPUT_DIR", "./data/processed"))

    extracted_pages_path = processed_output_dir / "extracted_pages.json"
    clean_pages_path = processed_output_dir / "clean_pages.json"
    inventory_path = processed_output_dir / "document_inventory.json"

    if not extracted_pages_path.exists():
        raise FileNotFoundError(
            f"Missing {extracted_pages_path}. Run python scripts\\ingest_pdfs.py first."
        )

    with extracted_pages_path.open("r", encoding="utf-8") as file:
        extracted_pages = json.load(file)

    clean_pages = []

    for page in extracted_pages:
        document_name = page["document_name"]
        page_number = page["page_number"]
        raw_text = page.get("text", "")

        metadata = classify_document(document_name)
        clean_text = clean_page_text(raw_text)

        clean_page = {
            "document_id": page["document_id"],
            "document_name": document_name,
            "document_type": metadata["document_type"],
            "provider_or_regulator": metadata["provider_or_regulator"],
            "product_type": metadata["product_type"],
            "jurisdiction": metadata["jurisdiction"],
            "source_category": metadata["source_category"],
            "page_number": page_number,
            "total_pages": page["total_pages"],
            "clean_text": clean_text,
            "raw_char_count": page.get("char_count", 0),
            "clean_char_count": len(clean_text),
            "source_reference": build_source_reference(document_name, page_number),
            "extraction_method": page.get("extraction_method", "unknown"),
        }

        clean_pages.append(clean_page)

    with clean_pages_path.open("w", encoding="utf-8") as file:
        json.dump(clean_pages, file, ensure_ascii=False, indent=2)

    documents = {}

    for page in clean_pages:
        document_name = page["document_name"]

        if document_name not in documents:
            documents[document_name] = {
                "document_name": document_name,
                "document_id": page["document_id"],
                "document_type": page["document_type"],
                "provider_or_regulator": page["provider_or_regulator"],
                "product_type": page["product_type"],
                "jurisdiction": page["jurisdiction"],
                "source_category": page["source_category"],
                "total_pages": page["total_pages"],
                "pages_with_text": 0,
                "total_clean_char_count": 0,
            }

        if page["clean_text"]:
            documents[document_name]["pages_with_text"] += 1

        documents[document_name]["total_clean_char_count"] += page["clean_char_count"]

    type_counter = Counter(page["document_type"] for page in clean_pages)

    inventory = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_documents": len(documents),
        "total_pages": len(clean_pages),
        "document_type_counts": dict(type_counter),
        "documents": list(documents.values()),
        "output_files": {
            "clean_pages": str(clean_pages_path),
            "document_inventory": str(inventory_path),
        },
    }

    with inventory_path.open("w", encoding="utf-8") as file:
        json.dump(inventory, file, ensure_ascii=False, indent=2)

    print("Cleaning and metadata enrichment completed.")
    print(f"Documents processed: {inventory['total_documents']}")
    print(f"Pages processed: {inventory['total_pages']}")
    print(f"Clean pages saved to: {clean_pages_path}")
    print(f"Inventory saved to: {inventory_path}")

    print("\nDocument types:")
    for document_type, count in inventory["document_type_counts"].items():
        print(f"- {document_type}: {count} pages")


if __name__ == "__main__":
    main()
