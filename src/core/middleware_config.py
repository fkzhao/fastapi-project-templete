"""
Middleware Configuration
Centralized configuration for all middleware with environment variable support
"""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class MiddlewareConfig(BaseSettings):
    """
    Global middleware configuration.
    All settings can be overridden via environment variables.
    """

    # CORS Configuration
    cors_enabled: bool = Field(default=True, description="Enable CORS middleware")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"],
        description="Allowed CORS origins"
    )
    cors_credentials: bool = Field(default=True, description="Allow credentials in CORS")
    cors_methods: List[str] = Field(default=["*"], description="Allowed HTTP methods")
    cors_headers: List[str] = Field(default=["*"], description="Allowed HTTP headers")
    cors_max_age: int = Field(default=600, description="CORS preflight cache duration")

    # Security Headers Configuration
    security_headers_enabled: bool = Field(default=True, description="Enable security headers middleware")
    security_hsts_enabled: bool = Field(default=False, description="Enable HSTS (for HTTPS only)")
    security_hsts_max_age: int = Field(default=31536000, description="HSTS max age in seconds")

    # Request ID Configuration
    request_id_enabled: bool = Field(default=True, description="Enable request ID middleware")

    # Process Time Configuration
    process_time_enabled: bool = Field(default=True, description="Enable process time middleware")

    # Request Logging Configuration
    request_logging_enabled: bool = Field(default=True, description="Enable request logging middleware")

    # Audit Log Configuration
    audit_log_enabled: bool = Field(default=True, description="Enable audit log middleware")
    audit_log_methods: List[str] = Field(
        default=["POST", "PUT", "DELETE", "PATCH"],
        description="HTTP methods to audit"
    )
    audit_log_exclude_paths: List[str] = Field(
        default=["/health", "/docs", "/redoc", "/openapi.json"],
        description="Paths to exclude from audit logging"
    )

    # Rate Limiting Configuration
    rate_limit_enabled: bool = Field(default=False, description="Enable rate limiting middleware")
    rate_limit_per_minute: int = Field(default=60, description="Requests per minute per client")
    rate_limit_per_hour: int = Field(default=1000, description="Requests per hour per client")

    # GZip Compression Configuration
    gzip_enabled: bool = Field(default=True, description="Enable GZip compression middleware")
    gzip_minimum_size: int = Field(default=1000, description="Minimum response size to compress (bytes)")

    # Trusted Host Configuration
    trusted_host_enabled: bool = Field(default=False, description="Enable trusted host middleware")
    trusted_host_allowed: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed host headers"
    )

    class Config:
        env_prefix = "MIDDLEWARE_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

        # Support parsing list from comma-separated string
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name in ['cors_origins', 'cors_methods', 'cors_headers',
                            'audit_log_methods', 'audit_log_exclude_paths',
                            'trusted_host_allowed']:
                return [item.strip() for item in raw_val.split(',')]
            return raw_val


# Global middleware configuration instance
middleware_config = MiddlewareConfig()


def get_middleware_config() -> MiddlewareConfig:
    """Get the global middleware configuration instance"""
    return middleware_config

