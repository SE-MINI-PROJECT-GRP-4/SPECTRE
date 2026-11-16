from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.conversations import router as conversations_router


app = FastAPI(
    title="SPECTRE API",
    description="AI-Based Legal Assistant and Case Guidance System",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(conversations_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }