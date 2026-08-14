from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str
    gemini_model: str = "gemini-flash-latest"
    gemini_embedding_model: str = "gemini-embedding-001"
    embedding_dim: int = 768

    database_url: str = "postgresql+psycopg2://hub:hub@localhost:5432/business_ops_hub"

    confidence_threshold: float = 0.90

    knowledge_dir: Path = Path("company-knowledge")
    logs_dir: Path = Path("logs")


settings = Settings()
settings.logs_dir.mkdir(parents=True, exist_ok=True)
