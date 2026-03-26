from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/scrounger.db"
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    openrouter_fallback_model: str = "deepseek/deepseek-chat"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
