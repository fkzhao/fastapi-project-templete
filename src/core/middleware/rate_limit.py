"""
Rate Limiting Middleware
Simple in-memory rate limiter for API endpoints
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from fastapi.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter.
    For production, use Redis-based rate limiting.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # Storage: {client_ip: [(timestamp, count)]}
        self.minute_storage: Dict[str, list] = defaultdict(list)
        self.hour_storage: Dict[str, list] = defaultdict(list)

    def _check_rate_limit(
        self,
        client_ip: str,
        storage: Dict[str, list],
        window_seconds: int,
        max_requests: int
    ) -> Tuple[bool, int]:
        """
        Check if request is within rate limit.
        Returns (is_allowed, remaining_requests)
        """
        current_time = time.time()
        window_start = current_time - window_seconds

        # Clean old requests
        storage[client_ip] = [
            req_time for req_time in storage[client_ip]
            if req_time > window_start
        ]

        # Check limit
        request_count = len(storage[client_ip])

        if request_count >= max_requests:
            return False, 0

        # Add current request
        storage[client_ip].append(current_time)

        return True, max_requests - request_count - 1

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        # Check minute limit
        minute_allowed, minute_remaining = self._check_rate_limit(
            client_ip,
            self.minute_storage,
            60,
            self.requests_per_minute
        )

        if not minute_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Too many requests per minute."
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + 60))
                }
            )

        # Check hour limit
        hour_allowed, hour_remaining = self._check_rate_limit(
            client_ip,
            self.hour_storage,
            3600,
            self.requests_per_hour
        )

        if not hour_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Too many requests per hour."
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_hour),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + 3600))
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(minute_remaining)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(hour_remaining)

        return response

