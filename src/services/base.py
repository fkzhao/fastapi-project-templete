"""
Base Service Class
Provides common business logic layer for services that interact with repositories.
"""
import logging
from typing import Type, TypeVar, Generic, List, Optional, Any, Dict, Union
from sqlalchemy.orm import Session

from repositories.base import BaseRepository, ModelType

logger = logging.getLogger(__name__)

# Type variable for repositories
RepositoryType = TypeVar('RepositoryType', bound=BaseRepository)


class BaseService(Generic[RepositoryType, ModelType]):
    """
    Base service class with automatic repository injection.
    Provides common service operations that delegate to repository.

    Example:
        class UserService(BaseService[UserRepository, User]):
            repository_class = UserRepository

            def get_active_users(self):
                return self.repository.get_all(status='active')

        # Usage
        user_service = UserService()
        users = user_service.get_all(limit=10)
        user = user_service.get_by_id(1)
    """

    # Repository class to inject (must be set in subclass)
    repository_class: Optional[Type[RepositoryType]] = None

    def __init__(
        self,
        repository: Optional[RepositoryType] = None,
        db_name: str = "default",
        session: Optional[Session] = None
    ):
        """
        Initialize service with optional repository injection.

        Args:
            repository: Optional pre-configured repository instance
            db_name: Database name (default: "default")
            session: Optional SQLAlchemy session for transaction management
        """
        if repository is not None:
            # Use provided repository instance
            self.repository = repository
            logger.debug(f"{self.__class__.__name__}: Using provided repository")
        elif self.repository_class is not None:
            # Auto-create repository instance
            self.repository = self.repository_class(db_name=db_name, session=session)
            logger.debug(f"{self.__class__.__name__}: Created repository instance")
        else:
            raise ValueError(
                f"{self.__class__.__name__} must either provide a repository instance "
                f"or set repository_class attribute"
            )

        self.db_name = db_name
        self._session = session

    # ==================== Common CRUD Operations ====================

    def create(self, obj_in: Union[Dict[str, Any], ModelType]) -> ModelType:
        """
        Create a new record.

        Args:
            obj_in: Dictionary or model instance with data

        Returns:
            Created model instance
        """
        logger.info(f"{self.__class__.__name__}: Creating record")
        return self.repository.create(obj_in)

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Get record by ID.

        Args:
            id: Primary key value

        Returns:
            Model instance or None if not found
        """
        logger.debug(f"{self.__class__.__name__}: Getting record by id={id}")
        return self.repository.get_by_id(id)

    def get_by_ids(self, ids: List[Any]) -> List[ModelType]:
        """
        Get records by multiple IDs.

        Args:
            ids: List of primary key values

        Returns:
            List of model instances
        """
        logger.debug(f"{self.__class__.__name__}: Getting records by ids={ids}")
        return self.repository.get_by_ids(ids)

    def get_one(self, **filters) -> Optional[ModelType]:
        """
        Get single record by filters.

        Args:
            **filters: Filter conditions (field=value)

        Returns:
            Model instance or None if not found
        """
        logger.debug(f"{self.__class__.__name__}: Getting one record with filters={filters}")
        return self.repository.get_one(**filters)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        desc: bool = False,
        **filters
    ) -> List[ModelType]:
        """
        Get all records with optional filtering and pagination.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            order_by: Field name to order by
            desc: If True, order in descending order
            **filters: Filter conditions (field=value)

        Returns:
            List of model instances
        """
        logger.debug(
            f"{self.__class__.__name__}: Getting all records "
            f"(skip={skip}, limit={limit}, filters={filters})"
        )
        return self.repository.get_all(
            skip=skip,
            limit=limit,
            order_by=order_by,
            desc=desc,
            **filters
        )

    def count(self, **filters) -> int:
        """
        Count records matching filters.

        Args:
            **filters: Filter conditions (field=value)

        Returns:
            Number of matching records
        """
        logger.debug(f"{self.__class__.__name__}: Counting records with filters={filters}")
        return self.repository.count(**filters)

    def update(
        self,
        id: Any,
        obj_in: Union[Dict[str, Any], ModelType]
    ) -> Optional[ModelType]:
        """
        Update a record by ID.

        Args:
            id: Primary key value
            obj_in: Dictionary or model instance with update data

        Returns:
            Updated model instance or None if not found
        """
        logger.info(f"{self.__class__.__name__}: Updating record id={id}")
        return self.repository.update(id, obj_in)

    def update_by_filters(
        self,
        update_data: Dict[str, Any],
        **filters
    ) -> int:
        """
        Update multiple records matching filters.

        Args:
            update_data: Dictionary with fields to update
            **filters: Filter conditions (field=value)

        Returns:
            Number of updated records
        """
        logger.info(
            f"{self.__class__.__name__}: Bulk updating records "
            f"with filters={filters}, data={update_data}"
        )
        return self.repository.update_by_filters(update_data, **filters)

    def delete(self, id: Any) -> bool:
        """
        Delete a record by ID.

        Args:
            id: Primary key value

        Returns:
            True if deleted, False if not found
        """
        logger.info(f"{self.__class__.__name__}: Deleting record id={id}")
        return self.repository.delete(id)

    def delete_by_filters(self, **filters) -> int:
        """
        Delete multiple records matching filters.

        Args:
            **filters: Filter conditions (field=value)

        Returns:
            Number of deleted records
        """
        logger.info(f"{self.__class__.__name__}: Bulk deleting records with filters={filters}")
        return self.repository.delete_by_filters(**filters)

    def exists(self, **filters) -> bool:
        """
        Check if record exists matching filters.

        Args:
            **filters: Filter conditions (field=value)

        Returns:
            True if exists, False otherwise
        """
        logger.debug(f"{self.__class__.__name__}: Checking existence with filters={filters}")
        return self.repository.exists(**filters)

    def bulk_create(self, objects: List[Union[Dict[str, Any], ModelType]]) -> List[ModelType]:
        """
        Create multiple records in bulk.

        Args:
            objects: List of dictionaries or model instances

        Returns:
            List of created model instances
        """
        logger.info(f"{self.__class__.__name__}: Bulk creating {len(objects)} records")
        return self.repository.bulk_create(objects)

    def get_or_create(
        self,
        defaults: Optional[Dict[str, Any]] = None,
        **filters
    ) -> tuple[ModelType, bool]:
        """
        Get record or create if not exists.

        Args:
            defaults: Default values for creation if record doesn't exist
            **filters: Filter conditions to find record

        Returns:
            Tuple of (model instance, created: bool)
        """
        logger.debug(f"{self.__class__.__name__}: Get or create with filters={filters}")
        return self.repository.get_or_create(defaults, **filters)

    # ==================== Pagination Helper ====================

    def paginate(
        self,
        page: int = 1,
        page_size: int = 20,
        order_by: Optional[str] = None,
        desc: bool = False,
        **filters
    ) -> Dict[str, Any]:
        """
        Get paginated results with metadata.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            order_by: Field name to order by
            desc: If True, order in descending order
            **filters: Filter conditions (field=value)

        Returns:
            Dictionary with:
                - items: List of model instances
                - total: Total number of records
                - page: Current page number
                - page_size: Items per page
                - total_pages: Total number of pages
        """
        skip = (page - 1) * page_size
        items = self.get_all(
            skip=skip,
            limit=page_size,
            order_by=order_by,
            desc=desc,
            **filters
        )
        total = self.count(**filters)
        total_pages = (total + page_size - 1) // page_size  # Ceiling division

        logger.debug(
            f"{self.__class__.__name__}: Paginated results "
            f"(page={page}, page_size={page_size}, total={total})"
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

