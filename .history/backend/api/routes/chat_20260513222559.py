from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/")
def chat(request: ChatRequest):
    return {
        "answer": f"You asked: {request.query}"
    }