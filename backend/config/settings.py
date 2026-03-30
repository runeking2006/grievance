from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str
    LOG_LEVEL: str = "INFO"
    METRICS_ENABLED: bool = True
    CLASSIFIER_MODEL: str = "facebook/bart-large-mnli"
    CLASSIFIER_ENABLED: bool = True
    GENERATOR_MODEL: str = "google/flan-t5-base"
    GENERATOR_ENABLED: bool = True
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    USER_DEFAULT_ROLE: str = "student"
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None
    USE_DISTRIBUTED_QUEUE: bool = False
    PGVECTOR_ENABLED: bool = True
    VECTOR_DIMENSION: int = 384
    SIMILARITY_CANDIDATE_LIMIT: int = 250
    VECTOR_SIMILARITY_THRESHOLD: float = 0.35
    VECTOR_HNSW_EF_SEARCH: int = 64
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str | None = None
    SMTP_USE_TLS: bool = True

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
