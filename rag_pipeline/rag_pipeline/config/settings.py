import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    TOP_K: int = int(os.getenv("TOP_K", "3"))
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "rag_documents")
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./data/processed/chroma_db")
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")


settings = Settings()
