"""Load the source document from data/raw/."""

from pathlib import Path
from src.config import RAW_DIR


def load_document(filename: str = "source.txt") -> str:
    """Read the source document and return its text.

    Args:
        filename: Name of the file in data/raw/.

    Returns:
        The full text of the document.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    filepath = Path(RAW_DIR) / filename
    if not filepath.exists():
        raise FileNotFoundError(
            f"Source file not found: {filepath}\n"
            f"Please place your document in {RAW_DIR}/"
        )
    return filepath.read_text(encoding="utf-8")
