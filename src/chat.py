"""Main RAG pipeline: combines retrieval + guardrails + LLM."""

from typing import List, Dict, Any, Optional
from ingest.embedder import Embedder
from query.retriever import Retriever
from query.llm import LLMClient
from query.guardrails import check_guardrails
from query.memory import ConversationMemory, rewrite_question


SYSTEM_PROMPT_TEMPLATE = """You are a facts-only assistant for HDFC mutual fund schemes.
Rules:
1. Only use information from the context below to answer.
2. If the context doesn't contain the answer, say "I don't know."
3. Never give investment advice.
4. Keep answers to 3 sentences or less.
5. Include one source link from the context.
6. End with "Last updated from sources: [date]".

Context:
{retrieved_chunks}

Question: {user_question}"""


class RAGChat:
    """The main RAG chatbot pipeline."""

    def __init__(self):
        """Initialize all components."""
        self.embedder = Embedder()
        self.retriever = Retriever(self.embedder)
        self.llm = LLMClient()
        self.memory = ConversationMemory()

    def ask(self, question: str) -> Dict[str, Any]:
        """Process a question and return an answer with sources.

        Args:
            question: The user's question.

        Returns:
            Dict with 'answer', 'sources', and 'refused' keys.
        """
        # Rewrite question using conversation memory
        rewritten = rewrite_question(question, self.memory)
        if rewritten != question:
            print(f"  [Memory] Rewritten: {rewritten}")

        # Get all embeddings for guardrails
        all_embeddings = self.retriever.get_all_embeddings()

        # Retrieve top-k chunks
        retrieved_chunks = self.retriever.retrieve(rewritten)

        # Run guardrails
        refusal = check_guardrails(rewritten, retrieved_chunks, self.embedder, all_embeddings)
        if refusal:
            # Still add to memory even if refused
            self.memory.add("user", question)
            self.memory.add("assistant", refusal)
            return {
                "answer": refusal,
                "sources": [],
                "refused": True,
            }

        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            context_parts.append(f"[Chunk {chunk['chunk_index'] + 1}]\n{chunk['text']}")
        context = "\n\n".join(context_parts)

        # Build system prompt
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            retrieved_chunks=context,
            user_question=rewritten,
        )

        # Generate answer
        answer = self.llm.generate(system_prompt, rewritten)

        # Add to memory
        self.memory.add("user", question)
        self.memory.add("assistant", answer)

        return {
            "answer": answer,
            "sources": retrieved_chunks,
            "refused": False,
        }
