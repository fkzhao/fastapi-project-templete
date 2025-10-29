"""
Response Time Middleware
Adds X-Process-Time header to show request processing time
"""
import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from fastapi.responses import Response


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """
    Middleware to measure and add processing time to response headers.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        # Add processing time to response header (in milliseconds)
        response.headers["X-Process-Time"] = f"{process_time * 1000:.2f}ms"

        return response

