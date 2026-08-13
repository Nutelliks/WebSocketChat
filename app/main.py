from fastapi import FastAPI


app = FastAPI(
    title="WebSocket Chat",
    version="1.0.0"
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello, WebSocketChat!"}