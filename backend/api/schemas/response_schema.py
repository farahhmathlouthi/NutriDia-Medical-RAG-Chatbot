from pydantic import BaseModel


class ChatResponse(BaseModel):
    query: str
    answer: str
