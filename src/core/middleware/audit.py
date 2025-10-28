import re
import json
import logging
from typing import Any
from datetime import datetime
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.responses import Response, StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

logger = logging.getLogger(__name__)


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware for auditing API requests and responses.
    Logs request arguments and response bodies for specified HTTP methods.
    """

    def __init__(self, app, methods: list[str] = None, exclude_paths: list[str] = None):
        super().__init__(app)
        self.methods = methods or ["POST", "PUT", "DELETE", "PATCH"]
        self.exclude_paths = exclude_paths or []
        self.audit_log_paths = ["/api/v1/auditlog/list"]
        self.max_body_size = 1024 * 1024  # 1MB

    async def get_request_args(self, request: Request) -> dict:
        args = {}
        for key, value in request.query_params.items():
            args[key] = value
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")

            if "multipart/form-data" in content_type:
                return args

            try:
                body = await request.json()
                args.update(body)
            except json.JSONDecodeError:
                try:
                    body = await request.form()
                    args.update(body)
                except Exception as e:
                    logger.warning(f"Failed to parse request body: {e}")
        return args

    async def get_response_body(self, request: Request, response: Response) -> Any:
        if isinstance(response, StreamingResponse):
            return {"message": "[Streaming Response]"}

        if hasattr(response, "body_iterator") and not hasattr(response, "body"):
            return {"message": "[Streaming Response]"}

        body = b""
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            return {
                "code": 0,
                "msg": "Response too large to log",
                "data": None,
            }

        try:
            if hasattr(response, "body"):
                body = response.body
            else:
                body_chunks = []
                async for chunk in response.body_iterator:
                    if not isinstance(chunk, bytes):
                        chunk = chunk.encode(response.charset)
                    body_chunks.append(chunk)

                response.body_iterator = self._async_iter(body_chunks)
                body = b"".join(body_chunks)
        except Exception as e:
            logger.warning(f"Failed to read response body: {e}")
            return {"message": "[Unable to read response body]"}

        if any(request.url.path.startswith(path) for path in self.audit_log_paths):
            try:
                data = self.lenient_json(body)
                if isinstance(data, dict):
                    data.pop("response_body", None)
                    if "data" in data and isinstance(data["data"], list):
                        for item in data["data"]:
                            item.pop("response_body", None)
                return data
            except Exception as e:
                logger.warning(f"Failed to process audit log response: {e}")
                return None

        return self.lenient_json(body)

    def lenient_json(self, v: Any) -> Any:
        """Convert value to JSON if possible"""
        if isinstance(v, str | bytes):
            try:
                return json.loads(v)
            except (ValueError, TypeError):
                pass
        return v

    async def _async_iter(self, items: list[bytes]) -> AsyncGenerator[bytes, None]:
        """Helper to create async iterator from list"""
        for item in items:
            yield item

    async def get_request_log(self, request: Request, response: Response) -> dict:
        data: dict = {
            "path": request.url.path,
            "status": response.status_code,
            "method": request.method,
        }

        app: FastAPI = request.app
        for route in app.routes:
            if (
                    isinstance(route, APIRoute)
                    and route.path_regex.match(request.url.path)
                    and request.method in route.methods
            ):
                data["module"] = ",".join(route.tags)
                data["summary"] = route.summary
        try:
            token = request.headers.get("token")
            user_obj = None
            # if token:
            #     user_obj: User = await AuthControl.is_authed(token)
            data["user_id"] = user_obj.id if user_obj else 0
            data["username"] = user_obj.username if user_obj else ""
        except Exception as e:
            logger.warning(f"Failed to get user info: {e}")
            data["user_id"] = 0
            data["username"] = ""
        return data

    async def before_request(self, request: Request):
        request_args = await self.get_request_args(request)
        request.state.request_args = request_args

    async def after_request(
            self, request: Request, response: Response, process_time: int
    ):
        if request.method in self.methods:
            for path in self.exclude_paths:
                if re.search(path, request.url.path, re.I) is not None:
                    return None
            data: dict = await self.get_request_log(request=request, response=response)
            data["response_time"] = process_time

            data["request_args"] = request.state.request_args
            data["response_body"] = await self.get_response_body(request, response)
            # await AuditLog.create(**data)

        return response

    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time: datetime = datetime.now()
        await self.before_request(request)
        response = await call_next(request)
        end_time: datetime = datetime.now()
        process_time = int((end_time.timestamp() - start_time.timestamp()) * 1000)
        await self.after_request(request, response, process_time)
        return response
