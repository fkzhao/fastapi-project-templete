from sqladmin import ModelView
from models.user import User


class UserAdmin(ModelView, model=User):
    """Admin view configuration for the User model."""

    column_list = [User.id, User.name]
    column_searchable_list = [User.name]
    can_create = True
    can_delete = True
