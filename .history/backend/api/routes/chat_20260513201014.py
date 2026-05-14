from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str

@router.get("/")
def chat():
    return {
        "status": "healthy"
    }