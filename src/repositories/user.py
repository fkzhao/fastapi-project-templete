"""
User Repository
Data access layer for User model
"""
from repositories.base import BaseRepository
from models.user import User


class UserRepository(BaseRepository[User]):
    """User repository"""
    model = User

    def get_by_name(self, name: str):
        """Get user by name"""
        return self.get_one(name=name)

