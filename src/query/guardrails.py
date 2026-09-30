"""Guardrails: off-topic detection and context sufficiency checks."""

from typing import List, Tuple, Optional
import numpy as np
from config import SIMILARITY_THRESHOLD
from ingest.embedder import Embedder


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
    """Check if a question is asking for investment advice.

    Args:
        question: The user's question.

    Returns:
        True if the question is opinionated/asking for advice.
    """
    opinionated_patterns = [
        "should i buy", "should i sell", "should i invest",
        "is it good to", "is it bad to", "should i purchase",
        "should i redeem", "should i switch", "best fund",
        "which fund should", "what should i do", "give me advice",
        "recommend", "suggestion", "opinion", "worth buying",
        "good investment", "bad investment", "will i get profit",
        "can i earn", "how much will i get", "guaranteed returns",
    ]
    question_lower = question.lower()
    return any(pattern in question_lower for pattern in opinionated_patterns)


def check_guardrails(
    question: str,
    retrieved_chunks: List[dict],
    embedder: Embedder,
    all_chunk_embeddings: List[List[float]],
) -> Optional[str]:
    """Run all guardrails and return a refusal message if any check fails.

    Args:
        question: The user's question.
        retrieved_chunks: List of retrieved chunk dicts with 'embedding' and 'text'.
        embedder: The embedder instance.
        all_chunk_embeddings: All chunk embeddings for off-topic check.

    Returns:
        None if all checks pass, otherwise a refusal message string.
    """
    # Check 0: Opinionated/advice questions
    if is_opinionated_question(question):
        return (
            "I can only answer factual questions about HDFC mutual fund schemes. "
            "I cannot provide investment advice. Please consult a financial advisor "
            "for personalized recommendations."
        )

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
