from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])


class CreateSessionRequest(BaseModel):
    title: str = "New chat"


class SessionResponse(BaseModel):
    session_id: int
    title: str


class ChatRequest(BaseModel):
    message: str
    session_id: int | None = None


class ChatResponse(BaseModel):
    session_id: int
    answer: str


class SessionListItem(BaseModel):
    session_id: int
    title: str


@router.post("/sessions", response_model=SessionResponse)
def create_session(request: CreateSessionRequest, db: Session = Depends(get_db)):
    try:
        service = ChatService(db)
        session = service.create_session(title=request.title)
        return SessionResponse(session_id=session.id, title=session.title)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/sessions", response_model=list[SessionListItem])
def list_sessions(db: Session = Depends(get_db)):
    try:
        service = ChatService(db)
        sessions = service.list_sessions()
        return [
            SessionListItem(session_id=session.id, title=session.title)
            for session in sessions
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        service = ChatService(db)
        result = service.ask(
            user_message=request.message,
            session_id=request.session_id,
        )
        return ChatResponse(
            session_id=result["session_id"],
            answer=result["answer"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc