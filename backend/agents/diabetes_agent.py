from retrieval.rag_chain import rag_chain


class DiabetesAgent:
    def run(self, query: str):
        return rag_chain.generate(query)


diabetes_agent = DiabetesAgent()