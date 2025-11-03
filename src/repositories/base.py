"""
Base Repository Class
Provides common database CRUD operations for SQLAlchemy models.
"""
import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from core.database import get_engine
from models.base import BaseModel

logger = logging.getLogger(__name__)

# Type variable for model classes
ModelType = TypeVar("ModelType", bound=BaseModel)


class RepositoryException(Exception):
    """Base exception for repository operations"""
    pass


class RecordNotFoundException(RepositoryException):
    """Record not found exception"""
    pass


class DuplicateRecordException(RepositoryException):
    """Duplicate record exception"""
    pass


class DatabaseOperationException(RepositoryException):
    """Database operation failed exception"""
    pass


class BaseRepository(Generic[ModelType]):
    """
    Base repository class with database CRUD capabilities.
    Provides common database operations for SQLAlchemy models.

    Example:
        class UserRepository(BaseRepository[User]):
            model = User

        # Usage
        user_repo = UserRepository()
        user = user_repo.get_by_id(1)
        users = user_repo.get_all(limit=10)
    """

    # Model class (must be set in subclass)
    model: Type[ModelType]

    def __init__(
        self,
        db_name: str = "default",
        session: Optional[Session] = None
    ):
        """
        Initialize base repository.

        Args:
            db_name: Database name (default: "default")
            session: Optional SQLAlchemy session (if not provided, will create new session)
        """
        self.db_name = db_name
        self.engine = get_engine(db_name)
        self._external_session = session

        if not hasattr(self, 'model') or self.model is None:
            raise ValueError(f"{self.__class__.__name__} must define a 'model' attribute")

    def _get_session(self) -> Session:
        """Get database session"""
        if self._external_session:
            return self._external_session
        return Session(self.engine)

    def _execute_with_session(self, func, *args, **kwargs):
        """Execute function with session management"""
        if self._external_session:
            # Use external session (caller manages transaction)
            return func(self._external_session, *args, **kwargs)
        else:
            # Create and manage own session
            session = Session(self.engine)
            try:
                result = func(session, *args, **kwargs)
                session.commit()
                return result
            except Exception as e:
                session.rollback()
                raise
            finally:
                session.close()

    def create(self, obj_in: Union[Dict[str, Any], ModelType]) -> ModelType:
        """
        Create a new record.

        Args:
            obj_in: Dictionary or model instance with data

        Returns:
            Created model instance

        Raises:
            DuplicateRecordException: If record already exists
            DatabaseOperationException: If database operation fails
        """
        def _create(session: Session, data: Union[Dict[str, Any], ModelType]) -> ModelType:
            try:
                if isinstance(data, dict):
                    db_obj = self.model(**data)
                else:
                    db_obj = data

                session.add(db_obj)
                session.flush()
                session.refresh(db_obj)

                logger.info(f"Created {self.model.__name__}: {db_obj}")
                return db_obj

            except IntegrityError as e:
                logger.error(f"Duplicate record in {self.model.__name__}: {str(e)}")
                raise DuplicateRecordException(f"Record already exists: {str(e)}") from e
            except SQLAlchemyError as e:
                logger.error(f"Database error creating {self.model.__name__}: {str(e)}")
                raise DatabaseOperationException(f"Failed to create record: {str(e)}") from e

        return self._execute_with_session(_create, obj_in)

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Get record by ID.

        Args:
            id: Primary key value

        Returns:
            Model instance or None if not found
        """
        session = self._get_session()
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = session.execute(stmt).scalar_one_or_none()
            logger.debug(f"Get {self.model.__name__} by id={id}: {'Found' if result else 'Not found'}")
            return result
        finally:
            if not self._external_session:
                session.close()

    def get_by_ids(self, ids: List[Any]) -> List[ModelType]:
        """
        Get records by multiple IDs.

        Args:
            ids: List of primary key values

        Returns:
            List of model instances
        """
        session = self._get_session()
        try:
            stmt = select(self.model).where(self.model.id.in_(ids))
            result = session.execute(stmt).scalars().all()
            logger.debug(f"Get {self.model.__name__} by ids={ids}: Found {len(result)} records")
            return list(result)
        finally:
            if not self._external_session:
                session.close()

    def get_one(self, **filters) -> Optional[ModelType]:
        """
        Get single record by filters.

        Args:
            **filters: Filter conditions (field=value)

        Returns:
            Model instance or None if not found
        """
        session = self._get_session()
        try:
            stmt = select(self.model)
            for key, value in filters.items():
                if hasattr(self.model, key):
                    stmt = stmt.where(getattr(self.model, key) == value)

            result = session.execute(stmt).scalar_one_or_none()
            logger.debug(f"Get one {self.model.__name__} with filters={filters}: {'Found' if result else 'Not found'}")
            return result
        finally:
            if not self._external_session:
                session.close()

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
        session = self._get_session()
        try:
            stmt = select(self.model)

            # Apply filters
            for key, value in filters.items():
                if hasattr(self.model, key):
                    stmt = stmt.where(getattr(self.model, key) == value)

            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                order_column = getattr(self.model, order_by)
                stmt = stmt.order_by(order_column.desc() if desc else order_column)

            # Apply pagination
            stmt = stmt.offset(skip).limit(limit)

            result = session.execute(stmt).scalars().all()
            logger.debug(f"Get all {self.model.__name__}: Found {len(result)} records")
            return list(result)
        finally:
            if not self._external_session:
                session.close()

    def count(self, **filters) -> int:
        """
        Count records matching filters.

        Args:
            **filters: Filter conditions (field=value)

        Returns:
            Number of matching records
        """
        session = self._get_session()
        try:
            stmt = select(func.count()).select_from(self.model)

            # Apply filters
            for key, value in filters.items():
                if hasattr(self.model, key):
                    stmt = stmt.where(getattr(self.model, key) == value)

            result = session.execute(stmt).scalar()
            logger.debug(f"Count {self.model.__name__} with filters={filters}: {result}")
            return result or 0
        finally:
            if not self._external_session:
                session.close()

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

        Raises:
            RecordNotFoundException: If record not found
            DatabaseOperationException: If database operation fails
        """
        def _update(session: Session, record_id: Any, data: Union[Dict[str, Any], ModelType]) -> ModelType:
            try:
                # Get existing record
                db_obj = session.get(self.model, record_id)
                if not db_obj:
                    raise RecordNotFoundException(f"{self.model.__name__} with id={record_id} not found")

                # Update fields
                if isinstance(data, dict):
                    for field, value in data.items():
                        if hasattr(db_obj, field):
                            setattr(db_obj, field, value)
                else:
                    for field in data.__dict__:
                        if not field.startswith('_') and hasattr(db_obj, field):
                            setattr(db_obj, field, getattr(data, field))

                session.flush()
                session.refresh(db_obj)

                logger.info(f"Updated {self.model.__name__}: {db_obj}")
                return db_obj

            except RecordNotFoundException:
                raise
            except SQLAlchemyError as e:
                logger.error(f"Database error updating {self.model.__name__}: {str(e)}")
                raise DatabaseOperationException(f"Failed to update record: {str(e)}") from e

        return self._execute_with_session(_update, id, obj_in)

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

        Raises:
            DatabaseOperationException: If database operation fails
        """
        def _update_by_filters(session: Session, data: Dict[str, Any], filter_conditions: Dict[str, Any]) -> int:
            try:
                stmt = update(self.model)

                # Apply filters
                for key, value in filter_conditions.items():
                    if hasattr(self.model, key):
                        stmt = stmt.where(getattr(self.model, key) == value)

                # Apply updates
                stmt = stmt.values(**data)

                result = session.execute(stmt)
                count = result.rowcount

                logger.info(f"Updated {count} {self.model.__name__} records with filters={filter_conditions}")
                return count

            except SQLAlchemyError as e:
                logger.error(f"Database error bulk updating {self.model.__name__}: {str(e)}")
                raise DatabaseOperationException(f"Failed to bulk update records: {str(e)}") from e

        return self._execute_with_session(_update_by_filters, update_data, filters)

    def delete(self, id: Any) -> bool:
        """
        Delete a record by ID.

        Args:
            id: Primary key value

        Returns:
            True if deleted, False if not found

        Raises:
            DatabaseOperationException: If database operation fails
        """
        def _delete(session: Session, record_id: Any) -> bool:
            try:
                db_obj = session.get(self.model, record_id)
                if not db_obj:
                    logger.warning(f"{self.model.__name__} with id={record_id} not found for deletion")
                    return False

                session.delete(db_obj)
                logger.info(f"Deleted {self.model.__name__} with id={record_id}")
                return True

            except SQLAlchemyError as e:
                logger.error(f"Database error deleting {self.model.__name__}: {str(e)}")
                raise DatabaseOperationException(f"Failed to delete record: {str(e)}") from e

        return self._execute_with_session(_delete, id)

    def delete_by_filters(self, **filters) -> int:
        """
        Delete multiple records matching filters.

        Args:
            **filters: Filter conditions (field=value)

        Returns:
            Number of deleted records

        Raises:
            DatabaseOperationException: If database operation fails
        """
        def _delete_by_filters(session: Session, filter_conditions: Dict[str, Any]) -> int:
            try:
                stmt = delete(self.model)

                # Apply filters
                for key, value in filter_conditions.items():
                    if hasattr(self.model, key):
                        stmt = stmt.where(getattr(self.model, key) == value)

                result = session.execute(stmt)
                count = result.rowcount

                logger.info(f"Deleted {count} {self.model.__name__} records with filters={filter_conditions}")
                return count

            except SQLAlchemyError as e:
                logger.error(f"Database error bulk deleting {self.model.__name__}: {str(e)}")
                raise DatabaseOperationException(f"Failed to bulk delete records: {str(e)}") from e

        return self._execute_with_session(_delete_by_filters, filters)

    def exists(self, **filters) -> bool:
        """
        Check if record exists matching filters.

        Args:
            **filters: Filter conditions (field=value)

        Returns:
            True if exists, False otherwise
        """
        return self.count(**filters) > 0

    def bulk_create(self, objects: List[Union[Dict[str, Any], ModelType]]) -> List[ModelType]:
        """
        Create multiple records in bulk.

        Args:
            objects: List of dictionaries or model instances

        Returns:
            List of created model instances

        Raises:
            DatabaseOperationException: If database operation fails
        """
        def _bulk_create(session: Session, data_list: List[Union[Dict[str, Any], ModelType]]) -> List[ModelType]:
            try:
                db_objs = []
                for data in data_list:
                    if isinstance(data, dict):
                        db_obj = self.model(**data)
                    else:
                        db_obj = data
                    db_objs.append(db_obj)

                session.add_all(db_objs)
                session.flush()

                for db_obj in db_objs:
                    session.refresh(db_obj)

                logger.info(f"Bulk created {len(db_objs)} {self.model.__name__} records")
                return db_objs

            except SQLAlchemyError as e:
                logger.error(f"Database error bulk creating {self.model.__name__}: {str(e)}")
                raise DatabaseOperationException(f"Failed to bulk create records: {str(e)}") from e

        return self._execute_with_session(_bulk_create, objects)

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
        def _get_or_create(
            session: Session,
            default_values: Optional[Dict[str, Any]],
            filter_conditions: Dict[str, Any]
        ) -> tuple[ModelType, bool]:
            try:
                # Try to get existing record
                stmt = select(self.model)
                for key, value in filter_conditions.items():
                    if hasattr(self.model, key):
                        stmt = stmt.where(getattr(self.model, key) == value)

                db_obj = session.execute(stmt).scalar_one_or_none()

                if db_obj:
                    logger.debug(f"Found existing {self.model.__name__} with filters={filter_conditions}")
                    return db_obj, False

                # Create new record
                create_data = {**(default_values or {}), **filter_conditions}
                db_obj = self.model(**create_data)
                session.add(db_obj)
                session.flush()
                session.refresh(db_obj)

                logger.info(f"Created new {self.model.__name__} with filters={filter_conditions}")
                return db_obj, True

            except SQLAlchemyError as e:
                logger.error(f"Database error in get_or_create {self.model.__name__}: {str(e)}")
                raise DatabaseOperationException(f"Failed to get or create record: {str(e)}") from e

        return self._execute_with_session(_get_or_create, defaults, filters)

