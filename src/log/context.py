"""
Log Context Manager
Provides request tracing and user association functionality
"""
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Lazy import to avoid circular imports
request_context: ContextVar[Dict[str, Any]] = ContextVar("request_context", default={})

# Context variables
_request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
_user_id: ContextVar[Optional[int]] = ContextVar("user_id", default=None)


class LogContext:
    """Log Context Manager"""

    @staticmethod
    def generate_request_id() -> str:
        """Generate unique request ID"""
        return str(uuid.uuid4())

    @staticmethod
    def set_request_id(request_id: str = None) -> str:
        """Set request ID"""
        if request_id is None:
            request_id = LogContext.generate_request_id()
        _request_id.set(request_id)
        LogContext.set_context("request_id", request_id)
        return request_id

    @staticmethod
    def set_user_id(user_id: int):
        """Set user ID"""
        _user_id.set(user_id)
        LogContext.set_context("user_id", user_id)

    @staticmethod
    def get_request_id() -> Optional[str]:
        """Get current request ID"""
        return _request_id.get()

    @staticmethod
    def get_user_id() -> Optional[int]:
        """Get current user ID"""
        return _user_id.get()

    @staticmethod
    def set_context(key: str, value: Any):
        """Set context information"""
        ctx = request_context.get()
        if ctx is None:
            ctx = {}
        ctx[key] = value
        request_context.set(ctx)

    @staticmethod
    def get_context(key: str, default: Any = None) -> Any:
        """Get context information"""
        ctx = request_context.get()
        if ctx is None:
            return default
        return ctx.get(key, default)

    @staticmethod
    def update_context(**kwargs):
        """Batch update context information"""
        ctx = request_context.get()
        if ctx is None:
            ctx = {}
        ctx.update(kwargs)
        request_context.set(ctx)

    @staticmethod
    def get_logger(name: str = None):
        """Get logger with context"""
        # Lazy import to avoid circular imports
        from log.log import get_logger

        # Get all context information
        ctx = request_context.get() or {}

        extra = {
            "request_id": LogContext.get_request_id(),
            "user_id": LogContext.get_user_id(),
            **ctx
        }

        return get_logger(name or __name__, **extra)

    @staticmethod
    def clear():
        """Clear context"""
        _request_id.set(None)
        _user_id.set(None)
        request_context.set({})


class RequestLogContext:
    """Request-level log context manager"""

    def __init__(self, **kwargs):
        self.context_data = kwargs
        self.old_context = None

    def __enter__(self):
        # Save old values
        self.old_context = request_context.get().copy() if request_context.get() else {}

        # Set new values
        LogContext.update_context(**self.context_data)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore old values
        request_context.set(self.old_context)
        return False

