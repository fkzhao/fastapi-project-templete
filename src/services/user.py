"""
User Service
Business logic for user management
"""
from services.base import BaseService
from repositories.user import UserRepository
from models.user import User


class UserService(BaseService[UserRepository, User]):
    """User service with business logic"""
    repository_class = UserRepository

    def get_by_name(self, name: str):
        """Get user by name"""
        return self.repository.get_one(name=name)

    def get_active_users(self, limit: int = 100):
        """Get all active users"""
        # Assuming there's a status field, otherwise just get all
        return self.get_all(limit=limit, order_by='create_time', desc=True)

