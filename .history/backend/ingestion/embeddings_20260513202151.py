from langchain_community.embeddings import OllamaEmbeddings
from config.settings import settings


def get_embeddings():
    return OllamaEmbeddings(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.EMBEDDING_MODEL
    )