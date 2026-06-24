from pathlib import Path

from src.llm.ollama_client import OllamaChatClient
from src.retrieval.search_service import RetrievalSearchService


SYSTEM_PROMPT = """
You are an insurance policy and claims assistant.

You must answer only using the retrieved context provided by the application.
Do not invent policy terms, claim decisions, exclusions, timeframes, or regulatory obligations.

Rules:
1. If the retrieved context is insufficient, say that the available context is insufficient.
2. Use careful language such as "based on the retrieved policy context".
3. Do not present a final legal, claim, or coverage decision.
4. Include source references from the provided context.
5. Keep the answer structured and practical.
"""


class RAGAnswerService:
    """
    Retrieval-augmented answer service.

    This service retrieves policy chunks first, then asks the local LLM
    to answer using only those chunks.
    """

    def __init__(
        self,
        vector_db_dir: Path,
        top_k: int = 5,
    ) -> None:
        self.search_service = RetrievalSearchService(
            vector_db_dir=vector_db_dir,
            top_k=top_k,
        )
        self.llm_client = OllamaChatClient()
        self.top_k = top_k

    def build_context(self, retrieval_results: list[dict]) -> str:
        """
        Converts retrieval results into a compact context block for the LLM.
        """
        context_blocks = []

        for result in retrieval_results:
            source_refs = "; ".join(result["source_references"])

            block = f"""
[Source {result['rank']}]
Document: {result['document_name']}
Document type: {result['document_type']}
Provider or regulator: {result['provider_or_regulator']}
Section: {result['section_title']}
Chunk type: {result['chunk_type']}
Pages: {result['start_page']} - {result['end_page']}
Source references: {source_refs}

Text:
{result['full_text']}
""".strip()

            context_blocks.append(block)

        return "\n\n---\n\n".join(context_blocks)

    def answer(self, question: str) -> dict:
        """
        Retrieves context and generates a grounded answer.
        """
        retrieval_results = self.search_service.search(
            query=question,
            top_k=self.top_k,
        )

        context = self.build_context(retrieval_results)

        user_prompt = f"""
Question:
{question}

Retrieved context:
{context}

Now answer the question using only the retrieved context.
""".strip()

        answer_text = self.llm_client.chat(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.1,
        )

        return {
            "question": question,
            "answer": answer_text,
            "retrieval_results": retrieval_results,
        }
