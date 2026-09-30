# Architecture — Groww Mutual Fund FAQ Assistant

## 1. System Overview

A **facts-only RAG chatbot** that answers questions about HDFC mutual fund schemes using only official public pages from Groww. Every answer includes one source link. No investment advice.

Two-phase architecture:
1. **Ingestion Pipeline** (one-time): Load → Chunk → Embed → Store in ChromaDB
2. **Query Pipeline** (per question): Embed → Retrieve → Generate

---

## 2. Components

### 2.1 Ingestion Pipeline

| Component | Responsibility |
|-----------|---------------|
| **Loader** | Fetches 5 public Groww pages for HDFC schemes |
| **Chunker** | Splits pages into overlapping chunks with metadata (source URL, char count, chunk index) |
| **Embedder** | Converts each chunk into a 384-dim vector using `all-MiniLM-L6-v2` |
| **Vector Store** | Stores embeddings + metadata in ChromaDB at `data/chroma/` |

### 2.2 Query Pipeline

| Component | Responsibility |
|-----------|---------------|
| **Query Embedder** | Converts the user's question into a vector using the same model |
| **Retriever** | Searches ChromaDB for top-k most similar chunks |
| **Context Builder** | Formats retrieved chunks into a context string for the LLM |
| **LLM Client** | Sends system prompt + context + question to Groq API |
| **Guardrails** | Refuses opinionated questions, enforces facts-only answers |

### 2.3 User Interface

| Component | Responsibility |
|-----------|---------------|
| **Welcome line** | Greets users with example questions |
| **Disclaimer** | "Facts-only. No investment advice." |
| **Chat interface** | Message history with sources expander |
| **Clear-chat button** | Resets conversation |

### 2.4 Supporting Components

| Component | Responsibility |
|-----------|---------------|
| **Conversation Memory** | Stores last 10 messages, rewrites follow-up questions |
| **Environment Loader** | Loads `GROQ_API_KEY` and `GROQ_MODEL` from `.env` |

---

## 3. Data Flow

### 3.1 Ingestion Flow (One-Time)

```
┌─────────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ 5 Groww     │────►│ Loader  │────►│ Chunker │────►│ Embedder│────►│ ChromaDB│
│ Pages       │     │         │     │         │     │         │     │ data/   │
└─────────────┘     └─────────┘     └────┬────┘     └─────────┘     └─────────┘
                                         │
                                         ▼
                                  ┌─────────────┐
                                  │ data/chunks/│
                                  │ chunks.txt  │
                                  └─────────────┘
```

**Steps:**
1. **Load**: Fetch 5 Groww pages for HDFC schemes
2. **Chunk**: Split into overlapping chunks (500 chars, 50 overlap). Metadata: `source_url`, `char_count`, `chunk_index`
3. **Embed**: Pass each chunk through `all-MiniLM-L6-v2` → 384-dim vector
4. **Store**: Save vectors + metadata to ChromaDB at `data/chroma/`

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
                                                            │ + Source │
                                                            └──────────┘
```

**Steps:**
1. **Receive**: User types a question
2. **Memory Check**: Rewrite follow-up questions using conversation history
3. **Guardrail Check**: Refuse opinionated/advice questions
4. **Embed**: Convert question into vector using same model
5. **Retrieve**: Search ChromaDB for top-k chunks
6. **Context Check**: If no relevant chunks, respond "I don't know"
7. **Build Context**: Format retrieved chunks
8. **Generate**: Send system prompt + context + question to Groq LLM
9. **Return**: Answer + source link + "Last updated from sources:"

---

## 4. Tech Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Language | Python | 3.10+ | Core runtime |
| Embedding Model | `sentence-transformers/all-MiniLM-L6-v2` | latest | Local text embeddings (384-dim) |
| Vector DB | ChromaDB | latest | Persistent vector storage |
| LLM | Groq API | — | Answer generation (free tier) |
| Env Management | `python-dotenv` | latest | Load `.env` variables |
| UI | Streamlit | latest | Web chat interface |
| Deployment | Render | — | Cloud hosting |

---

## 5. Folder Structure

```
rag-chatbot/
├── data/
│   ├── raw/
│   │   └── source.txt              # Collected Groww pages text
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
│   ├── config.py                   # Configuration
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── loader.py               # Load source pages
│   │   ├── chunker.py              # Split into chunks
│   │   ├── embedder.py             # Embed chunks
│   │   └── run.py                  # Orchestrate ingestion
│   ├── query/
│   │   ├── __init__.py
│   │   ├── retriever.py            # Search ChromaDB
│   │   ├── guardrails.py           # Facts-only checks
│   │   ├── memory.py               # Conversation memory
│   │   └── llm.py                  # Groq API client
│   ├── chat.py                     # Main RAG pipeline
│   ├── cli.py                      # CLI interface
│   └── app.py                      # Streamlit UI
├── .env                            # API keys (NEVER commit)
├── .env.example                    # Template for .env
├── .gitignore                      # Excludes .env, venv, __pycache__, data/chroma/
├── requirements.txt                # Python dependencies
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
                    ┌────│  Opinionated?   │────┐
                    │No  │  (Guardrails)   │    │Yes
                    │    └─────────────────┘    │
                    ▼                           ▼
           ┌──────────────┐          ┌─────────────────┐
           │  Rewrite using│          │  "I can only    │
           │  Memory      │          │  answer factual │
           │  (if history)│          │  questions.     │
           └──────┬───────┘          │  No investment  │
                  │                  │  advice."       │
                  ▼                  └─────────────────┘
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
 │  know..."    │          │  (top-k chunks) │
 └──────────────┘          └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │  Send to Groq   │
                          │  LLM            │
                          │  (system prompt │
                          │  + context +    │
                          │  question)      │
                          └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │  Display Answer │
                          │  + Source Link  │
                          │  + "Last updated│
                          │  from sources:" │
                          └─────────────────┘
```

---

## 7. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Local embedding model** | No API key needed, runs offline, fast |
| **Same model for chunks + queries** | Ensures same vector space for accurate similarity |
| **ChromaDB persisted to disk** | Ingestion runs once |
| **Groq for LLM** | Free tier, fast inference |
| **Facts-only guardrails** | Prevents investment advice |
| **Source link in every answer** | Transparency and trust |
| **Answers ≤3 sentences** | Clarity and conciseness |
| **No PII storage** | Privacy and security |
| **Streamlit for UI** | Fastest way to build chat UI in Python |

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

---

## 9. Document History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 1.0 | 2026-09-30 | AI Coding Agent | Updated architecture for Groww HDFC Mutual Fund FAQ Assistant |
