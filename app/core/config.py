from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "My Local GPT"
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    llm_backend: str = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3"

    database_url: str = "sqlite:///./local_gpt.db"
    chat_history_limit: int = 20
    chat_context_max_chars: int = 6000

    summary_trigger_messages: int = 12
    summary_max_chars: int = 2000
    summary_keep_recent_messages: int = 6

    chroma_path: str = "./data/chroma"
    docs_path: str = "./data/docs"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_top_k: int = 4
    rag_chunk_size: int = 800
    rag_chunk_overlap: int = 120


settings = Settings()