import pkgutil
import importlib
from core.database import engine
from .base import BaseModel, Base
from .user import User
from .product import Product


# Dynamically import all modules in the current package
def import_all_models():
    package = __name__
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{package}.{module_name}")

import_all_models()

# Create all tables for subclasses of BaseModel
Base.metadata.create_all(bind=engine)

__all__ = ["Product", "User"]