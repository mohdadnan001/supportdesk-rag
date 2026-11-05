import os
import threading
from typing import List

import chromadb

_CLIENT_LOCK = threading.Lock()


class VectorStore:
    def __init__(self, collection_name: str = "rag_documents", persist_path: str = "./data/processed/chroma_db"):
        self.collection_name = collection_name
        self.persist_path = persist_path
        os.makedirs(persist_path, exist_ok=True)

        with _CLIENT_LOCK:
            self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def reset(self) -> None:
        """Drop and recreate the collection so re-ingesting reflects data/raw exactly."""
        try:
            self.client.delete_collection(self.collection_name)
        except ValueError:
            pass
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def add_documents(self, documents: List[dict], embeddings: List[List[float]]) -> None:
        """Add documents and their embeddings to the vector store."""
        ids = [f"{doc['source']}_{doc['chunk_index']}" for doc in documents]
        metadatas = [
            {"source": doc["source"], "file_type": doc["file_type"], "chunk_index": doc["chunk_index"]}
            for doc in documents
        ]
        contents = [doc["content"] for doc in documents]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas,
        )

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[dict]:
        """Search for similar documents given a query embedding."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        documents = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                documents.append(
                    {
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else None,
                    }
                )
        return documents

    def count(self) -> int:
        """Return the number of documents in the collection."""
        return self.collection.count()
