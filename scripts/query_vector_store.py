import os
import sys
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.retrieval.search_service import RetrievalSearchService


def main() -> None:
    load_dotenv()

    vector_db_dir = Path(os.getenv("VECTOR_DB_DIR", "./vector_store/local"))

    query = "Is accidental damage covered under car insurance?"

    print(f"Search query: {query}", flush=True)

    search_service = RetrievalSearchService(
        vector_db_dir=vector_db_dir,
        top_k=5,
    )

    results = search_service.search(query=query, top_k=5)

    print("\nTop results:\n", flush=True)

    for result in results:
        print("=" * 100)
        print(f"Result: {result['rank']}")
        print(f"Score: {result['score']}")
        print(f"Distance: {result['distance']}")
        print(f"Document: {result['document_name']}")
        print(f"Document type: {result['document_type']}")
        print(f"Chunk type: {result['chunk_type']}")
        print(f"Section: {result['section_title']}")
        print(f"Pages: {result['start_page']} - {result['end_page']}")
        print(f"Sources: {result['source_references']}")
        print("-" * 100)
        print(result["text_preview"])
        print()


if __name__ == "__main__":
    main()
