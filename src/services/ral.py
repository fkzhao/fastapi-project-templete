"""
Ral Service Class with Dependency Injection
Automatically injects repository instances into services.
"""
import logging
from typing import Type, TypeVar, Generic, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Type variable for repositories
R = TypeVar('R')


class RalService(Generic[R]):
    """
    Ral service class with automatic repository injection.

    Usage:
        class UserService(RalService[UserRepository]):
            repository_class = UserRepository

            def get_user_info(self, user_id: int):
                return self.repository.get_user(user_id)
    """

    # Repository class to inject (override in subclass)
    repository_class: Optional[Type[R]] = None

    # Repository instance cache
    _repository_cache: Dict[str, Any] = {}

    def __init__(self, repository: Optional[R] = None, **kwargs):
        """
        Initialize service with optional repository injection.

        Args:
            repository: Optional pre-configured repository instance
            **kwargs: Additional repository initialization arguments
        """
        if repository is not None:
            # Use provided repository instance
            self._repository = repository
            logger.debug(f"{self.__class__.__name__}: Using provided repository")
        elif self.repository_class is not None:
            # Auto-create repository instance
            cache_key = self._get_cache_key()

            # Check cache first
            if cache_key in self._repository_cache:
                self._repository = self._repository_cache[cache_key]
                logger.debug(f"{self.__class__.__name__}: Using cached repository")
            else:
                # Create new repository instance
                self._repository = self._create_repository(**kwargs)
                self._repository_cache[cache_key] = self._repository
                logger.debug(f"{self.__class__.__name__}: Created new repository instance")
        else:
            self._repository = None
            logger.warning(f"{self.__class__.__name__}: No repository configured")

    def _get_cache_key(self) -> str:
        """Get cache key for repository instance"""
        return f"{self.__class__.__name__}_{self.repository_class.__name__}"

    def _create_repository(self, **kwargs) -> R:
        """
        Create repository instance.

        Args:
            **kwargs: Repository initialization arguments

        Returns:
            Repository instance
        """
        if self.repository_class is None:
            raise ValueError(f"{self.__class__.__name__}: repository_class not set")

        return self.repository_class(**kwargs)

    @property
    def repository(self) -> R:
        """
        Get repository instance.

        Returns:
            Repository instance

        Raises:
            ValueError: If repository is not configured
        """
        if self._repository is None:
            raise ValueError(
                f"{self.__class__.__name__}: Repository not initialized. "
                "Set repository_class or provide repository in __init__"
            )
        return self._repository

    def set_repository(self, repository: R) -> None:
        """
        Set repository instance manually.

        Args:
            repository: Repository instance
        """
        self._repository = repository
        logger.debug(f"{self.__class__.__name__}: Repository set manually")

    def close(self) -> None:
        """Close service and cleanup resources"""
        if self._repository and hasattr(self._repository, 'close'):
            self._repository.close()
            logger.debug(f"{self.__class__.__name__}: Repository closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    @classmethod
    def clear_cache(cls) -> None:
        """Clear repository cache"""
        cls._repository_cache.clear()
        logger.info("Repository cache cleared")


class MultiRepositoryService:
    """
    Ral service class that can inject multiple repositories.

    Usage:
        class UserManagementService(MultiRepositoryService):
            def __init__(self):
                super().__init__()
                self.user_repo = self.inject(UserRepository)
                self.auth_repo = self.inject(AuthRepository)
    """

    _repository_cache: Dict[str, Any] = {}

    def __init__(self):
        """Initialize multi-repository service"""
        self._repositories: Dict[str, Any] = {}
        logger.debug(f"{self.__class__.__name__}: Initialized")

    def inject(self, repository_class: Type[R], cache: bool = True, **kwargs) -> R:
        """
        Inject repository instance.

        Args:
            repository_class: Repository class to inject
            cache: Whether to cache the instance
            **kwargs: Repository initialization arguments

        Returns:
            Repository instance
        """
        repo_name = repository_class.__name__

        # Check cache
        if cache and repo_name in self._repository_cache:
            instance = self._repository_cache[repo_name]
            logger.debug(f"{self.__class__.__name__}: Using cached {repo_name}")
            return instance

        # Create new instance
        instance = repository_class(**kwargs)

        # Cache if requested
        if cache:
            self._repository_cache[repo_name] = instance
            logger.debug(f"{self.__class__.__name__}: Created and cached {repo_name}")
        else:
            logger.debug(f"{self.__class__.__name__}: Created {repo_name} (no cache)")

        # Store reference
        self._repositories[repo_name] = instance

        return instance

    def close(self) -> None:
        """Close all repositories"""
        # Close repositories stored in this instance
        for name, repo in self._repositories.items():
            if hasattr(repo, 'close'):
                repo.close()
                logger.debug(f"{self.__class__.__name__}: Closed {name}")

        # Also close cached repositories (if we want to fully cleanup)
        # Note: This will affect other service instances using the same cache
        # Uncomment if you want to clear cached repositories on close
        # for name, repo in list(self._repository_cache.items()):
        #     if hasattr(repo, 'close'):
        #         repo.close()
        #         logs.debug(f"{self.__class__.__name__}: Closed cached {name}")

        self._repositories.clear()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    @classmethod
    def clear_cache(cls) -> None:
        """Clear repository cache"""
        cls._repository_cache.clear()
        logger.info("Multi-repository cache cleared")

