"""
Application Settings
Configuration management using environment variables
"""
import os
from pathlib import Path


class Settings:
    """Application settings with environment variable support"""

    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_dir: str = os.getenv("LOG_DIR", "logs")
    log_format: str = os.getenv("LOG_FORMAT", "text")  # "text" or "json"
    log_rotation: str = os.getenv("LOG_ROTATION", "500 MB")
    log_retention: str = os.getenv("LOG_RETENTION", "10 days")

    # Application Configuration
    app_name: str = os.getenv("APP_NAME", "FastAPI Application")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database Configuration
    database_url_default: str = os.getenv(
        "DATABASE_URL_DEFAULT",
        "sqlite:///./data/database.db"
    )
    database_url_analytics: str = os.getenv(
        "DATABASE_URL_ANALYTICS",
        "sqlite:///./data/analytics.db"
    )

    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    session_secret: str = os.getenv("SESSION_SECRET", "change-this-session-secret")

    # CORS
    cors_origins: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8000"
    )

    def __init__(self):
        # Ensure log directory exists
        log_path = Path(self.log_dir)
        if not log_path.exists():
            log_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()


__all__ = ["settings", "Settings"]

