from typing import TypedDict, Optional, List


class AgentState(TypedDict):
    """Shared state passed between all nodes in the LangGraph."""
    query: str                        # Original user question
    route: Optional[str]              # "rag" | "doctor_search"
    answer: Optional[str]             # Final answer text
    doctors: Optional[List[dict]]     # List of doctors found (doctor_search only)
