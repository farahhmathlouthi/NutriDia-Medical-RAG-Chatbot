from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/")
def chat():
    return {
        "status": "healthy"
    }