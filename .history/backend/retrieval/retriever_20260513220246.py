from vectorstore.chroma_store import vectorstore


class Retriever:
    def __init__(self):
        self.vs = vectorstore

    
    def get_relevant_docs(self, query: str, k: int = 4):
        return self.vs.similarity_search(query, k=k)


retriever = Retriever()