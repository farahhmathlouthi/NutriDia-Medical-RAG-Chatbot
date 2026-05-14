from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/")
def health_check():
    return {
        "status": "healthy"
    }