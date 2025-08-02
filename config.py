from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE = Path(__file__).resolve().parent
env_path = BASE / ".env"  # wherever your .env actually lives


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding="utf-8")

    GOOGLE_API_KEY: str
    GOOGLE_MODEL: str = "gemini-1.5-flash"
    TELEGRAM_TOKEN: str
    HN_TOP_LIMIT: int = 100
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

settings = Settings()
