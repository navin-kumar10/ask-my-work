from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ask My Work"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # API container uses host networking on Ubuntu so localhost reaches
    # PostgreSQL/Qdrant published ports and the native Ollama service.
    postgres_url: str = "postgresql://ask_my_work:change-me@127.0.0.1:5432/ask_my_work"

    qdrant_url: str = "http://127.0.0.1:6333"
    qdrant_collection: str = "ask_my_work"

    # Ollama runs natively on the Ubuntu host, outside Docker.
    ollama_url: str = "http://127.0.0.1:11434"
    chat_model: str = "qwen3:4b"
    embed_model: str = "nomic-embed-text"

    top_k: int = 5
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
