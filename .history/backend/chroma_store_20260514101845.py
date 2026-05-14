from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config.settings import settings


class VectorStore:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )

        self.db = Chroma(
            persist_directory=settings.CHROMA_PATH,
            embedding_function=self.embeddings
        )

    def add_documents(self, docs):
        self.db.add_documents(docs)

    def similarity_search(self, query: str, k: int = 4):
        return self.db.similarity_search(query, k=k)


vectorstore = VectorStore()