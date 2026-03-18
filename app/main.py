from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.core.config import settings
from app.core.database import Base, engine
from app.memory import models  # noqa: F401


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}