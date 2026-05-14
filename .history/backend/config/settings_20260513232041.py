from pydantic_settings import BaseSettings
import os
import transformers


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Medical RAG Chatbot"
    ENV: str = "dev"

    # LLM (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:1b"

    # Embeddings
    #EMBEDDING_MODEL: str = "nomic-embed-text"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Vector DB
    CHROMA_PATH: str = "./vectorstore/chroma"

    # Chunking
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100

    # Retrieval
    TOP_K: int = 4

    # API
    API_PREFIX: str = "/api"

    class Config:
        env_file = ".env"


settings = Settings()