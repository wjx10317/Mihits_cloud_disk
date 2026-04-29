from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Mihits Cloud"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mihits_cloud"
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_PREFIX: str = "mihits-"
    MINIO_SECURE: bool = False

    # Rate Limiting
    LOGIN_RATE_LIMIT: str = "5/minute"

    # Storage
    DEFAULT_STORAGE_QUOTA: int = 5 * 1024 * 1024 * 1024  # 5GB

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
