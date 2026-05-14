from vectorstore.chroma_store import vectorstore


class Retriever:
    def __init__(self):
        self.vs = vectorstore

    #finds the most relevant chunks from your vector database based on the query, which will then be used as context for the LLM to generate a response.
    def get_relevant_docs(self, query: str, k: int = 4):
        return self.vs.similarity_search(query, k=k)


retriever = Retriever()