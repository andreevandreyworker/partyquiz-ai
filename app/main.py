from fastapi import FastAPI

from app.exceptions import register_exception_handlers
from app.router import router

app = FastAPI(title="ai-service")
register_exception_handlers(app)
app.include_router(router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
