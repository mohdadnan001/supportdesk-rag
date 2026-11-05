from typing import List


def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks.

    Args:
        text: The text to split.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of overlapping characters between chunks.

    Returns:
        List of text chunks.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be less than chunk_size")

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        if end >= text_length:
            break

        start = end - chunk_overlap

    return chunks


def split_documents(documents: List[dict], chunk_size: int = 500, chunk_overlap: int = 50) -> List[dict]:
    """Split all documents into chunks.

    Each chunk retains the source metadata of its parent document.
    """
    chunked_docs = []
    for doc in documents:
        chunks = split_text(doc["content"], chunk_size, chunk_overlap)
        for i, chunk in enumerate(chunks):
            chunked_docs.append(
                {
                    "content": chunk,
                    "source": doc["source"],
                    "file_type": doc["file_type"],
                    "chunk_index": i,
                }
            )
    return chunked_docs
