from typing import List

from config.settings import settings
from .embeddings import EmbeddingModel
from .generator import Generator
from .loader import load_documents
from .retriever import Retriever
from .splitter import split_documents
from .vectorstore import VectorStore


class RAGPipeline:
    def __init__(self):
        self.embedding_model = EmbeddingModel(model_name=settings.EMBEDDING_MODEL)
        self.vector_store = VectorStore(
            collection_name=settings.COLLECTION_NAME,
            persist_path=settings.VECTOR_DB_PATH,
        )
        self.retriever = Retriever(
            embedding_model=self.embedding_model,
            vector_store=self.vector_store,
            top_k=settings.TOP_K,
        )
        self.generator = Generator(groq_api_key=settings.GROQ_API_KEY)

    def ingest(self, data_dir: str = "data/raw") -> int:
        """Load, split, embed, and store documents from the data directory."""
        documents = load_documents(data_dir)
        if not documents:
            print("No documents found to ingest.")
            return 0

        self.vector_store.reset()

        chunked_docs = split_documents(
            documents,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

        texts = [doc["content"] for doc in chunked_docs]
        embeddings = self.embedding_model.embed_documents(texts)

        self.vector_store.add_documents(chunked_docs, embeddings)
        print(f"Ingested {len(documents)} documents into {len(chunked_docs)} chunks.")
        return len(chunked_docs)

    def query(self, question: str) -> dict:
        """Run a RAG query: retrieve context and generate an answer."""
        chunks = self.retriever.retrieve(question)
        answer = self.generator.generate(question, chunks)
        return {
            "answer": answer,
            "sources": [chunk.get("metadata", {}).get("source", "unknown") for chunk in chunks],
        }
