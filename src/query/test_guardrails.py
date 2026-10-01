"""Test the guardrails module.

Usage:
    python -m src.query.test_guardrails
"""

import chromadb
from config import CHROMA_DIR, COLLECTION_NAME
from ingest.embedder import Embedder
from query.guardrails import (
    is_on_topic,
    has_sufficient_context,
    is_opinionated_question,
    check_guardrails,
)


def main():
    print("=" * 60)
    print("Phase 4: Guardrails Test")
    print("=" * 60)

    # Load ChromaDB
    print("\nLoading ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)

    # Get all chunk embeddings
    results = collection.get(include=["embeddings", "documents", "metadatas"])
    chunk_embeddings = results["embeddings"]
    print(f"  Loaded {len(chunk_embeddings)} chunk embeddings")

    # Initialize embedder
    print("Loading embedding model...")
    embedder = Embedder()

    # Test cases
    test_cases = [
        ("What is the embedding model?", True, "On-topic question"),
        ("What is the chunking strategy?", True, "On-topic question"),
        ("What's the weather like today?", False, "Off-topic question"),
        ("Write a poem about the ocean", False, "Off-topic question"),
        ("What is the capital of France?", False, "Off-topic question"),
    ]

    print("\n" + "-" * 60)
    print("Testing off-topic detection:")
    print("-" * 60)

    all_passed = True
    for question, expected_on_topic, description in test_cases:
        on_topic, similarity = is_on_topic(question, chunk_embeddings, embedder)
        status = "PASS" if on_topic == expected_on_topic else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"\n  [{status}] {description}")
        print(f"    Question: '{question}'")
        print(f"    Expected on-topic: {expected_on_topic}, Got: {on_topic}")
        print(f"    Best similarity: {similarity:.4f}")

    # Test opinionated question detection
    print("\n" + "-" * 60)
    print("Testing opinionated question detection:")
    print("-" * 60)

    opinionated_tests = [
        ("Should I buy HDFC Top 100?", True, "Direct advice-seeking"),
        ("What is the NAV of HDFC Flexi Cap?", False, "Factual question"),
        ("Which fund should I invest in?", True, "Asking for recommendation"),
        ("What is the expense ratio of HDFC Index Fund?", False, "Factual question"),
        ("Is HDFC a good fund?", True, "Asking for opinion"),
        ("What are the holdings of HDFC Hybrid Fund?", False, "Factual question"),
        ("Can you recommend a good mutual fund?", True, "Asking for recommendation"),
        ("What is the investment objective of HDFC Top 100?", False, "Factual question"),
        ("Is it a good time to invest in HDFC?", True, "Asking for timing advice"),
        ("What is the minimum investment amount?", False, "Factual question"),
        ("What do you think about HDFC Small Cap?", True, "Asking for opinion"),
        ("How much will I get if I invest 10000?", True, "Asking for returns prediction"),
        ("What is the fund manager name?", False, "Factual question"),
        ("Should I switch from one fund to another?", True, "Asking for advice"),
        ("What is the exit load structure?", False, "Factual question"),
    ]

    opinionated_passed = True
    for question, expected_opinionated, description in opinionated_tests:
        result = is_opinionated_question(question)
        status = "PASS" if result == expected_opinionated else "FAIL"
        if status == "FAIL":
            opinionated_passed = False
        print(f"\n  [{status}] {description}")
        print(f"    Question: '{question}'")
        print(f"    Expected opinionated: {expected_opinionated}, Got: {result}")

    # Test context sufficiency
    print("\n" + "-" * 60)
    print("Testing context sufficiency:")
    print("-" * 60)

    # High similarity scores (should pass)
    sufficient = has_sufficient_context([0.8, 0.7, 0.6])
    print(f"\n  [{'PASS' if sufficient else 'FAIL'}] High similarities [0.8, 0.7, 0.6] -> {sufficient}")

    # Low similarity scores (should fail)
    not_sufficient = has_sufficient_context([0.1, 0.05, 0.02])
    print(f"  [{'PASS' if not not_sufficient else 'FAIL'}] Low similarities [0.1, 0.05, 0.02] -> {not_sufficient}")

    # Empty list (should fail)
    empty = has_sufficient_context([])
    print(f"  [{'PASS' if not empty else 'FAIL'}] Empty list -> {empty}")

    # Summary
    print("\n" + "=" * 60)
    if all_passed and opinionated_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
        if not all_passed:
            print("  - Off-topic detection tests failed")
        if not opinionated_passed:
            print("  - Opinionated question detection tests failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
