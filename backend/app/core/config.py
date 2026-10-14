from typing import List, Union
import json
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Feedback Intelligence System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS configuration
    BACKEND_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "feedback_db"
    
    # Defaults to SQLite for immediate local/test viability if Postgres is not spun up
    DATABASE_URL: str = "sqlite:///./feedback.db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Union[str, None]) -> str:
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+psycopg2://", 1)
            elif v.startswith("postgresql://") and not v.startswith("postgresql+"):
                return v.replace("postgresql://", "postgresql+psycopg2://", 1)
            return v
        return "sqlite:///./feedback.db"

    # Redis and Celery
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    LOG_LEVEL: str = "INFO"

    # AI/ML Configuration
    SENTIMENT_MODEL: str = "baseline"
    ENABLE_ADVANCED_NLP: bool = False
    CLASSIFICATION_THRESHOLD: float = 0.3

    # OpenAI Integration (Optional)
    OPENAI_API_KEY: Union[str, None] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Security and Authentication
    SECRET_KEY: str = "feedback-intelligence-insecure-development-secret-key-32chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    AUTH_RATE_LIMIT_PER_MINUTE: int = 15
    INITIAL_ADMIN_EMAIL: Union[str, None] = None
    INITIAL_ADMIN_PASSWORD: Union[str, None] = None
    CELERY_TASK_ALWAYS_EAGER: bool = False

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        env = info.data.get("ENVIRONMENT", "development")
        if env == "production" and ("insecure" in v.lower() or len(v) < 32):
            raise ValueError("SECRET_KEY must be a secure random string of at least 32 characters in production.")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

