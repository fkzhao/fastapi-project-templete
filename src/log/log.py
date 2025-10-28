import logging
import os
import sys
import json
from datetime import date, datetime
from typing import Any, Dict, Set

from loguru import logger as loguru_logger

from src.settings import settings


LOGGING_RESERVED_FIELDS: Set[str] = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
}


class InterceptHandler(logging.Handler):
    """Forward standard logging logs to loguru."""

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - direct call
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        extra = {
            k: v
            for k, v in record.__dict__.items()
            if k not in LOGGING_RESERVED_FIELDS and not k.startswith("_")
        }

        loguru_logger.opt(depth=depth, exception=record.exc_info).bind(**extra).log(
            level, record.getMessage()
        )


class LogConfig:
    """Unified log configuration management"""

    def __init__(self):
        self.log_level = settings.log_level
        self.log_dir = settings.log_dir
        self.log_rotation = settings.log_rotation
        self.log_retention = settings.log_retention
        self.log_format = settings.log_format

    def ensure_log_dir(self):
        """Ensure log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)

    @staticmethod
    def default_json_handler(obj: Any) -> Any:
        """Default handling logic for JSON serialization"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Exception):
            return {"error": str(obj), "type": type(obj).__name__}
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)

    @staticmethod
    def build_log_structure(record: Dict[str, Any]) -> Dict[str, Any]:
        """Build standardized log structure"""
        # Avoid recursive references
        safe_record = {
            k: v
            for k, v in record.items()
            if k
            not in {
                "extra",
                "file",
                "function",
                "level",
                "line",
                "module",
                "name",
                "process",
                "thread",
                "time",
            }
        }

        # Support context pass-through, compatible with fields like request_id / user_id
        extra = record.get("extra", {})

        log_entry = {
            "timestamp": record["time"].timestamp(),
            "level": record["level"].name,
            "message": record["message"],
            "module": record.get("name", ""),
            "function": record.get("function", ""),
            "line": record.get("line", 0),
            **safe_record,
            **extra,
        }
        return log_entry

    @classmethod
    def serialize_log(cls, message: str) -> str:
        """Serialize log record as JSON string"""
        try:
            record = json.loads(message)
            log_entry = cls.build_log_structure(record)
            return json.dumps(log_entry, default=cls.default_json_handler, ensure_ascii=False)
        except Exception:
            return message

    @staticmethod
    def log_patcher(record: Dict[str, Any]) -> None:
        """Attach serialized content to each log record"""
        if isinstance(record["message"], str):
            record["extra"]["serialized"] = record["message"]

    def setup_logging(self):
        """Configure log output"""
        # Clear default handlers
        loguru_logger.remove()

        # Intercept standard logging, unify output format
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

        seen = set()
        for name in [
            *logging.root.manager.loggerDict.keys(),
            "gunicorn",
            "gunicorn.access",
            "gunicorn.error",
            "uvicorn",
            "uvicorn.access",
            "uvicorn.error",
        ]:
            if name not in seen:
                seen.add(name.split(".")[0])
                logging.getLogger(name).handlers = [InterceptHandler()]

        # Enable unified patcher to ensure all log output is JSON structure
        loguru_logger.configure(patcher=self.log_patcher)

        # Console output (JSON stream)
        if self.log_format == "json":
            loguru_logger.add(
                sys.stdout,
                level=self.log_level,
                format="{message}",
                serialize=True,
                enqueue=True,
                colorize=False,
            )
        else:
            loguru_logger.add(
                sys.stdout,
                level=self.log_level,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                enqueue=True,
                colorize=True,
            )

        # File output - all level logs
        loguru_logger.add(
            os.path.join(self.log_dir, "app.log"),
            level=self.log_level,
            format="{message}",
            rotation=self.log_rotation,
            retention=self.log_retention,
            compression="zip",
            serialize=True,
            enqueue=True,
            encoding="utf-8",
        )

        # Error logs in separate file
        loguru_logger.add(
            os.path.join(self.log_dir, "error.log"),
            level="ERROR",
            format="{message}",
            rotation=self.log_rotation,
            retention=self.log_retention,
            compression="zip",
            serialize=True,
            enqueue=True,
            encoding="utf-8",
        )

        # Critical error logs (CRITICAL level)
        loguru_logger.add(
            os.path.join(self.log_dir, "critical.log"),
            level="CRITICAL",
            format="{message}",
            rotation=self.log_rotation,
            retention=self.log_retention,
            compression="zip",
            serialize=True,
            enqueue=True,
            encoding="utf-8",
        )

        # Add default context to all logs
        # Note: rebinding here will create a new logger instance
        return loguru_logger


# Global log configuration instance
log_config = LogConfig()
log_config.ensure_log_dir()
logger = log_config.setup_logging()


def get_logger(name: str = None, **context) -> Any:
    """
    Get a logger with context.

    Args:
        name: Logger name (optional)
        **context: Additional context to bind to logger

    Returns:
        Logger instance with bound context
    """
    if context:
        return logger.bind(**context)
    return logger


__all__ = ["logger", "get_logger", "LogConfig"]

