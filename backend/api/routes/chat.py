from fastapi import APIRouter, HTTPException
from api.schemas.chat_schema import ChatRequest
from api.schemas.response_schema import ChatResponse
from agents.orchestrator import orchestrator

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        answer = orchestrator.run(request.query)
        return ChatResponse(answer=answer, query=request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
