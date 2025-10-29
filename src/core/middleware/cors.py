"""
CORS (Cross-Origin Resource Sharing) Middleware Configuration
"""
from typing import List
import os


class CORSConfig:
    """CORS configuration settings"""

    # Allow origins - can be set via environment variable
    ALLOW_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")

    # Allow credentials
    ALLOW_CREDENTIALS: bool = True

    # Allow methods
    ALLOW_METHODS: List[str] = ["*"]

    # Allow headers
    ALLOW_HEADERS: List[str] = ["*"]

    # Max age for preflight requests
    MAX_AGE: int = 600


def get_cors_config() -> dict:
    """Get CORS configuration as dictionary"""
    return {
        "allow_origins": CORSConfig.ALLOW_ORIGINS,
        "allow_credentials": CORSConfig.ALLOW_CREDENTIALS,
        "allow_methods": CORSConfig.ALLOW_METHODS,
        "allow_headers": CORSConfig.ALLOW_HEADERS,
        "max_age": CORSConfig.MAX_AGE,
    }

