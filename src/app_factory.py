from fastapi import FastAPI

from admin import init_admin_panel
from router import register_routers
from core.app import init_middleware
from core.mcp_server import init_mcp_server


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
    # All middleware is configured via environment variables or default values
    # See src/core/middleware_config.py for configuration options
    # See src/core/app.py for middleware initialization logic
    init_middleware(app)

    # ============ MCP SSE Server ============
    # Model Context Protocol Server-Sent Events server
    # Configure via MCP_* environment variables
    # See src/core/mcp_config.py for configuration options
    init_mcp_server(app)

    # ============ Admin Panel ============
    init_admin_panel(app)

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
    # Auto-discover and register all routers from router module
    register_routers(app)

    return app

