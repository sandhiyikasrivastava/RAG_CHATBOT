"""Split raw text into overlapping chunks with metadata."""

from dataclasses import dataclass, asdict
from typing import List
from src.config import CHUNK_SIZE, CHUNK_OVERLAP


@dataclass
class Chunk:
    """A single chunk of text with metadata."""
    chunk_index: int
    source: str
    char_count: int
    text: str


def chunk_text(text: str, source: str = "source.txt") -> List[Chunk]:
    """Split text into overlapping chunks.

    Args:
        text: The raw text to split.
        source: The source filename for metadata.

    Returns:
        A list of Chunk objects.
    """
    chunks = []
    start = 0
    index = 0
    text_length = len(text)

    while start < text_length:
        end = start + CHUNK_SIZE
        chunk_text_slice = text[start:end]

        chunks.append(Chunk(
            chunk_index=index,
            source=source,
            char_count=len(chunk_text_slice),
            text=chunk_text_slice,
        ))

        index += 1
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def format_chunks(chunks: List[Chunk]) -> str:
    """Format chunks into a human-readable string for inspection.

    Args:
        chunks: List of Chunk objects.

    Returns:
        Formatted string with all chunks.
    """
    lines = []
    for chunk in chunks:
        lines.append(f"=== Chunk {chunk.chunk_index + 1} ===")
        lines.append(f"Source: {chunk.source}")
        lines.append(f"Characters: {chunk.char_count}")
        lines.append("---")
        lines.append(chunk.text)
        lines.append("")  # blank line between chunks
    return "\n".join(lines)
