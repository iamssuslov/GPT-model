from sqlalchemy.orm import Session

from app.memory.models import ChatMessage, ChatSession


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, title: str = "New chat") -> ChatSession:
        session = ChatSession(title=title)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: int) -> ChatSession | None:
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def list_sessions(self) -> list[ChatSession]:
        return (
            self.db.query(ChatSession)
            .order_by(ChatSession.created_at.desc())
            .all()
        )

    def update_session_summary(self, session_id: int, summary: str | None) -> ChatSession:
        session = self.get_session(session_id)
        if session is None:
            raise ValueError(f"Session with id={session_id} not found")

        session.summary = summary
        self.db.commit()
        self.db.refresh(session)
        return session

    def add_message(self, session_id: int, role: str, content: str) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(self, session_id: int, limit: int | None = None) -> list[ChatMessage]:
        query = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        )

        messages = query.all()
        if limit is not None and len(messages) > limit:
            return messages[-limit:]

        return messages