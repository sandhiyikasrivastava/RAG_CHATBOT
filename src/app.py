"""Streamlit chat UI for the RAG Chatbot.

Usage:
    streamlit run src/app.py
"""

import streamlit as st
from src.chat import RAGChat
from src.config import MEMORY_LIMIT

# Page config
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="centered",
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    st.session_state.chat = None


def init_chat():
    """Initialize the RAG chat pipeline."""
    if st.session_state.chat is None:
        with st.spinner("Loading embedding model..."):
            st.session_state.chat = RAGChat()


def clear_chat():
    """Clear the conversation history."""
    st.session_state.messages = []


def get_conversation_history() -> str:
    """Get the last N messages as a formatted string.

    Returns:
        Formatted conversation history.
    """
    messages = st.session_state.messages[-MEMORY_LIMIT:]
    history = []
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Bot"
        history.append(f"{role}: {msg['content']}")
    return "\n".join(history)


def rewrite_question(question: str) -> str:
    """Rewrite a follow-up question using conversation history.

    Args:
        question: The user's question.

    Returns:
        The rewritten question (or original if no history).
    """
    if len(st.session_state.messages) < 2:
        return question

    history = get_conversation_history()

    # Simple pronoun resolution
    pronouns = ["it", "its", "they", "them", "their", "this", "that", "these", "those"]
    question_lower = question.lower()

    # If question starts with a pronoun or is very short, try to rewrite
    words = question_lower.split()
    if words and words[0] in pronouns or len(words) <= 5:
        # Use the last bot message to provide context
        last_bot_msg = None
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "assistant":
                last_bot_msg = msg["content"]
                break

        if last_bot_msg:
            # Simple rewrite: combine context with question
            return f"{question} (Context from previous answer: {last_bot_msg[:200]})"

    return question


def main():
    """Main Streamlit app."""
    st.title("RAG Chatbot")
    st.caption("Ask questions about the document. The bot retrieves relevant chunks and generates answers.")

    # Initialize chat
    init_chat()

    # Sidebar
    with st.sidebar:
        st.header("Controls")
        if st.button("Clear Chat", type="primary"):
            clear_chat()
            st.rerun()

        st.divider()
        st.header("About")
        st.markdown(
            "**Embedding Model:** all-MiniLM-L6-v2\n\n"
            "**Vector DB:** ChromaDB\n\n"
            "**LLM:** Groq API\n\n"
            "**Chunks:** 14"
        )

    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Rewrite question if needed
        rewritten = rewrite_question(prompt)

        # Get answer
        with st.spinner("Thinking..."):
            result = st.session_state.chat.ask(rewritten)

        # Add bot response to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        })

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

            # Show sources for assistant messages
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("Sources"):
                    for source in msg["sources"]:
                        chunk_idx = source["chunk_index"] + 1
                        similarity = source["similarity"]
                        text = source["text"][:300]
                        st.markdown(f"**Chunk {chunk_idx}** (similarity: {similarity:.4f})")
                        st.text(text)
                        st.divider()


if __name__ == "__main__":
    main()
