# Product Requirements Document (PRD) — Groww Mutual Fund FAQ Assistant

## 1. Goal

Build a **facts-only RAG chatbot** that answers questions about HDFC mutual fund schemes using only official public pages from Groww. Every answer includes one source link. No investment advice.

---

## 2. Target Users

| User | Description |
|------|-------------|
| **Retail investors** | People comparing HDFC mutual fund schemes who want quick factual answers (expense ratio, exit load, minimum SIP, etc.) |
| **Support/content teams** | Teams answering repetitive mutual fund questions who need a facts-only reference tool |

---

## 3. In-Scope Features

### 3.1 Data Ingestion Pipeline
- **Loading**: Scrape/collect 5 public Groww pages for HDFC mutual fund schemes
- **Chunking**: Split pages into overlapping chunks with metadata (source URL, character count, chunk index)
- **Embedding**: Convert each chunk into a 384-dimension vector using `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Storage**: Store embeddings in ChromaDB, persisted to disk

### 3.2 Retrieval + Answer Generation
- **Query Embedding**: Embed the user's question using the same embedding model
- **Similarity Search**: Retrieve top-k most relevant chunks from ChromaDB
- **LLM Answer**: Send system prompt + retrieved chunks + question to Groq LLM
- **Source Attribution**: Every answer includes one clear citation link

### 3.3 Guardrails
- **Facts-only**: Refuse opinionated/portfolio questions (e.g., "Should I buy/sell?") with a polite message
- **No advice**: Never give investment advice; link to official factsheet if asked
- **No PII**: Do not accept/store PAN, Aadhaar, account numbers, OTPs, emails, or phone numbers
- **No performance claims**: Don't compute/compare returns; link to official factsheet
- **Clarity**: Keep answers ≤3 sentences; add "Last updated from sources:"

### 3.4 Conversation Memory
- Keep the last 10 messages in memory
- Rewrite follow-up questions using conversation history before retrieval

### 3.5 User Interface
- **Welcome line** + 3 example questions
- **Disclaimer**: "Facts-only. No investment advice."
- **Sources expander**: Show retrieved chunks under each answer
- **Clear-chat button**: Reset the conversation

### 3.6 Deployment
- Push code to GitHub (excluding `.env` and ChromaDB data)
- Deploy to Render as a Web Service

---

## 4. Out-of-Scope Features

| Feature | Reason |
|---------|--------|
| Investment advice or recommendations | Facts-only by design |
| Performance/return calculations | No performance claims allowed |
| Multi-AMC support | Scope is HDFC only |
| User accounts / PII storage | No PII allowed |
| Screenshots of app back-end | Public sources only |
| Third-party blogs as sources | Official pages only |

---

## 5. Example User Questions

### Answerable (factual)
- "What is the expense ratio of HDFC Large Cap Fund?"
- "What is the ELSS lock-in period?"
- "What is the minimum SIP for HDFC Small Cap Fund?"
- "What is the exit load for HDFC Equity Fund?"
- "How do I download my capital gains statement?"

### Refused (opinionated/advice)
- "Should I buy HDFC Large Cap Fund?"
- "Which fund is best for me?"
- "Should I sell my ELSS now?"
- "What will be my returns in 5 years?"

---

## 6. Success Criteria

| # | Criterion | How to Verify |
|---|-----------|---------------|
| 1 | Ingestion produces chunks from 5 Groww pages saved to `data/chunks/chunks.txt` | Open file and inspect chunks |
| 2 | Embeddings stored in ChromaDB and persist across restarts | Run ingestion, restart, query |
| 3 | Factual questions retrieve relevant chunks | Check chunk content matches question |
| 4 | Every answer includes one source link | Verify citation in every response |
| 5 | Opinionated questions are refused with polite message | Ask "Should I buy..." |
| 6 | Answers are ≤3 sentences with "Last updated from sources:" | Check answer length and footer |
| 7 | No PII accepted/stored | Test with PAN/Aadhaar input |
| 8 | UI shows welcome line, 3 example questions, disclaimer | Interact with Streamlit UI |
| 9 | App deploys successfully on Render | Open Render URL and ask a question |
| 10 | `.env` and ChromaDB data never committed to Git | Check `.gitignore` and git log |

---

## 7. Constraints

| Constraint | Detail |
|------------|--------|
| **Public sources only** | Only official Groww/AMC/SEBI/AMFI pages |
| **No PII** | Do not accept/store PAN, Aadhaar, account numbers, OTPs, emails, phone numbers |
| **No performance claims** | Don't compute/compare returns; link to official factsheet |
| **Clarity & transparency** | Answers ≤3 sentences; add "Last updated from sources:" |
| **Free-tier tools only** | Groq API, local embedding model, ChromaDB, Streamlit, Render |
| **Runs locally** | Python 3.10+ |
| **Deployable to Render** | Build command rebuilds vector DB |
| **API key security** | Groq API key in `.env`, never committed |
| **Same embedding model** | `all-MiniLM-L6-v2` for both chunks and queries |
| **Readable chunks** | All chunks saved to `.txt` file |

---

## 8. Tech Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.10+ | Core language |
| Embedding Model | `sentence-transformers/all-MiniLM-L6-v2` | Local text embeddings (384-dim) |
| Vector DB | ChromaDB | Store and search embeddings |
| LLM | Groq API | Answer generation |
| UI | Streamlit | Web chat interface |
| Deployment | Render | Cloud hosting |
| Env Management | `python-dotenv` | Load API keys from `.env` |

---

## 9. Source Corpus

| # | Scheme | URL |
|---|--------|-----|
| 1 | HDFC Large Cap Fund | https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth |
| 2 | HDFC Equity Fund (Flexi Cap) | https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth |
| 3 | HDFC ELSS Tax Saver Fund | https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth |
| 4 | HDFC Small Cap Fund | https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth |
| 5 | HDFC Balanced Advantage Fund | https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth |

---

## 10. High-Level Flow

```
┌─────────────────────────────────────────────────────────┐
│                    INGESTION (One-time)                  │
│                                                         │
│  5 Groww Pages → Load → Chunk → Embed → ChromaDB       │
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
│  Answer + Source Link + "Last updated from sources:"    │
└─────────────────────────────────────────────────────────┘
```

---

## 11. Document History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 1.0 | 2026-09-30 | AI Coding Agent | Initial PRD based on updated ProblemStatement.txt — Groww HDFC Mutual Fund FAQ Assistant |
