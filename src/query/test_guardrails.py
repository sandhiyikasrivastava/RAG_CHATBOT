"""Test the guardrails module.

Usage:
    python -m src.query.test_guardrails
"""

import chromadb
from config import CHROMA_DIR, COLLECTION_NAME
from ingest.embedder import Embedder
from query.guardrails import is_on_topic, has_sufficient_context, check_guardrails


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
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)


if __name__ == "__main__":
    main()
