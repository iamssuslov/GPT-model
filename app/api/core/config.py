from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "My Local GPT"
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    llm_backend: str = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3"


settings = Settings()