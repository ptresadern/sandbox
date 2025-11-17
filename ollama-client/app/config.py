"""Application configuration"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_embedding_model: str = "nomic-embed-text"

    # Application Settings
    secret_key: str = "change-this-secret-key-in-production"
    admin_password: str = "admin123"
    knowledge_base_path: Path = Path("./knowledge-base")

    # Vector Database
    vector_db_type: str = "chroma"
    vector_db_path: Path = Path("./data/vectordb")

    # RAG Settings
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 5

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Authentication
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    algorithm: str = "HS256"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.knowledge_base_path.mkdir(parents=True, exist_ok=True)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)


settings = Settings()
