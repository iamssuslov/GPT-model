from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        service = ChatService()
        answer = service.ask(request.message)
        return ChatResponse(answer=answer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc