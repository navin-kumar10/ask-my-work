from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ask My Work"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    postgres_url: str = "postgresql://ask_my_work:change-me@postgres:5432/ask_my_work"

    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "ask_my_work"

    # Ollama is already running on the host, outside this Compose stack.
    # Linux host access from Docker is provided through host.docker.internal.
    ollama_url: str = "http://host.docker.internal:11434"
    chat_model: str = "qwen3:4b"
    embed_model: str = "nomic-embed-text"

    top_k: int = 5
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
