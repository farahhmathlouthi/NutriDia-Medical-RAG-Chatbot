from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from config.settings import settings
from retrieval.retriever import retriever
from prompts.medical_prompt import MEDICAL_PROMPT


class RAGChain:
    def __init__(self):
        self.llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.2
        )

    def generate(self, query: str) -> str:
        docs = retriever.get_relevant_docs(query)

        if not docs:
            return (
                "I could not find relevant information in the provided documents. "
                "Please consult a medical professional for personalized advice."
            )

        context = "\n\n".join([d.page_content for d in docs])

        prompt = MEDICAL_PROMPT.format(context=context, question=query)

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content


rag_chain = RAGChain()
