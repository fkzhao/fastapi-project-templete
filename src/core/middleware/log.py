import traceback
from datetime import datetime
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

from log.context import LogContext


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all requests and responses with context.
    """

    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = datetime.now()

        request_id = LogContext.set_request_id()
        LogContext.update_context(
            method=request.method,
            path=request.url.path,
            url=str(request.url),
            query_params=dict(request.query_params),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            content_type=request.headers.get("content-type"),
            content_length=request.headers.get("content-length"),
            start_time=start_time.isoformat(),
        )

        context_logger = LogContext.get_logger()

        context_logger.info(f"Request started: {request.method} {request.url.path}")

        try:
            response = await call_next(request)

            end_time = datetime.now()
            process_time = (end_time - start_time).total_seconds() * 1000

            LogContext.update_context(
                status_code=response.status_code,
                process_time_ms=process_time,
                end_time=end_time.isoformat(),
                response_headers=dict(response.headers),
            )

            # Log request completion
            context_logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code} ({process_time:.2f}ms)"
            )

            return response

        except Exception as e:
            # Calculate processing time
            end_time = datetime.now()
            process_time = (end_time - start_time).total_seconds() * 1000

            # Update context information
            LogContext.update_context(
                exception_occurred=True,
                exception_type=type(e).__name__,
                exception_msg=str(e),
                process_time_ms=process_time,
                end_time=end_time.isoformat(),
                traceback=traceback.format_exc()
            )

            # Log detailed request exception information
            context_logger.error(
                f"Request processing exception: {request.method} {request.url.path} - {type(e).__name__}: {str(e)} ({process_time:.2f}ms)"
            )

            raise
        finally:
            # Clean up request context
            LogContext.clear()

