from sentence_transformers import SentenceTransformer

try:
    from config import EMBEDDING_MODEL
except (ModuleNotFoundError, ImportError):
    from src.config import EMBEDDING_MODEL


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def embed(self, texts):
        return self.model.encode(
            texts,
            normalize_embeddings=True
        ).tolist()

    def embed_query(self, text):
        return self.embed([text])[0]
