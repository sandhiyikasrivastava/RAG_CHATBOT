"""
Groww AI Assist - HDFC Insights
Streamlit UI for the existing RAG chatbot.
"""

import streamlit as st
import time

from chat import RAGChat


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Groww AI Assist - HDFC Insights",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------
# CUSTOM CSS (Responsive: Phone + Laptop)
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    /* ---------- PAGE ---------- */

    .stApp {
        background: #2d1b3d;
    }

    .block-container {
        max-width: 480px;
        padding-top: 0.5rem;
        padding-bottom: 5rem;
    }

    /* Hide Streamlit branding/footer */
    footer {
        visibility: hidden;
    }

    #MainMenu {
        visibility: hidden;
    }

    /* ---------- HEADER ---------- */

    .header-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 4px;
        margin-bottom: 8px;
    }

    .header-back {
        font-size: 22px;
        color: #e2d9f3;
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 8px;
        transition: background 0.15s;
    }

    .header-back:hover {
        background: rgba(255,255,255,0.08);
    }

    .header-title-group {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .header-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #4ade80;
        display: inline-block;
    }

    .header-title {
        font-size: 17px;
        font-weight: 700;
        color: #f3eef9;
    }

    .header-menu {
        font-size: 20px;
        color: #e2d9f3;
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 8px;
    }

    .header-menu:hover {
        background: rgba(255,255,255,0.08);
    }

    /* ---------- HERO ---------- */

    .hero-sparkle {
        text-align: center;
        font-size: 28px;
        margin-top: 16px;
        margin-bottom: 8px;
    }

    .hero-title {
        text-align: center;
        font-size: 28px;
        line-height: 1.25;
        font-weight: 800;
        color: #f3eef9;
        margin-bottom: 12px;
    }

    .hero-subtitle {
        text-align: center;
        font-size: 14px;
        line-height: 1.5;
        color: #b8a6d4;
        margin-bottom: 20px;
        padding: 0 12px;
    }

    /* ---------- SOURCES ---------- */

    .sources-section {
        text-align: center;
        margin-bottom: 16px;
    }

    .sources-label {
        font-size: 12px;
        color: #b8a6d4;
        margin-bottom: 8px;
    }

    .source-badge {
        display: inline-block;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 12px;
        color: #e2d9f3;
        margin: 3px 4px;
    }

    /* ---------- DISCLAIMER ---------- */

    .facts-disclaimer {
        text-align: center;
        font-size: 12px;
        color: #b8a6d4;
        margin-bottom: 24px;
        padding: 0 16px;
    }

    .facts-disclaimer strong {
        color: #e2d9f3;
    }

    /* ---------- SECTION ---------- */

    .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 20px;
        margin-bottom: 12px;
        padding: 0 4px;
    }

    .section-title {
        font-size: 13px;
        font-weight: 700;
        color: #b8a6d4;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .section-link {
        font-size: 13px;
        color: #b8a6d4;
        cursor: pointer;
    }

    .section-link:hover {
        color: #e2d9f3;
    }

    /* ---------- QUESTION CARDS ---------- */

    .question-card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.15s ease;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .question-card:hover {
        background: rgba(255,255,255,0.1);
        border-color: rgba(255,255,255,0.2);
    }

    .question-icon {
        font-size: 18px;
        flex-shrink: 0;
    }

    .question-text {
        font-size: 14px;
        color: #e2d9f3;
        line-height: 1.4;
    }

    /* ---------- CHAT MESSAGES ---------- */

    [data-testid="stChatMessage"] {
        border-radius: 18px;
        margin-bottom: 12px;
        padding: 14px 16px;
    }

    /* User message bubble */
    [data-testid="stChatMessage"][data-testid*="stChatMessage-user"],
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageContent-user"]) {
        background: rgba(124, 58, 237, 0.25) !important;
        border: 2px solid rgba(124, 58, 237, 0.6) !important;
        margin-left: 40px;
        box-shadow: 0 0 12px rgba(124, 58, 237, 0.15);
    }

    /* Assistant message bubble */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageContent-assistant"]) {
        background: rgba(255,255,255,0.06) !important;
        border: 2px solid rgba(255,255,255,0.2) !important;
        margin-right: 40px;
        box-shadow: 0 0 12px rgba(255,255,255,0.05);
    }

    [data-testid="stChatMessageContent"] {
        font-size: 14px;
        color: #f3eef9;
        line-height: 1.6;
    }

    /* ---------- THINKING INDICATOR ---------- */

    .thinking-container {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 14px 16px;
        background: rgba(255,255,255,0.06);
        border: 2px solid rgba(255,255,255,0.2);
        border-radius: 18px;
        margin-bottom: 12px;
        margin-right: 40px;
        box-shadow: 0 0 12px rgba(255,255,255,0.05);
    }

    .thinking-dots {
        display: flex;
        gap: 4px;
    }

    .thinking-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #b8a6d4;
        animation: thinking-pulse 1.4s ease-in-out infinite;
    }

    .thinking-dot:nth-child(2) {
        animation-delay: 0.2s;
    }

    .thinking-dot:nth-child(3) {
        animation-delay: 0.4s;
    }

    @keyframes thinking-pulse {
        0%, 80%, 100% {
            opacity: 0.3;
            transform: scale(0.8);
        }
        40% {
            opacity: 1;
            transform: scale(1.2);
        }
    }

    .thinking-text {
        font-size: 14px;
        color: #b8a6d4;
        font-style: italic;
    }

    /* ---------- SOURCES ---------- */

    .source-label {
        font-size: 12px;
        color: #b8a6d4;
        font-weight: 600;
    }

    /* ---------- CHAT INPUT ---------- */

    .stChatInput {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #2d1b3d;
        padding: 12px 16px 16px 16px;
        z-index: 999;
    }

    .stChatInput > div {
        max-width: 480px;
        margin: 0 auto;
    }

    .stChatInput textarea {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 24px !important;
        color: #f3eef9 !important;
        font-size: 14px !important;
        padding: 12px 20px !important;
    }

    .stChatInput textarea::placeholder {
        color: #b8a6d4 !important;
    }

    .stChatInput button {
        background: #7c3aed !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
    }

    /* ---------- DISCLAIMER ---------- */

    .disclaimer {
        text-align: center;
        color: #b8a6d4;
        font-size: 11px;
        padding: 4px 0 8px 0;
    }

    /* ---------- CLEAR ---------- */

    .clear-area {
        margin-top: 10px;
    }

    /* ============================================
       RESPONSIVE: LAPTOP (min-width 768px)
       ============================================ */

    @media (min-width: 768px) {

        .block-container {
            max-width: 720px;
            padding-top: 1.5rem;
            padding-bottom: 6rem;
        }

        .hero-sparkle {
            font-size: 36px;
            margin-top: 32px;
            margin-bottom: 12px;
        }

        .hero-title {
            font-size: 42px;
            margin-bottom: 16px;
        }

        .hero-subtitle {
            font-size: 16px;
            margin-bottom: 28px;
            padding: 0 40px;
        }

        .sources-section {
            margin-bottom: 24px;
        }

        .sources-label {
            font-size: 13px;
            margin-bottom: 10px;
        }

        .source-badge {
            font-size: 13px;
            padding: 8px 18px;
            margin: 4px 6px;
        }

        .facts-disclaimer {
            font-size: 13px;
            margin-bottom: 32px;
            padding: 0 40px;
        }

        .section-header {
            margin-top: 32px;
            margin-bottom: 16px;
            padding: 0 8px;
        }

        .section-title {
            font-size: 14px;
        }

        .section-link {
            font-size: 14px;
        }

        .question-card {
            border-radius: 16px;
            padding: 18px 20px;
            margin-bottom: 12px;
        }

        .question-icon {
            font-size: 22px;
        }

        .question-text {
            font-size: 15px;
        }

        [data-testid="stChatMessage"] {
            border-radius: 20px;
            margin-bottom: 16px;
            padding: 18px 20px;
        }

        [data-testid="stChatMessageContent"] {
            font-size: 15px;
        }

        .thinking-container {
            border-radius: 20px;
            padding: 18px 20px;
            margin-bottom: 16px;
        }

        .thinking-text {
            font-size: 15px;
        }

        .stChatInput > div {
            max-width: 720px;
        }

        .stChatInput textarea {
            font-size: 15px !important;
            padding: 14px 24px !important;
        }

        .stChatInput button {
            width: 44px !important;
            height: 44px !important;
            min-width: 44px !important;
        }

        .disclaimer {
            font-size: 12px;
        }
    }

    /* ============================================
       RESPONSIVE: LARGE LAPTOP (min-width 1200px)
       ============================================ */

    @media (min-width: 1200px) {

        .block-container {
            max-width: 900px;
            padding-top: 2rem;
            padding-bottom: 7rem;
        }

        .hero-sparkle {
            font-size: 40px;
            margin-top: 40px;
        }

        .hero-title {
            font-size: 48px;
        }

        .hero-subtitle {
            font-size: 17px;
            padding: 0 80px;
        }

        .facts-disclaimer {
            padding: 0 80px;
        }

        .stChatInput > div {
            max-width: 900px;
        }
    }

    /* ============================================
       RESPONSIVE: SMALL PHONE (max-width 380px)
       ============================================ */

    @media (max-width: 380px) {

        .block-container {
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }

        .hero-title {
            font-size: 24px;
        }

        .hero-subtitle {
            font-size: 13px;
            padding: 0 8px;
        }

        .question-card {
            padding: 12px 14px;
        }

        .question-text {
            font-size: 13px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    st.session_state.chat = None

if "thinking" not in st.session_state:
    st.session_state.thinking = False


# ---------------------------------------------------------
# RAG INITIALIZATION
# ---------------------------------------------------------

def init_chat():
    if st.session_state.chat is None:
        with st.spinner("Loading AI Assist..."):
            st.session_state.chat = RAGChat()


# ---------------------------------------------------------
# ASK QUESTION
# ---------------------------------------------------------

def ask_question(question):
    """Send a question through the existing RAG pipeline."""

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    st.session_state.thinking = True
    st.rerun()


# ---------------------------------------------------------
# GENERATE ANSWER
# ---------------------------------------------------------

def generate_answer():
    """Generate the answer for the last user message."""

    if not st.session_state.messages:
        return

    last_message = st.session_state.messages[-1]

    if last_message["role"] != "user":
        return

    question = last_message["content"]

    # Show thinking indicator
    thinking_placeholder = st.markdown(
        """
        <div class="thinking-container">
            <div class="thinking-dots">
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
            </div>
            <span class="thinking-text">Thinking...</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Generate answer
    result = st.session_state.chat.ask(question)

    # Remove thinking indicator
    thinking_placeholder.empty()

    # Save answer to messages
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result.get("sources", []),
        }
    )

    st.session_state.thinking = False


# ---------------------------------------------------------
# CLEAR CHAT
# ---------------------------------------------------------

def clear_chat():
    st.session_state.messages = []
    st.session_state.thinking = False

    if st.session_state.chat:
        st.session_state.chat.memory.clear()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

def render_header():

    left, center, right = st.columns([1, 5, 1])

    with left:
        if st.button("‹", key="back_button"):
            st.session_state.messages = []
            st.session_state.thinking = False
            st.rerun()

    with center:
        st.markdown(
            """
            <div class="header-title-group" style="justify-content: center;">
                <span class="header-dot"></span>
                <span class="header-title">AI Assist</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.button("⋯", key="menu_button")


# ---------------------------------------------------------
# WELCOME SCREEN
# ---------------------------------------------------------

def render_welcome():

    st.markdown(
        '<div class="hero-sparkle">✦</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-title">
            Know your HDFC fund<br>
            before you invest in it.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-subtitle">
            Ask about expense ratios, exit loads, lock-in periods,
            benchmarks and fund managers. Every answer links back
            to the official page it came from.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# SOURCES
# ---------------------------------------------------------

def render_sources():

    st.markdown(
        """
        <div class="sources-section">
            <div class="sources-label">Answers from</div>
            <span class="source-badge">HDFC Mutual Fund</span>
            <span class="source-badge">SEBI</span>
            <span class="source-badge">AMFI</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="facts-disclaimer">
            <strong>Facts only.</strong> This assistant does not give investment advice.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# TRY ASKING
# ---------------------------------------------------------

def render_try_asking():

    st.markdown(
        """
        <div class="section-header">
            <span class="section-title">Try asking</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-link" style="text-align: center; margin-bottom: 12px; font-size: 13px; color: #b8a6d4;">Tap a question to start</div>',
        unsafe_allow_html=True,
    )

    questions = [
        {
            "icon": "💡",
            "text": "What is the expense ratio of HDFC Large Cap Fund?",
            "question": "What is the expense ratio of HDFC Large Cap Fund?",
        },
        {
            "icon": "📊",
            "text": "What is the exit load of HDFC Flexi Cap Fund?",
            "question": "What is the exit load of HDFC Flexi Cap Fund?",
        },
        {
            "icon": "🔔",
            "text": "Who is the fund manager of HDFC ELSS Tax Saver?",
            "question": "Who is the fund manager of HDFC ELSS Tax Saver?",
        },
        {
            "icon": "💰",
            "text": "What is the benchmark of HDFC Small Cap Fund?",
            "question": "What is the benchmark of HDFC Small Cap Fund?",
        },
    ]

    for q in questions:
        if st.button(
            f"{q['icon']}  {q['text']}",
            key=f"question_{q['text'][:20].replace(' ', '_')}",
        ):
            ask_question(q["question"])
            st.rerun()


# ---------------------------------------------------------
# CHAT HISTORY
# ---------------------------------------------------------

def render_messages():

    for i, message in enumerate(st.session_state.messages):

        role = message["role"]

        # Show thinking indicator after last user message
        if st.session_state.thinking and i == len(st.session_state.messages) - 1:
            with st.chat_message("user"):
                st.markdown(message.get("content", ""))

            # Show thinking indicator
            st.markdown(
                """
                <div class="thinking-container">
                    <div class="thinking-dots">
                        <div class="thinking-dot"></div>
                        <div class="thinking-dot"></div>
                        <div class="thinking-dot"></div>
                    </div>
                    <span class="thinking-text">Thinking...</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            continue

        with st.chat_message(role):

            content = message.get("content", "")

            if content:
                st.markdown(content)

            if role == "assistant":

                sources = message.get("sources", [])

                if sources:

                    with st.expander(
                        f"📚 Sources ({len(sources)})"
                    ):

                        for j, source in enumerate(sources, start=1):

                            chunk_index = (
                                source.get("chunk_index", 0) + 1
                            )

                            similarity = source.get(
                                "similarity",
                                0,
                            )

                            source_text = source.get(
                                "text",
                                "",
                            )

                            st.markdown(
                                f"**Source {j} — Chunk {chunk_index}**"
                            )

                            st.caption(
                                f"Similarity: {similarity:.4f}"
                            )

                            if source_text:
                                st.write(source_text[:500])

                            st.divider()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    init_chat()

    render_header()

    # Show welcome UI until conversation begins
    if not st.session_state.messages:

        render_welcome()

        render_sources()

        render_try_asking()

    else:

        render_messages()

        # Generate answer if thinking
        if st.session_state.thinking:
            generate_answer()
            st.rerun()

    # Chat input
    prompt = st.chat_input(
        "Ask anything about HDFC mutual funds..."
    )

    if prompt:

        ask_question(prompt)

        st.rerun()

    # Disclaimer
    st.markdown(
        '<div class="disclaimer">AI generated analysis. Please verify before making decisions.</div>',
        unsafe_allow_html=True,
    )

    # Clear conversation
    if st.session_state.messages:

        st.markdown(
            '<div class="clear-area"></div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "Clear conversation",
            key="clear_conversation",
        ):
            clear_chat()
            st.rerun()


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
