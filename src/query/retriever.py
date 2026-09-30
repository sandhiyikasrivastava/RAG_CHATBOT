"""Retrieve relevant chunks from ChromaDB."""

from typing import List, Dict, Any
import chromadb
from config import CHROMA_DIR, COLLECTION_NAME, TOP_K
from ingest.embedder import Embedder


class Retriever:
    """Embeds queries and retrieves top-k chunks from ChromaDB."""

    def __init__(self, embedder: Embedder = None):
        """Initialize the retriever.

        Args:
            embedder: The embedder instance. Creates one if not provided.
        """
        self.embedder = embedder or Embedder()
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.collection = self.client.get_collection(COLLECTION_NAME)

    def retrieve(self, question: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
        """Retrieve the top-k most relevant chunks for a question.

        Args:
            question: The user's question.
            top_k: Number of chunks to retrieve.

        Returns:
            List of dicts with chunk data and similarity scores.
        """
        # Embed the question
        query_embedding = self.embedder.embed_query(question)

        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        chunks = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0.0
                # Convert distance to similarity (cosine distance: 0=identical, 2=opposite)
                similarity = 1.0 - distance

                chunks.append({
                    "text": doc,
                    "metadata": metadata,
                    "similarity": similarity,
                    "chunk_index": metadata.get("chunk_index", i),
                })

        return chunks

    def get_all_embeddings(self) -> List[List[float]]:
        """Get all chunk embeddings from ChromaDB (for guardrails).

        Returns:
            List of all chunk embedding vectors.
        """
        results = self.collection.get(include=["embeddings"])
        embeddings = results["embeddings"]
        if embeddings is None or len(embeddings) == 0:
            return []
        return embeddings.tolist() if hasattr(embeddings, "tolist") else list(embeddings)
