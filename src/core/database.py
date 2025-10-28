import os
from sqlalchemy import create_engine


# Support multiple databases via environment variables or config
def get_database_url(name: str) -> str:
    return os.getenv(f"DATABASE_URL_{name.upper()}") or f"sqlite:///{name}.db"


# List your supported database names here
DATABASES = ["default", "analytics"]

engines = {
    name: create_engine(
        get_database_url(name),
        connect_args={"check_same_thread": False} if get_database_url(name).startswith("sqlite") else {},
    )
    for name in DATABASES
}


def get_engine(name: str = "default"):
    return engines[name]


# For backward compatibility
engine = engines["default"]
DATABASE_URL = get_database_url("default")

__all__ = ["engine", "DATABASE_URL", "engines", "get_engine"]
