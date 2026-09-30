"""CLI interface for testing the RAG chatbot.

Usage:
    python -m src.cli
"""

from chat import RAGChat


def main():
    print("=" * 60)
    print("RAG Chatbot — CLI")
    print("=" * 60)
    print("\nInitializing (loading embedding model)...")

    chat = RAGChat()

    print("Ready! Type your questions below.")
    print("Type 'quit' to exit.\n")

    while True:
        # Get user input
        question = input("You: ").strip()

        if not question:
            continue

        if question.lower() == "quit":
            print("\nGoodbye!")
            break

        # Get answer
        print("\nThinking...")
        result = chat.ask(question)

        # Display answer
        print(f"\nBot: {result['answer']}")

        # Display sources
        if result["sources"]:
            print("\n--- Retrieved Sources ---")
            for source in result["sources"]:
                chunk_idx = source["chunk_index"] + 1
                similarity = source["similarity"]
                text_preview = source["text"][:100].replace("\n", " ")
                print(f"  Chunk {chunk_idx} (similarity: {similarity:.4f}): {text_preview}...")
            print("-------------------------\n")
        else:
            print()


if __name__ == "__main__":
    main()
