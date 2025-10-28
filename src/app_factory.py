from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.admin import init_admin
from src.router import user, product
from src.core.middleware import (
    AuditLogMiddleware,
    RequestLoggingMiddleware,
    RequestIDMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    ProcessTimeMiddleware,
    get_cors_config,
)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    app = FastAPI(
        title="Service-Differentiated API",
        version="0.1.0",
        description="Different services live under distinct path prefixes.",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ============ Middleware Configuration ============
    # Note: Middleware is executed in REVERSE order (last added = first executed)
    # So we add them in reverse order of desired execution

    # 8. Trusted Host - Validate host header (uncomment in production)
    # app.add_middleware(
    #     TrustedHostMiddleware,
    #     allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    # )

    # 7. GZip Compression - Compress responses (last to compress final response)
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 6. Rate Limiting - Limit requests per client (optional)
    # Uncomment to enable rate limiting
    # app.add_middleware(
    #     RateLimitMiddleware,
    #     requests_per_minute=60,
    #     requests_per_hour=1000
    # )

    # 5. Audit Log - Log API operations for audit trail
    app.add_middleware(
        AuditLogMiddleware,
        methods=["POST", "PUT", "DELETE", "PATCH"],
        exclude_paths=["/health", "/docs", "/redoc", "/openapi.json"]
    )

    # 4. Request Logging - Log all requests and responses
    app.add_middleware(RequestLoggingMiddleware)

    # 3. Process Time - Measure request processing time
    app.add_middleware(ProcessTimeMiddleware)

    # 2. Request ID - Add unique ID to each request
    app.add_middleware(RequestIDMiddleware)

    # 1. Security Headers - Add security-related headers (first to process)
    app.add_middleware(SecurityHeadersMiddleware)

    # 0. CORS - Enable Cross-Origin Resource Sharing (must be first)
    cors_config = get_cors_config()
    app.add_middleware(CORSMiddleware, **cors_config)

    # ============ Admin Panel ============
    init_admin(app)

    # ============ Route Handlers ============
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Welcome to FastAPI Project Template",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/health"
        }

    @app.get("/health")
    async def health():
        """Health check endpoint for Docker and monitoring."""
        return {
            "status": "healthy",
            "version": "0.1.0",
            "service": "FastAPI Application"
        }

    # ============ API Routers ============
    app.include_router(user.router, prefix="/user", tags=["User Operations"])
    app.include_router(product.router, prefix="/product", tags=["Product Operations"])

    return app

