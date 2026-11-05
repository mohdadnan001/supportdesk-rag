from typing import List

from .embeddings import EmbeddingModel
from .vectorstore import VectorStore


class Retriever:
    def __init__(self, embedding_model: EmbeddingModel, vector_store: VectorStore, top_k: int = 3):
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(self, query: str) -> List[dict]:
        """Retrieve the most relevant document chunks for a query."""
        query_embedding = self.embedding_model.embed_query(query)
        results = self.vector_store.search(query_embedding, top_k=self.top_k)
        return results
