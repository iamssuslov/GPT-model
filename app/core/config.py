from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "My Local GPT"
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    llm_backend: str = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3"

    database_url: str = "sqlite:///./local_gpt.db"
    chat_history_limit: int = 10


settings = Settings()