from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

    APP_NAME: str = "Research Analytics SaaS"
    API_V1_STR: str = "/api/v1"
    ENV: str = "development"

    SECRET_KEY: str = "change_me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str

    BACKEND_CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    STORAGE_ROOT: str = "storage"
    MAX_UPLOAD_SIZE_MB: int = 10
    CATEGORICAL_UNIQUE_RATIO_THRESHOLD: float = 0.05


@lru_cache
def get_settings() -> Settings:
    return Settings()
