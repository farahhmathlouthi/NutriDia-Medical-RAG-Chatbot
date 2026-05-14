from retrieval.rag_chain import rag_chain


class NutritionAgent:
    def run(self, query: str):
        return rag_chain.generate(query)


nutrition_agent = NutritionAgent()