from app.memory.repository import ChatRepository


class MemoryService:
    def __init__(self, repository: ChatRepository):
        self.repository = repository

    def create_session(self, title: str = "New chat"):
        return self.repository.create_session(title=title)

    def get_or_create_session(self, session_id: int | None):
        if session_id is None:
            return self.repository.create_session()

        session = self.repository.get_session(session_id)
        if session is None:
            raise ValueError(f"Session with id={session_id} not found")

        return session

    def save_user_message(self, session_id: int, content: str):
        return self.repository.add_message(session_id=session_id, role="user", content=content)

    def save_assistant_message(self, session_id: int, content: str):
        return self.repository.add_message(session_id=session_id, role="assistant", content=content)

    def get_history(self, session_id: int, limit: int):
        messages = self.repository.get_messages(session_id=session_id, limit=limit)
        return [{"role": msg.role, "content": msg.content} for msg in messages]