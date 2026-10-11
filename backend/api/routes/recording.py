from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["recording"])


@router.post("/recording")
def receive_recording() -> dict:
    return {"status": "success", "message": "Recording endpoint ready for client integration."}
