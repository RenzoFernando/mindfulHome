from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "MindfulHome"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/mindfulhome"

    SECRET_KEY: str = "mindfulhome-dev-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    GROQ_API_KEY: Optional[str] = None

    @field_validator("DEBUG", mode="before")
    @classmethod
    def validate_debug(cls, value):
        if value is None or value == "":
            return False
        return value

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, value):
        if value is None or value == "":
            return "postgresql://postgres:postgres@db:5432/mindfulhome"
        return value

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, value):
        if value is None or value == "":
            return "mindfulhome-dev-secret-key"
        return value

    @field_validator("GROQ_API_KEY", mode="before")
    @classmethod
    def validate_groq_api_key(cls, value):
        if value is None or value == "":
            return None
        return value

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
