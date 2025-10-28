from fastapi import FastAPI
from admin import init_admin
from router import user, product

def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    app = FastAPI(
        title="Service-Differentiated API",
        version="0.1.0",
        description="Different services live under distinct path prefixes."
    )
    init_admin(app)

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/health")
    async def health():
        """Health check endpoint for Docker and monitoring."""
        return {"status": "healthy", "version": "0.1.0"}

    app.include_router(user.router, prefix="/user", tags=["User Operations"])
    app.include_router(product.router, prefix="/product", tags=["Product Operations"])


    return app
