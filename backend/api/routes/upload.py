from fastapi import APIRouter, File, UploadFile

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)) -> dict:
    return {
        "status": "success",
        "filename": file.filename,
        "content_type": file.content_type,
        "size": 0,
    }
