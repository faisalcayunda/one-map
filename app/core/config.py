from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = Field(default="Satu Peta")
    VERSION: str = Field(default="0.1.0")
    DESCRIPTION: str = Field(default="Satu Peta API")

    # Server settings
    DEBUG: bool = Field(default=False)
    HOST: str = Field(default="localhost")
    PORT: int = Field(default=8000)

    # Database settings
    DATABASE_URL: str

    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Cors settings
    ALLOWED_ORIGINS: List[str] = Field(default=["*"])

    # S3/MinIO settings
    MINIO_ENDPOINT_URL: str = Field(default="http://localhost:9000")
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_SECURE: Optional[bool] = False
    MINIO_BUCKET_NAME: Optional[str] = Field(default="satu-peta")
    MINIO_REGION: Optional[str] = Field(default=None)

    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB default limit
    ALLOWED_EXTENSIONS: List[str] = [
        "jpg",
        "jpeg",
        "png",
        "pdf",
        "doc",
        "docx",
        "xls",
        "xlsx",
        "txt",
        "csv",
        "zip",
        "rar",
    ]

    # Settings config
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="allow")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
