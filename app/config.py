from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Ask My Work"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "ask_my_work"
    ollama_url: str = "http://ollama:11434"
    chat_model: str = "qwen3:4b"
    embed_model: str = "nomic-embed-text"
    sqlite_path: str = "/data/ask-my-work.db"
    top_k: int = 5
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
