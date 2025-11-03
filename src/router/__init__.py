"""
Router Module
Auto-discovers and imports all routers from this package.
"""
import importlib
import logging
from pathlib import Path
from typing import List, Tuple
from fastapi import APIRouter

logger = logging.getLogger(__name__)


def discover_routers() -> List[Tuple[str, APIRouter, dict]]:
    """
    Automatically discover all routers in the router package.

    Returns:
        List of tuples: (module_name, router_instance, router_config)
        router_config contains: prefix, tags, and other router metadata
    """
    routers = []
    current_dir = Path(__file__).parent

    # Get all Python files in router directory
    for file_path in current_dir.glob("*.py"):
        # Skip __init__.py, base.py, and private files
        if file_path.stem in ["__init__", "base"] or file_path.stem.startswith("_"):
            continue

        module_name = file_path.stem

        try:
            # Import the module
            module = importlib.import_module(f"router.{module_name}")

            # Check if module has a 'router' attribute
            if hasattr(module, "router") and isinstance(module.router, APIRouter):
                router_instance = module.router

                # Extract router configuration
                config = {
                    "prefix": f"/{module_name}",  # Default prefix based on module name
                    "tags": [module_name.replace("_", " ").title()],
                }

                # Check if module has custom config
                if hasattr(module, "ROUTER_CONFIG"):
                    config.update(module.ROUTER_CONFIG)

                routers.append((module_name, router_instance, config))
                logger.info(f"✓ Discovered router: {module_name}")

            else:
                logger.debug(f"Module {module_name} has no router attribute")

        except Exception as e:
            logger.error(f"✗ Failed to load router from {module_name}: {e}")

    return routers


def get_all_routers() -> List[Tuple[str, APIRouter, dict]]:
    """
    Get all discovered routers.

    Returns:
        List of tuples: (module_name, router_instance, router_config)
    """
    return discover_routers()


def register_routers(app, auto_prefix: bool = True, auto_tags: bool = True):
    """
    Register all discovered routers to a FastAPI app.

    Args:
        app: FastAPI application instance
        auto_prefix: Automatically add prefix based on module name
        auto_tags: Automatically add tags based on module name

    Example:
        from fastapi import FastAPI
        from router import register_routers

        app = FastAPI()
        register_routers(app)
    """
    routers = discover_routers()

    logger.info(f"Registering {len(routers)} routers to FastAPI app")

    for module_name, router_instance, config in routers:
        prefix = config["prefix"] if auto_prefix else ""
        tags = config["tags"] if auto_tags else None

        app.include_router(
            router_instance,
            prefix=prefix,
            tags=tags
        )

        logger.info(f"✓ Registered router: {module_name} at {prefix}")

    logger.info("Router registration completed")


# Auto-import and expose routers
_discovered_routers = discover_routers()

# Export router instances for backward compatibility
for module_name, router_instance, config in _discovered_routers:
    globals()[module_name] = importlib.import_module(f"router.{module_name}")

__all__ = ["discover_routers", "get_all_routers", "register_routers"] + [name for name, _, _ in _discovered_routers]

