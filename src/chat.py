"""Main RAG pipeline: combines retrieval + guardrails + LLM."""

from typing import List, Dict, Any, Optional
from ingest.embedder import Embedder
from query.retriever import Retriever
from query.llm import LLMClient
from query.guardrails import check_guardrails
from query.memory import ConversationMemory, rewrite_question


SYSTEM_PROMPT_TEMPLATE = """You are a strictly factual assistant for HDFC mutual fund schemes. You extract and report objective, documented facts from the provided context.

IMPORTANT: The context below contains the answer to most questions. Your job is to FIND the relevant information in the context and report it. Only say "I don't know" if the context truly does not contain the requested information.

RULES:
1. Extract the answer directly from the context. If the data is there, report it.
2. If the context doesn't contain the answer, say "I don't know."
3. NEVER give investment advice, opinions, recommendations, or suggestions.
4. NEVER predict future performance or returns.
5. Keep answers concise (1-3 sentences).
6. Include the source link from the context.
7. End with "Last updated from sources: [date]".

If the user asks an opinionated or advice-seeking question, respond with: "Only fact-based questions allowed."

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

        # Run guardrails (with LLM-based opinionated question check)
        refusal = check_guardrails(rewritten, retrieved_chunks, self.embedder, all_embeddings, self.llm)
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

        # Post-generation check: verify answer doesn't contain opinions
        if self._contains_opinions(answer):
            refusal = "Only fact-based questions allowed."
            self.memory.add("user", question)
            self.memory.add("assistant", refusal)
            return {
                "answer": refusal,
                "sources": [],
                "refused": True,
            }

        # Add to memory
        self.memory.add("user", question)
        self.memory.add("assistant", answer)

        return {
            "answer": answer,
            "sources": retrieved_chunks,
            "refused": False,
        }

    def _contains_opinions(self, answer: str) -> bool:
        """Check if the generated answer contains opinionated language.

        Args:
            answer: The generated answer text.

        Returns:
            True if the answer contains opinionated language.
        """
        opinion_indicators = [
            "i recommend", "i suggest", "i advise", "you should",
            "you must", "you ought to", "it is advisable",
            "it is recommended", "it is suggested", "good investment",
            "bad investment", "worth buying", "worth investing",
            "good time to invest", "bad time to invest",
            "i think", "in my opinion", "i believe",
            "you can earn", "you will get", "you will make",
            "guaranteed returns", "risk-free", "safe investment",
            "best fund", "best scheme", "better option",
            "good option", "bad option", "good choice",
            "bad choice", "good pick", "bad pick",
        ]
        answer_lower = answer.lower()
        return any(indicator in answer_lower for indicator in opinion_indicators)
