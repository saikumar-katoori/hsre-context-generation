from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.health import router as health_router
from api.routes.inference import router as inference_router
from api.routes.upload import router as upload_router
from api.routes.recording import router as recording_router
from config.settings import settings

app = FastAPI(title="HSRE Context Generation API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(inference_router)
app.include_router(upload_router)
app.include_router(recording_router)


@app.get("/")
def root() -> dict:
    return {"status": "ok", "service": "hsre-api"}
