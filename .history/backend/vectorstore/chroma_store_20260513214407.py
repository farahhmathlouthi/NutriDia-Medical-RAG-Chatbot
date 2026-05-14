from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from config.settings import settings


class VectorStore:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.EMBEDDING_MODEL
        )

        self.db = Chroma(
            persist_directory=settings.CHROMA_PATH,
            embedding_function=self.embeddings
        )

    def add_documents(self, docs):
        self.db.add_documents(docs)
        self.db.persist()

    def similarity_search(self, query: str, k: int = 4):
        return self.db.similarity_search(query, k=k)


vectorstore = VectorStore()