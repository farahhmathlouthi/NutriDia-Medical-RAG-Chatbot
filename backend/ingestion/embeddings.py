from langchain_huggingface import HuggingFaceEmbeddings
from config.settings import settings


def get_embeddings():
    """Returns a HuggingFace embedding model (runs fully locally)."""
    return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
