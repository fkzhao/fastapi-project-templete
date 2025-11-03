"""
Application Settings
Configuration management using environment variables
"""
import os
from pathlib import Path

def get_required_env(key: str) -> str:
    """Get required environment variable or raise error"""
    value = os.getenv(key)
    if not value:
        raise ValueError(f"{key} environment variable is required")
    return value

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

    # Redis Configuration
    redis_mode: str = os.getenv("REDIS_MODE", "standalone")  # "standalone" or "cluster"
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_cluster_nodes: str = os.getenv("REDIS_CLUSTER_NODES", "")  # Comma-separated list: "host1:port1,host2:port2"
    redis_max_connections: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
    redis_socket_timeout: int = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
    redis_socket_connect_timeout: int = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5"))
    redis_decode_responses: bool = os.getenv("REDIS_DECODE_RESPONSES", "true").lower() == "true"
    redis_ssl: bool = os.getenv("REDIS_SSL", "false").lower() == "true"
    redis_ssl_cert_reqs: str = os.getenv("REDIS_SSL_CERT_REQS", "required")  # "required", "optional", "none"
    redis_key_prefix: str = os.getenv("REDIS_KEY_PREFIX", "mcp")
    redis_default_ttl: int = int(os.getenv("REDIS_DEFAULT_TTL", "3600"))

def __init__(self):
        # Ensure log directory exists
        log_path = Path(self.log_dir)
        if not log_path.exists():
            log_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()


__all__ = ["settings", "Settings"]

