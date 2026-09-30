# Product Requirements Document (PRD) — RAG Chatbot

## 1. Goal

Build a **Retrieval-Augmented Generation (RAG) chatbot** for a class demo that answers questions using information from a provided document. The chatbot ingests a source document, chunks it, embeds the chunks into a vector database, retrieves relevant chunks at query time, and generates answers using a Large Language Model (LLM) grounded in the retrieved context.

The system is designed to be built incrementally with an AI coding agent (Cursor or OpenCode), with each phase verified before moving to the next.

---

## 2. Target Users

| User | Description |
|------|-------------|
| **Students** | Learners in the class who will use the chatbot to ask questions about the course material and see how RAG works. |
| **Instructor** | The teacher who demonstrates the RAG pipeline, explains each phase, and evaluates the final product. |
| **Developer (you)** | The person building the chatbot alongside an AI coding agent, following the phased implementation plan. |

---

## 3. In-Scope Features

### 3.1 Data Ingestion Pipeline
- **Loading**: Read a source text document from `data/raw/`.
- **Chunking**: Split the document into overlapping chunks with metadata (source, character count, chunk index). The AI agent inspects the data and proposes a chunking strategy before writing code.
- **Embedding**: Convert each chunk into a 384-dimension vector using `sentence-transformers/all-MiniLM-L6-v2` (local, no API key needed).
- **Vector Storage**: Store embeddings in ChromaDB, persisted to disk so ingestion runs once.

### 3.2 Retrieval + Answer Generation
- **Query Embedding**: Embed the user's question using the *same* embedding model.
- **Similarity Search**: Retrieve the top-k most relevant chunks from ChromaDB.
- **LLM Answer**: Send system prompt + retrieved chunks + user question to Groq's LLM to generate a grounded answer.
- **Source Attribution**: Show which chunks were retrieved for each answer.

### 3.3 Guardrails
- Refuse off-topic questions (questions unrelated to the source document).
- Do not give advice outside the source content.
- Say "I don't know" when retrieved context does not answer the question.

### 3.4 Conversation Memory
- Keep the last 10 messages in memory.
- Rewrite follow-up questions using conversation history before retrieval (e.g., resolve pronouns like "its" from earlier context).

### 3.5 User Interface
- **CLI**: A command-line interface for testing questions during development.
- **Streamlit Web UI**: A chat interface with message history, a "sources" expander under each answer, and a clear-chat button.

### 3.6 Deployment
- Push code to GitHub (excluding `.env` and ChromaDB data).
- Deploy to Render as a Web Service with automatic redeploys on git push.
- Vector DB is rebuilt during the Render build step.

---

## 4. Out-of-Scope Features

| Feature | Reason |
|---------|--------|
| Multi-document support (beyond a single source file) | Class demo uses one document. |
| User authentication / multi-user support | Single-user demo. |
| Streaming token-by-token responses in the UI | Not required for the demo. |
| Fine-tuning the embedding model | Using a pre-trained model is sufficient. |
| Hosted vector DB (e.g., Pinecone, Weaviate) | ChromaDB local persistence meets requirements. |
| Mobile app | Web UI is sufficient. |
| Voice input / output | Not part of the demo. |
| Admin dashboard for managing documents | Single-document ingestion is manual. |

---

## 5. Example User Questions

### Answerable (on-topic)
- "What is the main topic of the document?"
- "Summarize the key points."
- "What are the steps involved in the process?"
- "Explain the data flow described in the document."

### Off-topic (should be refused)
- "What's the weather like today?"
- "Write a poem about the ocean."
- "What is the capital of France?"

### Tricky (requires good retrieval)
- "How does X relate to Y?" (where X and Y are mentioned in different sections)
- "What are the trade-offs?" (requires synthesizing multiple chunks)
- Follow-up: "What about its fees?" (requires conversation memory to resolve "its")

---

## 6. Success Criteria

| # | Criterion | How to Verify |
|---|-----------|---------------|
| 1 | The ingestion pipeline produces chunks saved to `data/chunks/chunks.txt` with metadata. | Open the file and inspect chunk count, source labels, and character counts. |
| 2 | Embeddings are stored in ChromaDB and persist across restarts. | Run ingestion, restart the process, query without re-ingesting. |
| 3 | The system retrieves relevant chunks for on-topic questions. | Check that retrieved chunks contain keywords/semantic matches to the question. |
| 4 | The LLM generates answers grounded in the retrieved context. | Answers should reference information from the chunks, not hallucinate. |
| 5 | Off-topic questions are refused. | Ask an unrelated question; the bot should decline to answer. |
| 6 | When context is insufficient, the bot says "I don't know." | Ask a question whose answer is not in the document. |
| 7 | Follow-up questions resolve pronouns using conversation memory. | Ask "What about its fees?" after discussing a specific topic. |
| 8 | The Streamlit UI shows message history, sources, and a clear-chat button. | Interact with the UI and confirm all elements work. |
| 9 | The app deploys successfully on Render. | Open the Render URL and ask a question. |
| 10 | `.env` and ChromaDB data are never committed to Git. | Check `.gitignore` and git log. |

---

## 7. Constraints

| Constraint | Detail |
|------------|--------|
| **Free-tier tools only** | Groq API (free tier), local embedding model (no cost), ChromaDB (open source), Streamlit (open source), Render (free tier). |
| **Runs locally** | The entire pipeline (embedding, vector DB, LLM API calls) must work on a local machine with Python 3.10+. |
| **Deployable to Render** | The app must be deployable as a Render Web Service with a build command that rebuilds the vector DB and a start command that runs the UI. |
| **API key security** | The Groq API key is stored in `.env`, loaded via `python-dotenv`, and never committed to Git or pasted into chat. |
| **Same embedding model** | The same model (`all-MiniLM-L6-v2`) must be used for both chunk embedding and query embedding to ensure vector space consistency. |
| **Readable chunks** | All chunks must be saved to a human-readable `.txt` file for inspection. |
| **Python 3.10+** | The project targets Python 3.10 or higher. |

---

## 8. Tech Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.10+ | Core language |
| Embedding Model | `sentence-transformers/all-MiniLM-L6-v2` | Local text embeddings (384-dim) |
| Vector DB | ChromaDB | Store and search embeddings |
| LLM | Groq API | Answer generation |
| CLI | Python `input()` | Development testing |
| UI | Streamlit | Web chat interface |
| Deployment | Render | Cloud hosting |
| Env Management | `python-dotenv` | Load API keys from `.env` |

---

## 9. High-Level Flow

```
┌─────────────────────────────────────────────────────────┐
│                    INGESTION (One-time)                  │
│                                                         │
│  Source Document → Load → Chunk → Embed → ChromaDB      │
│                                                         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   QUERY (Per question)                   │
│                                                         │
│  User Question → Embed → Search ChromaDB → Top-k Chunks │
│                                                         │
│  System Prompt + Chunks + Question → Groq LLM → Answer  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 10. Document History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 1.0 | 2026-09-30 | AI Coding Agent | Initial PRD based on ProblemStatement.txt |
