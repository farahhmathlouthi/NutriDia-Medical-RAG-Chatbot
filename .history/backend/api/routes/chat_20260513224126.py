from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    query: str


@router.post("/")
def chat(request: ChatRequest):
    return {
        "answer": request.query
    }