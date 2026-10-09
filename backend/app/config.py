"""
FinSight Backend Configuration
Uses Pydantic Settings for environment variable management.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(PROJECT_ROOT / ".env"), ".env"],
        extra="ignore",
        case_sensitive=True,
    )

    # PostgreSQL
    POSTGRES_USER: str = "finsight_user"
    POSTGRES_PASSWORD: str = "finsight_secure_password_change_me"
    POSTGRES_DB: str = "finsight"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # MongoDB
    MONGO_URI: str = "mongodb://admin:admin_password@localhost:27017/finsight_analytics?authSource=admin"
    MONGO_DB: str = "finsight_analytics"

    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production-min-32-chars"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # Security
    BCRYPT_ROUNDS: int = 12

    # Rate limiting
    RATE_LIMIT_PER_MIN: int = 120
    RATE_LIMIT_LOGIN_PER_MIN: int = 5

    # File uploads
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    # App
    APP_NAME: str = "FinSight"
    DEBUG: bool = False


settings = Settings()