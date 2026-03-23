from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.rag.service import RagService
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])


class CreateSessionRequest(BaseModel):
    title: str = "New chat"


class SessionResponse(BaseModel):
    session_id: int
    title: str
    summary: str | None = None


class ChatRequest(BaseModel):
    message: str
    session_id: int | None = None
    use_rag: bool = False


class ChatResponse(BaseModel):
    session_id: int
    answer: str


class SessionListItem(BaseModel):
    session_id: int
    title: str
    summary: str | None = None


class MessageItem(BaseModel):
    id: int
    role: str
    content: str
    created_at: str


class IndexResponse(BaseModel):
    files_indexed: int
    chunks_indexed: int


class SearchRequest(BaseModel):
    query: str
    top_k: int | None = None


class SearchResultItem(BaseModel):
    content: str
    metadata: dict
    distance: float | None = None


@router.post("/sessions", response_model=SessionResponse)
def create_session(request: CreateSessionRequest, db: Session = Depends(get_db)):
    try:
        service = ChatService(db)
        session = service.create_session(title=request.title)
        return SessionResponse(
            session_id=session.id,
            title=session.title,
            summary=session.summary,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/sessions", response_model=list[SessionListItem])
def list_sessions(db: Session = Depends(get_db)):
    try:
        service = ChatService(db)
        sessions = service.list_sessions()
        return [
            SessionListItem(
                session_id=session.id,
                title=session.title,
                summary=session.summary,
            )
            for session in sessions
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)):
    try:
        service = ChatService(db)
        session = service.memory.get_session(session_id)
        return SessionResponse(
            session_id=session.id,
            title=session.title,
            summary=session.summary,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/messages", response_model=list[MessageItem])
def get_session_messages(session_id: int, db: Session = Depends(get_db)):
    try:
        service = ChatService(db)
        messages = service.get_session_messages(session_id)
        return [MessageItem(**message) for message in messages]
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        service = ChatService(db)
        result = service.ask(
            user_message=request.message,
            session_id=request.session_id,
            use_rag=request.use_rag,
        )
        return ChatResponse(
            session_id=result["session_id"],
            answer=result["answer"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/rag/index", response_model=IndexResponse)
def index_documents():
    try:
        rag_service = RagService()
        result = rag_service.index_documents()
        return IndexResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/rag/search", response_model=list[SearchResultItem])
def search_documents(request: SearchRequest):
    try:
        rag_service = RagService()
        results = rag_service.search(query=request.query, top_k=request.top_k)
        return [SearchResultItem(**item) for item in results]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc