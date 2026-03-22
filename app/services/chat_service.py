from sqlalchemy.orm import Session

from app.core.config import settings
from app.llm.mlx_provider import MLXProvider
from app.llm.ollama_provider import OllamaProvider
from app.memory.repository import ChatRepository
from app.memory.service import MemoryService
from app.services.context_manager import ContextManager
from app.services.summarizer import SummarizerService


DEFAULT_SYSTEM_PROMPT = (
    "Ты локальный персональный AI-ассистент. "
    "Отвечай ясно, по делу, на русском языке, если пользователь не попросил иначе."
)


def get_llm_provider():
    backend = settings.llm_backend.lower()

    if backend == "ollama":
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
        )

    if backend == "mlx":
        return MLXProvider()

    raise ValueError(f"Unsupported LLM backend: {settings.llm_backend}")


class ChatService:
    def __init__(self, db: Session):
        self.provider = get_llm_provider()
        self.memory = MemoryService(ChatRepository(db))
        self.context_manager = ContextManager(
            max_chars=settings.chat_context_max_chars,
            max_messages=settings.chat_history_limit,
        )
        self.summarizer = SummarizerService(self.provider)

    def create_session(self, title: str = "New chat"):
        return self.memory.create_session(title=title)

    def list_sessions(self):
        return self.memory.repository.list_sessions()

    def get_session_messages(self, session_id: int):
        return self.memory.get_all_messages(session_id)

    def ask(self, user_message: str, session_id: int | None = None) -> dict:
        session = self.memory.get_or_create_session(session_id)

        self.memory.save_user_message(session.id, user_message)

        full_history = self.memory.get_full_history(session.id)

        updated_summary, recent_messages = self.summarizer.update_summary(
            existing_summary=session.summary,
            full_history=full_history,
        )

        if updated_summary != session.summary:
            self.memory.update_summary(session.id, updated_summary)

        context_messages = self.context_manager.build_context(
            messages=recent_messages,
            summary=updated_summary,
        )

        answer = self.provider.generate(
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            messages=context_messages,
        )

        self.memory.save_assistant_message(session.id, answer)

        return {
            "session_id": session.id,
            "answer": answer,
        }