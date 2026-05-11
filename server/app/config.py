from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Mihits Cloud"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mihits_cloud"
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

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

    # Upload
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024 * 1024 * 1024  # 5TB
    CHUNK_SIZE: int = 5 * 1024 * 1024  # 5MB
    UPLOAD_SESSION_EXPIRE_HOURS: int = 24
    PRESIGNED_URL_EXPIRE_SECONDS: int = 3600  # 1h

    # Rate Limiting
    LOGIN_RATE_LIMIT: str = "5/minute"

    # Storage
    DEFAULT_STORAGE_QUOTA: int = 5 * 1024 * 1024 * 1024  # 5GB
    TRASH_AUTO_DELETE_DAYS: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
