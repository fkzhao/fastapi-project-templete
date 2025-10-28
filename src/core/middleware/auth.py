from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce authentication on incoming requests.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        # Here you would implement your authentication logic
        # For example, check for a valid token in headers
        auth_header = request.headers.get("Authorization")
        if not auth_header or not self._is_token_valid(auth_header):
            from starlette.responses import JSONResponse
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

        response = await call_next(request)
        return response

    def _is_token_valid(self, token: str) -> bool:
        # Placeholder for token validation logic
        # Replace with actual validation against your auth service
        valid_tokens = {"valid-token-123"}  # Example set of valid tokens
        return token in valid_tokens