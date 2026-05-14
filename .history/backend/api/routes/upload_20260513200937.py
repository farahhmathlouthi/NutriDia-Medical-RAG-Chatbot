from fastapi import APIRouter

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.get("/")
def upload():
    return {
        "status": "healthy"
    }