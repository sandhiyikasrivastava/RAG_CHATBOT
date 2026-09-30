"""Streamlit chat UI for the RAG Chatbot.

Usage:
    streamlit run src/app.py
"""

import streamlit as st
from chat import RAGChat

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
    if st.session_state.chat:
        st.session_state.chat.memory.clear()


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

        # Get answer (memory rewriting happens inside RAGChat)
        with st.spinner("Thinking..."):
            result = st.session_state.chat.ask(prompt)

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
