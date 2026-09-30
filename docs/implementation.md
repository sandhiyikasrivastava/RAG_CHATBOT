# Implementation Plan — Groww Mutual Fund FAQ Assistant

This document breaks the build into 6 phases. Each phase lists the files to create, what the phase does, and how to verify it works before moving on.

---

## Phase 1: Project Setup

### What this does
Creates the project skeleton: folder structure, dependencies, and gitignore rules so secrets are never committed.

### Files to create

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies |
| `.gitignore` | Excludes `.env`, `venv/`, `__pycache__/`, `data/chroma/` |
| `.env.example` | Template with `GROQ_API_KEY=` and `GROQ_MODEL=` |
| `src/__init__.py` | Makes `src` a Python package |
| `src/config.py` | Central configuration (model names, paths, top-k) |
| `src/ingest/__init__.py` | Makes `ingest` a sub-package |
| `src/query/__init__.py` | Makes `query` a sub-package |

### How to verify
- [ ] `pip install -r requirements.txt` completes without errors.
- [ ] `python -c "import src.config"` runs without import errors.
- [ ] `.env` is listed in `.gitignore`.

---

## Phase 2: Loading & Chunking

### What this does
Fetches 5 Groww pages for HDFC mutual fund schemes, splits them into overlapping chunks with metadata, and saves them to a readable file.

### Files to create

| File | Purpose |
|------|---------|
| `data/raw/source.txt` | Collected text from 5 Groww pages |
| `src/ingest/loader.py` | Fetches and combines the 5 pages |
| `src/ingest/chunker.py` | Splits text into chunks with metadata |
| `src/ingest/run.py` | Orchestrates load → chunk → save |

### Chunker strategy
- **Chunk size**: 500 characters
- **Overlap**: 50 characters
- **Metadata per chunk**: `chunk_index`, `source_url`, `char_count`
- **Output format** in `data/chunks/chunks.txt`

### How to verify
- [ ] `python -m src.ingest.run` completes without errors.
- [ ] `data/chunks/chunks.txt` exists and is readable.
- [ ] Chunks are numbered with source URLs and character counts.
- [ ] Spot-check that chunk text matches the Groww pages.

---

## Phase 3: Embedding & Vector Store

### What this does
Converts each chunk into a 384-dimension vector using `all-MiniLM-L6-v2` and stores them in ChromaDB on disk.

### Files to create

| File | Purpose |
|------|---------|
| `src/ingest/embedder.py` | Loads the embedding model and embeds text |
| `src/ingest/run.py` | (Update) Add embed + store steps |
| `data/embeddings_preview.txt` | First 5 embeddings, first 10 dimensions each |

### ChromaDB settings
- **Persistent directory**: `data/chroma/`
- **Collection name**: `documents`
- **Distance metric**: cosine (default)

### How to verify
- [ ] `python -m src.ingest.run` completes without errors.
- [ ] `data/chroma/` directory is created.
- [ ] `data/embeddings_preview.txt` exists.
- [ ] Vectors persist across restarts.

---

## Phase 4: Guardrails

### What this does
Adds checks to refuse opinionated questions, enforce facts-only answers, and say "I don't know" when context is insufficient.

### Files to create

| File | Purpose |
|------|---------|
| `src/query/guardrails.py` | Opinionated question detection and context sufficiency checks |

### Guardrail logic
1. **Opinionated check**: Detect questions like "Should I buy/sell?" → refuse with polite message
2. **Off-topic check**: Compare question embedding against all chunks. If best similarity < 0.3, refuse.
3. **Context sufficiency**: If retrieved chunks don't contain enough relevant info, respond "I don't know."
4. **No advice**: System prompt instructs LLM to only use provided context, never give advice.
5. **No PII**: Reject questions containing PAN, Aadhaar, account numbers, etc.
6. **Answer format**: ≤3 sentences + source link + "Last updated from sources:"

### How to verify
- [ ] Ask "Should I buy HDFC Large Cap Fund?" → bot refuses.
- [ ] Ask "What is the expense ratio?" → bot answers with source link.
- [ ] Ask "What's the weather?" → bot refuses (off-topic).
- [ ] Ask a question not in the pages → bot says "I don't know."

---

## Phase 5: Retrieval + LLM Answer

### What this does
Embeds the user's question, retrieves top-k chunks from ChromaDB, sends them to Groq's LLM with a system prompt, and returns the answer with source link.

### Files to create

| File | Purpose |
|------|---------|
| `src/query/retriever.py` | Embeds query and searches ChromaDB |
| `src/query/llm.py` | Groq API client |
| `src/chat.py` | Main RAG pipeline |
| `src/cli.py` | CLI interface for testing |

### System prompt template
```
You are a facts-only assistant for HDFC mutual fund schemes.
Rules:
1. Only use information from the context below to answer.
2. If the context doesn't contain the answer, say "I don't know."
3. Never give investment advice.
4. Keep answers to 3 sentences or less.
5. Include one source link from the context.
6. End with "Last updated from sources: [date]".

Context:
{retrieved_chunks}

Question: {user_question}
```

### How to verify
- [ ] `python -m src.cli` starts and prompts for a question.
- [ ] Ask a factual question → answer includes source link.
- [ ] Ask an opinionated question → bot refuses.
- [ ] Type "quit" → CLI exits cleanly.

---

## Phase 6: UI (Streamlit)

### What this does
Builds a web chat interface with welcome line, example questions, disclaimer, message history, sources expander, and clear-chat button.

### Files to create

| File | Purpose |
|------|---------|
| `src/app.py` | Streamlit chat UI |

### UI requirements
- **Welcome line**: "Welcome! Ask me facts about HDFC mutual fund schemes."
- **3 example questions**: Clickable suggestion chips
- **Disclaimer**: "Facts-only. No investment advice."
- **Message history**: Chat layout
- **Sources expander**: Retrieved chunks under each answer
- **Clear-chat button**: Resets conversation
- **Conversation memory**: Last 10 messages for follow-up context

### How to verify
- [ ] `streamlit run src/app.py` starts the app.
- [ ] Welcome line and 3 example questions are visible.
- [ ] Disclaimer is displayed.
- [ ] Ask a question → answer appears with source link.
- [ ] Click "Sources" → retrieved chunks shown.
- [ ] Click "Clear chat" → conversation resets.
- [ ] Ask a follow-up question → pronoun resolution works.

---

## Summary: Phase Completion Checklist

| Phase | Key Verification |
|-------|-----------------|
| 1. Setup | `pip install` works, `.env` is gitignored |
| 2. Chunking | `chunks.txt` exists with numbered chunks + metadata |
| 3. Embedding | ChromaDB persists, embeddings preview file exists |
| 4. Guardrails | Opinionated questions refused, insufficient context says "I don't know" |
| 5. Retrieval + LLM | CLI answers questions with source links |
| 6. UI | Streamlit app runs with welcome line, disclaimer, sources, clear button |

---

## Render Deployment Values

| Setting | Value |
|---------|-------|
| Root Directory | *(leave blank)* |
| Build Command | `pip install -r requirements.txt && python -m src.ingest.run` |
| Start Command | `python -m streamlit run src/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true` |
| Environment Variables | `GROQ_API_KEY`, `GROQ_MODEL` |

---

## Document History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 1.0 | 2026-09-30 | AI Coding Agent | Updated implementation plan for Groww HDFC Mutual Fund FAQ Assistant |
