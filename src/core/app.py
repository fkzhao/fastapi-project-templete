from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from core.middleware.log import (
    RequestLoggingMiddleware,
)

def init_app():
    pass


def make_middlewares():
    middleware = [
        Middleware(
            CORSMiddleware,
            # allow_origins=settings.CORS_ORIGINS_LIST,
            # allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
            # allow_methods=settings.CORS_ALLOW_METHODS,
            # allow_headers=settings.CORS_ALLOW_HEADERS,
        ),
        Middleware(RequestLoggingMiddleware),
        # Middleware(
        #     HttpAuditLogMiddleware,
        #     methods=["GET", "POST", "PUT", "DELETE"],
        #     exclude_paths=[
        #         "/api/v1/base/access_token",
        #         "/docs",
        #         "/openapi.json",
        #     ],
        # ),
    ]
    return middleware
