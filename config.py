from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE = Path(__file__).resolve().parent
env_path = BASE / ".env"  # wherever your .env actually lives


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding="utf-8")

    TELEGRAM_TOKEN: str
    OLLAMA_MODEL: str
    OLLAMA_URL: str
    HN_TOP_LIMIT: int
    LANGSMITH_TRACING: str
    LANGSMITH_ENDPOINT: str
    LANGSMITH_API_KEY: str
    LANGSMITH_PROJECT: str
    USER_AGENT: str


settings = Settings()
