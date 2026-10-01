"""Embed text chunks using sentence-transformers."""

from typing import List
from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL


class Embedder:
    """Loads the embedding model and converts text to vectors."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """Initialize the embedding model.

        Args:
            model_name: The sentence-transformers model to use.
        """
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Convert a list of texts into embedding vectors.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors (each is a list of floats).
        """
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Convert a single query text into an embedding vector.

        Args:
            text: The query text to embed.

        Returns:
            A single embedding vector.
        """
        return self.embed([text])[0]
