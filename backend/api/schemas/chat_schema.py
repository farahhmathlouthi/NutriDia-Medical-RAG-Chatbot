from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str

    class Config:
        json_schema_extra = {
            "example": {"query": "What foods should a diabetic patient avoid?"}
        }
