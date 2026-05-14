from retrieval.rag_chain import rag_chain


class SummaryAgent:
    def run(self, query: str):
        return rag_chain.generate(query)


summary_agent = SummaryAgent()