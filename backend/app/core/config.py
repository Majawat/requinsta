from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Requinsta"
    VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str = "postgresql://requinsta:password@db:5432/requinsta"

    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    class Config:
        env_file = ".env"


settings = Settings()
