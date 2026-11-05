from pathlib import Path
from typing import List

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


def load_documents(data_dir: str = "data/raw") -> List[dict]:
    """Load all documents from the raw data directory.

    Returns a list of dicts with keys: 'content', 'source', 'file_type'
    """
    documents = []
    raw_path = Path(data_dir)

    if not raw_path.exists():
        return documents

    for file_path in raw_path.rglob("*"):
        if not file_path.is_file():
            continue

        content = _extract_text(file_path)
        if content and content.strip():
            documents.append(
                {
                    "content": content,
                    "source": str(file_path),
                    "file_type": file_path.suffix.lower(),
                }
            )

    return documents


def _extract_text(file_path: Path) -> str:
    """Extract text from a file based on its extension."""
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(file_path)
    elif suffix in (".txt", ".md"):
        return file_path.read_text(encoding="utf-8")
    else:
        return ""


def _extract_pdf(file_path: Path) -> str:
    """Extract text from a PDF file."""
    if PdfReader is None:
        return ""
    reader = PdfReader(str(file_path))
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text)
    return "\n".join(texts)
