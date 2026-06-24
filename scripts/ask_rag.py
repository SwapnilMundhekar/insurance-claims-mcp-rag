import os
import sys
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.llm.rag_answer_service import RAGAnswerService


def main() -> None:
    load_dotenv()

    vector_db_dir = Path(os.getenv("VECTOR_DB_DIR", "./vector_store/local"))

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "Is accidental damage covered under car insurance?"

    print("Starting local RAG answer test...", flush=True)
    print(f"Question: {question}", flush=True)
    print(f"Vector DB dir: {vector_db_dir}", flush=True)

    rag_service = RAGAnswerService(
        vector_db_dir=vector_db_dir,
        top_k=5,
    )

    result = rag_service.answer(question)

    print("\nAnswer:\n")
    print(result["answer"])

    print("\nRetrieved sources:\n")

    for item in result["retrieval_results"]:
        print("-" * 100)
        print(f"Rank: {item['rank']}")
        print(f"Score: {item.get('score')}")
        print(f"Document: {item['document_name']}")
        print(f"Section: {item['section_title']}")
        print(f"Chunk type: {item['chunk_type']}")
        print(f"Pages: {item['start_page']} - {item['end_page']}")
        print(f"Sources: {item['source_references']}")


if __name__ == "__main__":
    main()
