"""Central configuration for the RAG Chatbot."""

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ChromaDB settings
CHROMA_DIR = "data/chroma"
COLLECTION_NAME = "documents"

# Chunking settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Retrieval settings
TOP_K = 3

# Similarity threshold for guardrails
SIMILARITY_THRESHOLD = 0.3

# Data paths
RAW_DIR = "data/raw"
CHUNKS_DIR = "data/chunks"
CHUNKS_FILE = "data/chunks/chunks.txt"
EMBEDDINGS_PREVIEW_FILE = "data/embeddings_preview.txt"

# Conversation memory
MEMORY_LIMIT = 10
