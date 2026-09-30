# Implementation Plan — RAG Chatbot

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

### `requirements.txt` contents
```
sentence-transformers
chromadb
groq
python-dotenv
streamlit
```

### `.gitignore` contents
```
.env
venv/
__pycache__/
data/chroma/
*.pyc
```

### How to verify
- [ ] `pip install -r requirements.txt` completes without errors.
- [ ] `python -c "import src.config"` runs without import errors.
- [ ] `.env` is listed in `.gitignore` (run `git check-ignore .env` to confirm).

---

## Phase 2: Loading & Chunking

### What this does
Loads the source document from `data/raw/`, splits it into overlapping chunks with metadata, and saves them to a readable file for inspection.

### Files to create

| File | Purpose |
|------|---------|
| `data/raw/source.txt` | Copy the source document here |
| `src/ingest/loader.py` | Reads the source file and returns raw text |
| `src/ingest/chunker.py` | Splits text into chunks with metadata |
| `src/ingest/run.py` | Orchestrates load → chunk → save |

### Chunker strategy (proposed)
- **Chunk size**: 500 characters
- **Overlap**: 50 characters
- **Metadata per chunk**: `chunk_index`, `source` (filename), `char_count`
- **Output format** in `data/chunks/chunks.txt`:
  ```
  === Chunk 1 ===
  Source: source.txt
  Characters: 500
  ---
  [chunk text]

  === Chunk 2 ===
  ...
  ```

### How to verify
- [ ] `python -m src.ingest.run` completes without errors.
- [ ] `data/chunks/chunks.txt` exists and is readable.
- [ ] Open `chunks.txt` and confirm chunks are numbered, have source labels, and character counts.
- [ ] Count the chunks and confirm the number is reasonable for the document size.
- [ ] Spot-check that chunk text matches the source document.

---

## Phase 3: Embedding & Vector Store

### What this does
Converts each chunk into a 384-dimension vector using `all-MiniLM-L6-v2` and stores them in ChromaDB on disk. Also writes a preview of the first 5 embeddings.

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
- [ ] `data/chroma/` directory is created with ChromaDB files.
- [ ] `data/embeddings_preview.txt` exists and shows 5 vectors with 10 dimensions each.
- [ ] Run a second time and confirm it says "Collection already exists" or skips re-ingestion (persistence check).
- [ ] Restart Python, import ChromaDB, and confirm the collection still has vectors (persistence across restarts).

---

## Phase 4: Guardrails

### What this does
Adds checks to refuse off-topic questions, prevent advice outside the source, and say "I don't know" when context is insufficient.

### Files to create

| File | Purpose |
|------|---------|
| `src/query/guardrails.py` | Off-topic detection and context sufficiency checks |

### Guardrail logic
1. **Off-topic check**: Compare the question embedding against all chunk embeddings. If the best similarity score is below a threshold (e.g., 0.3), refuse: "I can only answer questions about the document."
2. **Context sufficiency**: If retrieved chunks don't contain enough relevant information (low similarity scores), respond: "I don't know. The document doesn't contain enough information to answer that."
3. **No advice outside source**: The system prompt instructs the LLM to only use the provided context and never give advice beyond it.

### How to verify
- [ ] Ask an off-topic question (e.g., "What's the weather?") and confirm the bot refuses.
- [ ] Ask an on-topic question and confirm it proceeds to retrieval.
- [ ] Ask a question whose answer is NOT in the document and confirm the bot says "I don't know."
- [ ] Ask a question that IS in the document and confirm the bot answers normally.

---

## Phase 5: Retrieval + LLM Answer

### What this does
Embeds the user's question, retrieves top-k chunks from ChromaDB, sends them to Groq's LLM with a system prompt, and returns the answer. Includes a CLI for testing.

### Files to create

| File | Purpose |
|------|---------|
| `src/query/retriever.py` | Embeds query and searches ChromaDB |
| `src/query/llm.py` | Groq API client — sends prompt and returns answer |
| `src/chat.py` | Main RAG pipeline — combines retrieval + guardrails + LLM |
| `src/cli.py` | CLI interface for testing |

### System prompt template
```
You are a helpful assistant that answers questions based ONLY on the provided context.
Rules:
1. Only use information from the context below to answer.
2. If the context doesn't contain the answer, say "I don't know."
3. Never give advice or information beyond what's in the context.
4. Be concise and accurate.

Context:
{retrieved_chunks}

Question: {user_question}
```

### CLI behavior
- Prompt the user to type a question.
- Show which chunks were retrieved (chunk index + similarity score).
- Display the LLM's answer.
- Loop until the user types "quit".

### How to verify
- [ ] `python -m src.cli` starts and prompts for a question.
- [ ] Ask an on-topic question and confirm the answer is grounded in the document.
- [ ] Confirm the CLI shows retrieved chunk indices and similarity scores.
- [ ] Ask an off-topic question and confirm the guardrail refusal appears.
- [ ] Type "quit" and confirm the CLI exits cleanly.

---

## Phase 6: UI (Streamlit)

### What this does
Builds a web chat interface with message history, a sources expander under each answer, and a clear-chat button.

### Files to create

| File | Purpose |
|------|---------|
| `src/app.py` | Streamlit chat UI |

### UI requirements
- **Message history**: Show all user questions and bot answers in a chat layout.
- **Sources expander**: Under each answer, a collapsible "Sources" section showing the retrieved chunks.
- **Clear-chat button**: A button to reset the conversation.
- **Conversation memory**: Keep last 10 messages and use them for question rewriting.

### How to verify
- [ ] `streamlit run src/app.py` starts the app.
- [ ] Type a question and confirm the answer appears in the chat.
- [ ] Click "Sources" and confirm retrieved chunks are shown.
- [ ] Click "Clear chat" and confirm the conversation resets.
- [ ] Ask a follow-up question (e.g., "What about its fees?") and confirm pronoun resolution works.
- [ ] Confirm the UI is accessible at `http://localhost:8501`.

---

## Summary: Phase Completion Checklist

| Phase | Key Verification |
|-------|-----------------|
| 1. Setup | `pip install` works, `.env` is gitignored |
| 2. Chunking | `chunks.txt` exists with numbered chunks + metadata |
| 3. Embedding | ChromaDB persists, embeddings preview file exists |
| 4. Guardrails | Off-topic refused, insufficient context says "I don't know" |
| 5. Retrieval + LLM | CLI answers questions, shows retrieved chunks |
| 6. UI | Streamlit app runs, shows history + sources + clear button |

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
| 1.0 | 2026-09-30 | AI Coding Agent | Initial implementation plan based on architecture.md |
