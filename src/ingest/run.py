"""Orchestrate the full ingestion pipeline: load → chunk → embed → store.

Usage:
    python -m src.ingest.run
"""

from pathlib import Path
import chromadb
from src.config import (
    CHUNKS_FILE,
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDINGS_PREVIEW_FILE,
)
from src.ingest.loader import load_document
from src.ingest.chunker import chunk_text, format_chunks
from src.ingest.embedder import Embedder


def main():
    print("=" * 60)
    print("Phase 3: Embedding & Vector Store")
    print("=" * 60)

    # Step 1: Load
    print("\n[1/5] Loading source document...")
    raw_text = load_document("source.txt")
    print(f"  Loaded {len(raw_text)} characters from data/raw/source.txt")

    # Step 2: Chunk
    print("\n[2/5] Splitting into chunks...")
    chunks = chunk_text(raw_text, source="source.txt")
    print(f"  Created {len(chunks)} chunks")

    # Step 3: Save chunks to file
    print("\n[3/5] Saving chunks to file...")
    output_path = Path(CHUNKS_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(format_chunks(chunks), encoding="utf-8")
    print(f"  Saved to {CHUNKS_FILE}")

    # Step 4: Embed
    print("\n[4/5] Embedding chunks...")
    embedder = Embedder()
    texts = [chunk.text for chunk in chunks]
    embeddings = embedder.embed(texts)
    print(f"  Embedded {len(embeddings)} chunks (dimension: {len(embeddings[0])})")

    # Step 5: Store in ChromaDB
    print("\n[5/5] Storing in ChromaDB...")
    chroma_path = Path(CHROMA_DIR)
    chroma_path.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(chroma_path))

    # Check if collection already exists (persistence check)
    existing_collections = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing_collections:
        print(f"  Collection '{COLLECTION_NAME}' already exists. Deleting and recreating...")
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Add chunks to ChromaDB
    ids = [str(chunk.chunk_index) for chunk in chunks]
    metadatas = [
        {
            "source": chunk.source,
            "char_count": chunk.char_count,
            "chunk_index": chunk.chunk_index,
        }
        for chunk in chunks
    ]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    print(f"  Stored {collection.count()} vectors in ChromaDB at {CHROMA_DIR}/")

    # Write embeddings preview
    print("\n  Writing embeddings preview...")
    preview_lines = []
    for i in range(min(5, len(embeddings))):
        preview_lines.append(f"=== Embedding {i + 1} (Chunk {chunks[i].chunk_index + 1}) ===")
        preview_lines.append(f"First 10 dimensions: {embeddings[i][:10]}")
        preview_lines.append("")

    preview_path = Path(EMBEDDINGS_PREVIEW_FILE)
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    preview_path.write_text("\n".join(preview_lines), encoding="utf-8")
    print(f"  Saved to {EMBEDDINGS_PREVIEW_FILE}")

    # Summary
    print("\n" + "=" * 60)
    print(f"DONE: {len(embeddings)} vectors stored in ChromaDB")
    print(f"Vector dimension: {len(embeddings[0])}")
    print(f"ChromaDB path: {CHROMA_DIR}/")
    print(f"Preview: {EMBEDDINGS_PREVIEW_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
