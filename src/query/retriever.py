"""Retrieve relevant chunks from ChromaDB."""

from typing import List, Dict, Any
import chromadb
from src.config import CHROMA_DIR, COLLECTION_NAME, TOP_K
from ingest.embedder import Embedder


# Known HDFC fund names for matching
HDFC_FUND_NAMES = [
    "HDFC Large Cap Fund",
    "HDFC Flexi Cap Fund",
    "HDFC ELSS Tax Saver Fund",
    "HDFC Small Cap Fund",
    "HDFC Balanced Advantage Fund",
    "HDFC Equity Fund",
    "HDFC Index Fund",
    "HDFC Hybrid Fund",
    "HDFC Top 100 Fund",
    "HDFC Banking Fund",
    "HDFC Liquid Fund",
    "HDFC Short Term Fund",
    "HDFC Medium Term Fund",
    "HDFC Long Duration Fund",
    "HDFC Dynamic Fund",
    "HDFC Multi Cap Fund",
    "HDFC Value Fund",
    "HDFC Contra Fund",
    "HDFC Infrastructure Fund",
    "HDFC Pharma Fund",
    "HDFC Technology Fund",
    "HDFC Focused Fund",
    "HDFC Arbitrage Fund",
    "HDFC Overnight Fund",
    "HDFC Money Market Fund",
    "HDFC Corporate Bond Fund",
    "HDFC Gilt Fund",
    "HDFC Floating Rate Fund",
    "HDFC Nifty 50 Index Fund",
    "HDFC Nifty Next 50 Index Fund",
    "HDFC Sensex Index Fund",
    "HDFC Gold Fund",
    "HDFC Silver Fund",
    "HDFC International Fund",
    "HDFC US Equity Fund",
    "HDFC China Fund",
    "HDFC Japan Fund",
    "HDFC European Fund",
    "HDFC Emerging Markets Fund",
    "HDFC Global Fund",
    "HDFC Retirement Fund",
    "HDFC Children's Gift Fund",
    "HDFC Savings Fund",
    "HDFC Ultra Short Term Fund",
    "HDFC Low Duration Fund",
    "HDFC Short Duration Fund",
    "HDFC Medium Duration Fund",
    "HDFC Long Term Fund",
    "HDFC Income Fund",
    "HDFC Dynamic Debt Fund",
    "HDFC Credit Risk Fund",
    "HDFC Banking and PSU Fund",
    "HDFC Debt Fund",
    "HDFC Fixed Maturity Plan",
    "HDFC FMP",
    "HDFC Hybrid Equity Fund",
    "HDFC Aggressive Hybrid Fund",
    "HDFC Conservative Hybrid Fund",
    "HDFC Equity Savings Fund",
    "HDFC Arbitrage Fund",
    "HDFC Multi-Asset Fund",
    "HDFC Diversified Equity Fund",
    "HDFC Large and Mid Cap Fund",
    "HDFC Mid Cap Fund",
    "HDFC Small and Mid Cap Fund",
    "HDFC Micro Cap Fund",
    "HDFC Small Cap Direct Growth",
    "HDFC Large Cap Direct Growth",
    "HDFC Flexi Cap Direct Growth",
    "HDFC ELSS Tax Saver Direct Growth",
    "HDFC Balanced Advantage Direct Growth",
    "HDFC Equity Direct Growth",
    "HDFC Index Direct Growth",
    "HDFC Hybrid Direct Growth",
    "HDFC Top 100 Direct Growth",
    "HDFC Banking Direct Growth",
    "HDFC Liquid Direct Growth",
    "HDFC Short Term Direct Growth",
    "HDFC Medium Term Direct Growth",
    "HDFC Long Duration Direct Growth",
    "HDFC Dynamic Direct Growth",
    "HDFC Multi Cap Direct Growth",
    "HDFC Value Direct Growth",
    "HDFC Contra Direct Growth",
    "HDFC Infrastructure Direct Growth",
    "HDFC Pharma Direct Growth",
    "HDFC Technology Direct Growth",
    "HDFC Focused Direct Growth",
    "HDFC Arbitrage Direct Growth",
    "HDFC Overnight Direct Growth",
    "HDFC Money Market Direct Growth",
    "HDFC Corporate Bond Direct Growth",
    "HDFC Gilt Direct Growth",
    "HDFC Floating Rate Direct Growth",
    "HDFC Nifty 50 Index Direct Growth",
    "HDFC Nifty Next 50 Index Direct Growth",
    "HDFC Sensex Index Direct Growth",
    "HDFC Gold Direct Growth",
    "HDFC Silver Direct Growth",
    "HDFC International Direct Growth",
    "HDFC US Equity Direct Growth",
    "HDFC China Direct Growth",
    "HDFC Japan Direct Growth",
    "HDFC European Direct Growth",
    "HDFC Emerging Markets Direct Growth",
    "HDFC Global Direct Growth",
    "HDFC Retirement Direct Growth",
    "HDFC Children's Gift Direct Growth",
    "HDFC Savings Direct Growth",
    "HDFC Ultra Short Term Direct Growth",
    "HDFC Low Duration Direct Growth",
    "HDFC Short Duration Direct Growth",
    "HDFC Medium Duration Direct Growth",
    "HDFC Long Term Direct Growth",
    "HDFC Income Direct Growth",
    "HDFC Dynamic Debt Direct Growth",
    "HDFC Credit Risk Direct Growth",
    "HDFC Banking and PSU Direct Growth",
    "HDFC Debt Direct Growth",
    "HDFC Fixed Maturity Plan Direct Growth",
    "HDFC FMP Direct Growth",
    "HDFC Hybrid Equity Direct Growth",
    "HDFC Aggressive Hybrid Direct Growth",
    "HDFC Conservative Hybrid Direct Growth",
    "HDFC Equity Savings Direct Growth",
    "HDFC Arbitrage Direct Growth",
    "HDFC Multi-Asset Direct Growth",
    "HDFC Diversified Equity Direct Growth",
    "HDFC Large and Mid Cap Direct Growth",
    "HDFC Mid Cap Direct Growth",
    "HDFC Small and Mid Cap Direct Growth",
    "HDFC Micro Cap Direct Growth",
]


def extract_fund_names(question: str) -> List[str]:
    """Extract HDFC fund names from a question.

    Args:
        question: The user's question.

    Returns:
        List of fund names found in the question.
    """
    question_lower = question.lower()
    found = []
    for name in HDFC_FUND_NAMES:
        if name.lower() in question_lower:
            found.append(name)
    return found


def boost_chunks_with_fund_names(
    chunks: List[Dict[str, Any]],
    fund_names: List[str],
    boost_factor: float = 0.15,
) -> List[Dict[str, Any]]:
    """Boost similarity scores for chunks that mention specific fund names.

    Args:
        chunks: List of chunk dicts with 'text' and 'similarity'.
        fund_names: List of fund names to match.
        boost_factor: Amount to add to similarity for matching chunks.

    Returns:
        List of chunks with boosted similarity scores, sorted by similarity.
    """
    if not fund_names:
        return chunks

    for chunk in chunks:
        text_lower = chunk["text"].lower()
        for name in fund_names:
            if name.lower() in text_lower:
                chunk["similarity"] = min(1.0, chunk["similarity"] + boost_factor)
                break

    # Re-sort by boosted similarity
    chunks.sort(key=lambda c: c["similarity"], reverse=True)
    return chunks


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

        # Search ChromaDB (get more results to allow for boosting)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k * 3, 30),
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

        # Boost chunks that mention specific fund names from the question
        fund_names = extract_fund_names(question)
        if fund_names:
            chunks = boost_chunks_with_fund_names(chunks, fund_names)

        # Return top-k after boosting
        return chunks[:top_k]

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
