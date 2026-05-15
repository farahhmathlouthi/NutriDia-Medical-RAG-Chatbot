from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from config.settings import settings
from retrieval.retriever import retriever
from agents.state import AgentState
from prompts.medical_prompt import MEDICAL_PROMPT

SYSTEM_PROMPT = """You are NutriDia, a specialized medical assistant focused on diabetes and nutrition.

You answer ONLY based on the context provided from trusted medical documents.
Be clear, accurate, and compassionate. Always remind users to consult a doctor for personal medical decisions.

If the context does not contain enough information, say so honestly."""

RAG_PROMPT = """Use the following medical document excerpts to answer the question.

--- CONTEXT FROM MEDICAL DOCUMENTS ---
{context}
--- END OF CONTEXT ---

Question: {question}

Answer clearly and in a structured way based on the context above:"""


class RAGAgent:
    def __init__(self):
        self.llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.2
        )

    def run(self, state: AgentState) -> AgentState:
        query = state["query"]

        # Retrieve relevant chunks from ChromaDB
        docs = retriever.get_relevant_docs(query)

        if not docs:
            answer = (
                "I could not find relevant information in the medical documents. "
                "Please upload relevant PDFs first, or consult a healthcare professional."
            )
            return {**state, "answer": answer}

        context = "\n\n".join([
            f"[Source: {d.metadata.get('source', 'document')}, Page {d.metadata.get('page', '?')}]\n{d.page_content}"
            for d in docs
        ])

        prompt = RAG_PROMPT.format(context=context, question=query)

        response = self.llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])

        print(f"[RAG Agent] Answered using {len(docs)} chunks from ChromaDB")
        return {**state, "answer": response.content}


rag_agent = RAGAgent()
