from fastapi import APIRouter

router = APIRouter(prefix="/c", tags=["Health"])


@router.get("/")
def health_check():
    return {
        "status": "healthy"
    }