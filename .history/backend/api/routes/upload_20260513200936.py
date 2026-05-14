from fastapi import APIRouter

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.get("/")
def health_check():
    return {
        "status": "healthy"
    }