from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/")
def chat(request: dict):
    print(request)
    return {"received": request}