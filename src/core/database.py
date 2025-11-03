import os
import importlib
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)


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
EngineBase = declarative_base()

def init_db():
    """
    Initialize database by loading all models.
    This ensures all model classes are registered with SQLAlchemy Base.
    """
    try:
        # Get the models directory path
        current_dir = Path(__file__).resolve().parent.parent
        models_dir = current_dir / "models"

        if not models_dir.exists():
            logger.warning(f"Models directory not found: {models_dir}")
            return

        # Import all model modules
        logger.info("Loading models from: %s", models_dir)

        # Get all Python files in models directory
        for file_path in models_dir.glob("*.py"):
            # Skip __init__.py and base.py
            if file_path.stem in ["__init__", "base"]:
                continue

            module_name = file_path.stem
            try:
                # Import the model module
                importlib.import_module(f"models.{module_name}")
                logger.info(f"✓ Loaded model: models.{module_name}")
            except Exception as e:
                logger.error(f"✗ Failed to load model {module_name}: {e}")

        logger.info("Database initialization completed")

    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        raise


def init_db_with_tables():
    """
    Initialize database and create all tables.
    Note: In production, use Alembic migrations instead.
    """


    # Load all models first
    init_db()

    # Create tables (only for development/testing)
    logger.info("Creating database tables...")
    EngineBase.metadata.create_all(bind=get_engine())
    logger.info("Database tables created")


__all__ = ["engine", "DATABASE_URL", "engines", "get_engine", "init_db", "init_db_with_tables", "EngineBase"]
