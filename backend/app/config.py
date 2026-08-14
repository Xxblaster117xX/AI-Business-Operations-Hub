from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str
    gemini_model: str = "gemini-flash-lite-latest"
    gemini_embedding_model: str = "gemini-embedding-001"
    embedding_dim: int = 768

    database_url: str = "postgresql+psycopg2://hub:hub@localhost:5432/business_ops_hub"

    confidence_threshold: float = 0.90

    knowledge_dir: Path = Path("company-knowledge")
    logs_dir: Path = Path("logs")

    # SMTP is optional — when smtp_user/smtp_password are unset, email_client
    # falls back to the simulated mock (logs/emails.log) so the rest of the
    # pipeline still runs without credentials.
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    email_from_name: str = "AI Business Operations Hub"

    @property
    def smtp_enabled(self) -> bool:
        return bool(self.smtp_user and self.smtp_password)


settings = Settings()
settings.logs_dir.mkdir(parents=True, exist_ok=True)
