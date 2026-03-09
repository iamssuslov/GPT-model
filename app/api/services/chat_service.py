from app.api.core.config import settings
from app.api.llm.ollama_provider import OllamaProvider
from app.api.llm.mlx_provider import MLXProvider


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
    def __init__(self):
        self.provider = get_llm_provider()

    def ask(self, user_message: str) -> str:
        messages = [
            {"role": "user", "content": user_message}
        ]
        return self.provider.generate(
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            messages=messages,
        )