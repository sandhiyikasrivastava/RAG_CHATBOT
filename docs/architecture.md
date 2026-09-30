# Architecture — RAG Chatbot

## 1. System Overview

The RAG Chatbot is a Python-based application that answers user questions using information retrieved from a source document. It follows a two-phase architecture:

1. **Ingestion Pipeline** (one-time): Load → Chunk → Embed → Store in ChromaDB
2. **Query Pipeline** (per question): Embed → Retrieve → Generate

The system uses a local embedding model for vectorization, ChromaDB for vector storage, and Groq's API for answer generation.

---

## 2. Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                        RAG CHATBOT SYSTEM                           │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐      │
│  │   Ingestion  │    │    Query     │    │       UI         │      │
│  │   Pipeline   │    │   Pipeline   │    │   (CLI + Web)    │      │
│  └──────┬───────┘    └──────┬───────┘    └────────┬─────────┘      │
│         │                   │                      │                │
│         ▼                   ▼                      ▼                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐      │
│  │  Embedding   │◄──►│  ChromaDB    │    │  Conversation    │      │
│  │    Model     │    │  (Persistent)│    │     Memory       │      │
│  └──────────────┘    └──────────────┘    └──────────────────┘      │
│         │                   │                                       │
│         ▼                   ▼                                       │
│  ┌──────────────┐    ┌──────────────┐                              │
│  │  sentence-   │    │   Groq API   │                              │
│  │ transformers │    │   (LLM)      │                              │
│  └──────────────┘    └──────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.1 Ingestion Pipeline

| Component | Responsibility |
|-----------|---------------|
| **Loader** | Reads the source document from `data/raw/` and produces raw text. |
| **Chunker** | Splits raw text into overlapping chunks with metadata (source, character count, chunk index). Saves chunks to `data/chunks/chunks.txt`. |
| **Embedder** | Converts each chunk into a 384-dimension vector using `sentence-transformers/all-MiniLM-L6-v2`. |
| **Vector Store** | Stores embeddings + metadata in ChromaDB, persisted to `data/chroma/`. |

### 2.2 Query Pipeline

| Component | Responsibility |
|-----------|---------------|
| **Query Embedder** | Converts the user's question into a vector using the *same* embedding model. |
| **Retriever** | Searches ChromaDB for the top-k most similar chunks (cosine similarity). |
| **Context Builder** | Formats retrieved chunks into a context string for the LLM. |
| **LLM Client** | Sends system prompt + context + question to Groq API and returns the answer. |
| **Guardrails** | Checks if the question is on-topic and if the context is sufficient before generating an answer. |

### 2.3 User Interface

| Component | Responsibility |
|-----------|---------------|
| **CLI** | Command-line interface for testing questions during development. Shows retrieved chunks. |
| **Streamlit App** | Web chat interface with message history, sources expander, and clear-chat button. |

### 2.4 Supporting Components

| Component | Responsibility |
|-----------|---------------|
| **Conversation Memory** | Stores the last 10 messages and rewrites follow-up questions to resolve pronouns. |
| **Environment Loader** | Loads `GROQ_API_KEY` and `GROQ_MODEL` from `.env` via `python-dotenv`. |

---

## 3. Data Flow

### 3.1 Ingestion Flow (One-Time)

```
┌─────────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ data/raw/   │────►│ Loader  │────►│ Chunker │────►│ Embedder│────►│ ChromaDB│
│ source.txt  │     │         │     │         │     │         │     │ data/   │
└─────────────┘     └─────────┘     └────┬────┘     └─────────┘     └─────────┘
                                         │
                                         ▼
                                  ┌─────────────┐
                                  │ data/chunks/│
                                  │ chunks.txt  │
                                  └─────────────┘
```

**Steps:**
1. **Load**: Read `data/raw/source.txt` into a string.
2. **Chunk**: Split text into overlapping chunks (e.g., 500 chars, 50 overlap). Each chunk gets metadata: `source`, `char_count`, `chunk_index`. Save all chunks to `data/chunks/chunks.txt`.
3. **Embed**: Pass each chunk through `all-MiniLM-L6-v2` to get a 384-dim vector.
4. **Store**: Save vectors + metadata to ChromaDB at `data/chroma/`.

### 3.2 Query Flow (Per Question)

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  User    │───►│  Query   │───►│  Search  │───►│  Build   │───►│  Groq    │
│ Question │    │ Embedder │    │ ChromaDB │    │ Context  │    │   LLM    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                                   │
                                                                   ▼
                                                            ┌──────────┐
                                                            │  Answer  │
                                                            └──────────┘
```

**Steps:**
1. **Receive**: User types a question (CLI or Streamlit).
2. **Memory Check**: If conversation history exists, rewrite the question to resolve pronouns.
3. **Guardrail Check**: Determine if the question is on-topic. If off-topic, refuse.
4. **Embed**: Convert the (possibly rewritten) question into a vector using the same embedding model.
5. **Retrieve**: Search ChromaDB for the top-k most similar chunks (e.g., k=3).
6. **Context Check**: If no relevant chunks found, respond "I don't know."
7. **Build Context**: Format retrieved chunks into a context string.
8. **Generate**: Send system prompt + context + question to Groq LLM.
9. **Return**: Display the answer with source attribution.

---

## 4. Tech Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Language | Python | 3.10+ | Core runtime |
| Embedding Model | `sentence-transformers/all-MiniLM-L6-v2` | latest | Local text embeddings (384-dim) |
| Vector DB | ChromaDB | latest | Persistent vector storage |
| LLM | Groq API | — | Answer generation (free tier) |
| Env Management | `python-dotenv` | latest | Load `.env` variables |
| CLI | Python `input()` | built-in | Development testing |
| Web UI | Streamlit | latest | Chat interface |
| HTTP Client | `requests` or `groq` SDK | latest | Groq API calls |
| Deployment | Render | — | Cloud hosting |

---

## 5. Folder Structure

```
rag-chatbot/
├── data/
│   ├── raw/
│   │   └── source.txt              # Original source document
│   ├── chunks/
│   │   └── chunks.txt              # Numbered chunks with metadata
│   ├── chroma/
│   │   └── (ChromaDB persistent files)
│   └── embeddings_preview.txt      # First 5 embeddings (10 dims each)
├── docs/
│   ├── PRD.md                      # Product Requirements Document
│   ├── architecture.md             # This file
│   └── implementation.md           # Phased implementation plan
├── src/
│   ├── __init__.py
│   ├── config.py                   # Configuration (model names, paths, top-k)
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── loader.py               # Load source document
│   │   ├── chunker.py              # Split into chunks
│   │   ├── embedder.py             # Embed chunks
│   │   └── run.py                  # Orchestrate ingestion
│   ├── query/
│   │   ├── __init__.py
│   │   ├── retriever.py            # Search ChromaDB
│   │   ├── guardrails.py           # Off-topic / insufficient context checks
│   │   ├── memory.py               # Conversation memory + question rewrite
│   │   └── llm.py                  # Groq API client
│   ├── chat.py                     # Main RAG pipeline (combine all)
│   ├── cli.py                      # CLI interface
│   └── app.py                      # Streamlit UI
├── design/
│   └── stitch/                     # (Optional) Google Stitch export
├── .env                            # API keys (NEVER commit)
├── .env.example                    # Template for .env
├── .gitignore                      # Excludes .env, venv, __pycache__, data/chroma/
├── requirements.txt                # Python dependencies
├── ProblemStatement.txt            # Original problem statement
└── README.md                       # Project overview
```

---

## 6. Query Flow Diagram

```
                         ┌─────────────────┐
                         │   User Types    │
                         │   a Question    │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                    ┌────│  On-Topic?      │────┐
                    │No  │  (Guardrails)   │    │Yes
                    │    └─────────────────┘    │
                    ▼                           ▼
           ┌──────────────┐          ┌─────────────────┐
           │  "Sorry, I   │          │  Rewrite using  │
           │  can only    │          │  Conversation   │
           │  answer      │          │  Memory         │
           │  questions   │          │  (if history)   │
           │  about the   │          └────────┬────────┘
           │  document."  │                   │
           └──────────────┘                   ▼
                                     ┌─────────────────┐
                                     │  Embed Question │
                                     │  (same model)   │
                                     └────────┬────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                ┌────│  Relevant       │────┐
                                │No  │  Chunks Found?  │    │Yes
                                │    └─────────────────┘    │
                                ▼                           ▼
                       ┌──────────────┐          ┌─────────────────┐
                       │  "I don't    │          │  Build Context  │
                       │  know. The   │          │  (top-k chunks) │
                       │  document    │          └────────┬────────┘
                       │  doesn't     │                   │
                       │  contain     │                   ▼
                       │  enough      │          ┌─────────────────┐
                       │  information.│          │  Send to Groq   │
                       │  "           │          │  LLM            │
                       └──────────────┘          │  (system prompt │
                                                 │  + context +    │
                                                 │  question)      │
                                                 └────────┬────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │  Display Answer │
                                                 │  + Sources      │
                                                 └─────────────────┘
```

---

## 7. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Local embedding model** | No API key needed, runs offline, fast for a class demo. |
| **Same model for chunks + queries** | Ensures vectors live in the same space for accurate similarity search. |
| **ChromaDB persisted to disk** | Ingestion runs once; no need to re-embed on every restart. |
| **Groq for LLM** | Free tier, fast inference, simple API. |
| **`.env` for API keys** | Security best practice; never commit secrets. |
| **Readable chunks file** | Students can inspect what the bot "knows." |
| **Conversation memory (last 10)** | Resolves pronouns in follow-ups without excessive token usage. |
| **Guardrails before LLM call** | Saves API calls and prevents hallucination on off-topic questions. |
| **Streamlit for UI** | Fastest way to build a chat UI in Python; deployable to Render. |

---

## 8. Deployment Architecture (Render)

```
┌─────────────────────────────────────────────────────────┐
│                        RENDER                            │
│                                                         │
│  Build Command:                                         │
│  pip install -r requirements.txt && python -m src.ingest.run│
│                                                         │
│  Start Command:                                         │
│  python -m streamlit run src/app.py --server.port $PORT│
│    --server.address 0.0.0.0 --server.headless true     │
│                                                         │
│  Environment Variables:                                 │
│  GROQ_API_KEY=xxx                                       │
│  GROQ_MODEL=xxx                                         │
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌────────────┐  │
│  │   Build     │───►│  Ingestion  │───►│  ChromaDB  │  │
│  │   Step      │    │  Pipeline   │    │  (ephemeral)│  │
│  └─────────────┘    └─────────────┘    └────────────┘  │
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌────────────┐  │
│  │  Streamlit  │◄───│  RAG Query  │◄───│   Groq     │  │
│  │  UI         │    │  Pipeline   │    │   API      │  │
│  └─────────────┘    └─────────────┘    └────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

> **Note**: On Render, the ChromaDB is ephemeral (rebuilt on each deploy). The build command runs ingestion to repopulate the vector DB before the app starts.

---

## 9. Document History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 1.0 | 2026-09-30 | AI Coding Agent | Initial architecture based on PRD.md |
