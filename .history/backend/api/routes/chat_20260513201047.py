from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str

@router.get("/")
def chat(request: ChatRequest):
    return {
        "question": 
    }