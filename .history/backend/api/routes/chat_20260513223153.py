from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/")
def chat(request: ChatRequest):
    print("REQUEST TYPE:", type(request))
    print("REQUEST CONTENT:", request)
    return {
        "answer": f"You asked: {request.query}"
    }