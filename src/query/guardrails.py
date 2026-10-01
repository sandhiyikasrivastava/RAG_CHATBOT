"""Guardrails: off-topic detection and context sufficiency checks."""

from typing import List, Tuple, Optional
import numpy as np
from src.config import SIMILARITY_THRESHOLD
from ingest.embedder import Embedder
from query.llm import LLMClient


def compute_similarity(query_embedding: List[float], chunk_embedding: List[float]) -> float:
    """Compute cosine similarity between two vectors.

    Args:
        query_embedding: The query vector.
        chunk_embedding: The chunk vector.

    Returns:
        Cosine similarity score between -1 and 1.
    """
    query = np.array(query_embedding)
    chunk = np.array(chunk_embedding)

    dot_product = np.dot(query, chunk)
    query_norm = np.linalg.norm(query)
    chunk_norm = np.linalg.norm(chunk)

    if query_norm == 0 or chunk_norm == 0:
        return 0.0

    return float(dot_product / (query_norm * chunk_norm))


def is_on_topic(
    question: str,
    chunk_embeddings: List[List[float]],
    embedder: Embedder,
    threshold: float = SIMILARITY_THRESHOLD,
) -> Tuple[bool, float]:
    """Check if a question is on-topic by comparing it against all chunk embeddings.

    Args:
        question: The user's question.
        chunk_embeddings: List of all chunk embedding vectors.
        embedder: The embedder instance.
        threshold: Minimum similarity score to be considered on-topic.

    Returns:
        Tuple of (is_on_topic: bool, best_similarity: float).
    """
    query_embedding = embedder.embed_query(question)

    best_similarity = -1.0
    for chunk_emb in chunk_embeddings:
        sim = compute_similarity(query_embedding, chunk_emb)
        if sim > best_similarity:
            best_similarity = sim

    return best_similarity >= threshold, best_similarity


def has_sufficient_context(
    similarities: List[float],
    threshold: float = SIMILARITY_THRESHOLD,
) -> bool:
    """Check if retrieved chunks have sufficient relevance to answer.

    Args:
        similarities: List of similarity scores for retrieved chunks.
        threshold: Minimum similarity score for context to be sufficient.

    Returns:
        True if at least one chunk meets the threshold.
    """
    if not similarities:
        return False
    return max(similarities) >= threshold


def is_opinionated_question(question: str) -> bool:
    """Check if a question is asking for investment advice or opinions.

    Args:
        question: The user's question.

    Returns:
        True if the question is opinionated/asking for advice.
    """
    opinionated_patterns = [
        # Direct advice-seeking
        "should i buy", "should i sell", "should i invest",
        "should i purchase", "should i redeem", "should i switch",
        "should i hold", "should i exit", "should i enter",
        "should i put", "should i allocate", "should i diversify",
        "is it good to", "is it bad to", "is it worth",
        "is it a good", "is it a bad", "is it better",
        "is it profitable", "is it safe", "is it risky",
        "what should i do", "what should i choose",
        "what should i pick", "what should i go with",
        "which fund should", "which scheme should", "which is better",
        "which is best", "which one should", "which is good",
        "which is the best", "which is the right",
        "give me advice", "give me your opinion", "give me your thoughts",
        "recommend", "recommendation", "suggestion", "suggest",
        "opinion", "thoughts on", "views on", "your take",
        "worth buying", "worth investing", "worth it",
        "good investment", "bad investment", "good fund", "bad fund",
        "good scheme", "bad scheme", "best fund", "best scheme",
        "better fund", "better scheme", "top fund", "top scheme",
        "will i get profit", "will i make money", "will i earn",
        "can i earn", "can i make money", "how much will i get",
        "how much can i earn", "how much profit", "guaranteed returns",
        "guaranteed profit", "risk free", "risk-free",
        "is this a good time", "is now a good time",
        "should i start", "should i begin", "should i go for",
        "is it the right time", "is it too late", "is it too early",
        "what do you think", "do you think", "do you recommend",
        "would you recommend", "would you suggest", "would you buy",
        "would you invest", "would you choose", "would you pick",
        "what would you do", "what would you choose",
        "is hdfc a good", "is hdfc good", "is hdfc bad",
        "is hdfc worth", "is hdfc safe", "is hdfc risky",
        "how is hdfc", "how is the fund", "how is the scheme",
        "performance of hdfc", "how has hdfc performed",
        "past performance", "future performance", "expected returns",
        "expected profit", "can i invest", "can i buy", "can i purchase",
        "can i put money", "can i start", "should i consider",
        "is it advisable", "is it recommended", "is it suggested",
        "is it a good idea", "is it a bad idea",
        "what is your advice", "what is your recommendation",
        "what is your suggestion", "what is your opinion",
        "tell me if i should", "tell me whether i should",
        "advise me", "guide me on", "help me decide",
        "help me choose", "help me pick", "help me select",
        "which one is better", "which one is best", "which one should",
        "compare and suggest", "compare and recommend",
        "which is more profitable", "which is safer", "which is riskier",
        "which gives better returns", "which gives higher returns",
        "which has better performance", "which has good performance",
        "is it good for me", "is it bad for me", "is it suitable",
        "is it appropriate", "is it ideal", "is it perfect",
        "should i go with", "should i opt for", "should i prefer",
        "is it a good option", "is it a bad option",
        "is it a good choice", "is it a bad choice",
        "is it a good pick", "is it a bad pick",
        "is it a good bet", "is it a bad bet",
        "is it a good move", "is it a bad move",
        "is it a good decision", "is it a bad decision",
        "is it a good strategy", "is it a bad strategy",
        "is it a good approach", "is it a bad approach",
        "is it a good plan", "is it a bad plan",
        "is it a good idea to invest", "is it a good idea to buy",
        "is it a good idea to start", "is it a good idea to put",
        "is it a good idea to allocate", "is it a good idea to diversify",
        "is it a good idea to consider", "is it a good idea to go",
        "is it a good idea to choose", "is it a good idea to pick",
        "is it a good idea to opt", "is it a good idea to prefer",
        "is it a good idea to switch", "is it a good idea to redeem",
        "is it a good idea to hold", "is it a good idea to exit",
        "is it a good idea to enter", "is it a good idea to purchase",
        "is it a good idea to sell", "is it a good idea to invest",
        "is it a good idea to buy", "is it a good idea to start",
        "is it a good idea to put", "is it a good idea to allocate",
        "is it a good idea to diversify", "is it a good idea to consider",
        "is it a good idea to go", "is it a good idea to choose",
        "is it a good idea to pick", "is it a good idea to opt",
        "is it a good idea to prefer", "is it a good idea to switch",
        "is it a good idea to redeem", "is it a good idea to hold",
        "is it a good idea to exit", "is it a good idea to enter",
        "is it a good idea to purchase", "is it a good idea to sell",
    ]
    question_lower = question.lower()
    return any(pattern in question_lower for pattern in opinionated_patterns)


def is_opinionated_question_llm(question: str, llm_client: LLMClient) -> bool:
    """Use the LLM to check if a question is opinionated/asking for advice.

    This is a second layer of defense that catches rephrased or subtle
    opinionated questions that the keyword-based check might miss.

    Args:
        question: The user's question.
        llm_client: The LLM client instance.

    Returns:
        True if the LLM determines the question is opinionated.
    """
    classifier_prompt = """You are a classifier. Determine if the following question is asking for an opinion, advice, recommendation, or subjective judgment about investing or mutual funds.

A question is OPINIONATED if it:
- Asks what someone should do (buy, sell, invest, choose, etc.)
- Asks for a recommendation or suggestion
- Asks whether something is "good", "bad", "worth it", "safe", "risky", etc.
- Asks for a comparison to decide which is better
- Asks for future performance predictions or expected returns
- Asks for personal financial advice

A question is FACTUAL if it:
- Asks about objective facts (fund name, NAV, expense ratio, holdings, etc.)
- Asks about historical data that is documented
- Asks about scheme details, features, or rules
- Asks about past performance data that is documented

Respond with only "OPINIONATED" or "FACTUAL". Nothing else.

Question: {question}"""

    try:
        response = llm_client.generate(
            classifier_prompt.format(question=question),
            question,
        )
        return "OPINIONATED" in response.upper()
    except Exception:
        # If LLM check fails, fall back to keyword check only
        return False


def check_guardrails(
    question: str,
    retrieved_chunks: List[dict],
    embedder: Embedder,
    all_chunk_embeddings: List[List[float]],
    llm_client: Optional[LLMClient] = None,
) -> Optional[str]:
    """Run all guardrails and return a refusal message if any check fails.

    Args:
        question: The user's question.
        retrieved_chunks: List of retrieved chunk dicts with 'embedding' and 'text'.
        embedder: The embedder instance.
        all_chunk_embeddings: All chunk embeddings for off-topic check.
        llm_client: Optional LLM client for opinionated question classification.

    Returns:
        None if all checks pass, otherwise a refusal message string.
    """
    # Check 0a: Opinionated/advice questions (keyword-based, fast)
    if is_opinionated_question(question):
        return "Only fact-based questions allowed."

    # Check 0b: Opinionated/advice questions (LLM-based, catches rephrased questions)
    if llm_client and is_opinionated_question_llm(question, llm_client):
        return "Only fact-based questions allowed."

    # Check 1: Off-topic
    on_topic, best_sim = is_on_topic(question, all_chunk_embeddings, embedder)
    if not on_topic:
        return (
            "I can only answer questions about the document. "
            "Your question seems off-topic."
        )

    # Check 2: Context sufficiency (use similarity scores from retriever)
    similarities = [chunk["similarity"] for chunk in retrieved_chunks if "similarity" in chunk]

    if not has_sufficient_context(similarities):
        return (
            "I don't know. The document doesn't contain enough "
            "information to answer that."
        )

    return None
