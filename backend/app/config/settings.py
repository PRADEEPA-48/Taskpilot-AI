"""
Application settings loaded from environment variables.
Raises descriptive errors on startup if required vars are missing.
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Groq / LangChain
    groq_api_key: str

    # Google OAuth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str = "http://localhost:8000/auth/callback"

    # Email
    email_provider: str = "resend"          # "resend" or "gmail"
    resend_api_key: str = ""
    sender_email: str = "noreply@taskpilot.ai"

    # CORS
    allowed_origins: str = "http://localhost:3000"

    # App
    log_level: str = "INFO"
    secret_key: str = "change-me-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
