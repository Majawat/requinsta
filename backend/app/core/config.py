from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://requinsta:password@localhost:5432/requinsta"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_HOSTS: List[str] = ["*"]
    # Directory scanned for third-party plugin `.py` drop-ins (mount a volume here).
    PLUGINS_DIR: str = "/plugins"

    class Config:
        env_file = ".env"


settings = Settings()
