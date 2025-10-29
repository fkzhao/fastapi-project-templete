"""
Application initialization and middleware setup
Centralized middleware configuration and loading
"""
import logging
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.core.middleware_config import get_middleware_config
from src.core.middleware import (
    AuditLogMiddleware,
    RequestLoggingMiddleware,
    RequestIDMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    ProcessTimeMiddleware,
)

logger = logging.getLogger(__name__)


def init_middleware(app: FastAPI) -> None:
    """
    Initialize and configure all middleware based on global configuration.
    Middleware is added in reverse order of execution.

    Args:
        app: FastAPI application instance
    """
    config = get_middleware_config()

    logger.info("Initializing middleware with configuration:")
    logger.info(f"  CORS: {config.cors_enabled}")
    logger.info(f"  Security Headers: {config.security_headers_enabled}")
    logger.info(f"  Request ID: {config.request_id_enabled}")
    logger.info(f"  Process Time: {config.process_time_enabled}")
    logger.info(f"  Request Logging: {config.request_logging_enabled}")
    logger.info(f"  Audit Log: {config.audit_log_enabled}")
    logger.info(f"  Rate Limiting: {config.rate_limit_enabled}")
    logger.info(f"  GZip: {config.gzip_enabled}")
    logger.info(f"  Trusted Host: {config.trusted_host_enabled}")

    # ============ Middleware Loading (in reverse execution order) ============

    # 8. Trusted Host - Validate host header (production security)
    if config.trusted_host_enabled:
        logger.info(f"Loading Trusted Host middleware with allowed hosts: {config.trusted_host_allowed}")
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=config.trusted_host_allowed
        )

    # 7. GZip Compression - Compress responses
    if config.gzip_enabled:
        logger.info(f"Loading GZip middleware with minimum size: {config.gzip_minimum_size} bytes")
        app.add_middleware(
            GZipMiddleware,
            minimum_size=config.gzip_minimum_size
        )

    # 6. Rate Limiting - Limit requests per client
    if config.rate_limit_enabled:
        logger.info(
            f"Loading Rate Limit middleware: {config.rate_limit_per_minute}/min, "
            f"{config.rate_limit_per_hour}/hour"
        )
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=config.rate_limit_per_minute,
            requests_per_hour=config.rate_limit_per_hour
        )

    # 5. Audit Log - Log API operations for audit trail
    if config.audit_log_enabled:
        logger.info(
            f"Loading Audit Log middleware for methods: {config.audit_log_methods}, "
            f"excluding paths: {config.audit_log_exclude_paths}"
        )
        app.add_middleware(
            AuditLogMiddleware,
            methods=config.audit_log_methods,
            exclude_paths=config.audit_log_exclude_paths
        )

    # 4. Request Logging - Log all requests and responses
    if config.request_logging_enabled:
        logger.info("Loading Request Logging middleware")
        app.add_middleware(RequestLoggingMiddleware)

    # 3. Process Time - Measure request processing time
    if config.process_time_enabled:
        logger.info("Loading Process Time middleware")
        app.add_middleware(ProcessTimeMiddleware)

    # 2. Request ID - Add unique ID to each request
    if config.request_id_enabled:
        logger.info("Loading Request ID middleware")
        app.add_middleware(RequestIDMiddleware)

    # 1. Security Headers - Add security-related headers
    if config.security_headers_enabled:
        logger.info("Loading Security Headers middleware")
        app.add_middleware(SecurityHeadersMiddleware)

    # 0. CORS - Enable Cross-Origin Resource Sharing (must be first/last in execution)
    if config.cors_enabled:
        logger.info(f"Loading CORS middleware with origins: {config.cors_origins}")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origins,
            allow_credentials=config.cors_credentials,
            allow_methods=config.cors_methods,
            allow_headers=config.cors_headers,
            max_age=config.cors_max_age,
        )

    logger.info("Middleware initialization completed")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application with all middleware.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Service-Differentiated API",
        version="0.1.0",
        description="FastAPI application with configurable middleware",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Initialize all middleware
    init_middleware(app)

    return app


__all__ = ["init_middleware", "create_app"]

