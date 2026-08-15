from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title="WebSocket Chat", version="0.1.0")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello, WebSocketChat!"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "env": settings.ENV}
