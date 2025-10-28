import inspect
import pkgutil
import importlib
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from fastapi import Request
from core.database import engine


class MyAuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        # Simple check (replace with secure logic in production)
        if username == "admin" and password == "123456":
            # Set session token (simplified example)
            request.session.update({"token": "some-secret-token"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return token == "some-secret-token"


def discover_model_views():
    """Automatically discover all ModelView subclasses in the admin package."""
    model_views = []
    package = __name__

    # Import all modules in the current package
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f"{package}.{module_name}")

        # Find all ModelView subclasses in the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, ModelView) and obj is not ModelView:
                model_views.append(obj)

    return model_views


def init_admin(app):
    """Create and register the SQLAdmin dashboard views."""
    admin = Admin(app, engine, authentication_backend=MyAuthBackend("123"))

    # Automatically discover and register all ModelView subclasses
    for view_class in discover_model_views():
        admin.add_view(view_class)

    return admin
