"""
Redis Service
High-level service for Redis operations with automatic repository injection.
"""
import logging
from typing import Any, Optional, List, Dict

from services.base import BaseService
from repositories.redis import RedisRepository, RedisException

logger = logging.getLogger(__name__)


class RedisService(BaseService[RedisRepository]):
    """
    Redis service with high-level operations.
    Automatically injects RedisRepository.
    """

    repository_class = RedisRepository

    def __init__(self, repository: Optional[RedisRepository] = None, **kwargs):
        """
        Initialize Redis service.

        Args:
            repository: Optional pre-configured RedisRepository instance
            **kwargs: Additional repository initialization arguments
        """
        super().__init__(repository=repository, **kwargs)
        logger.info("RedisService initialized")

    def health_check(self) -> Dict[str, Any]:
        """
        Check Redis health.

        Returns:
            Dictionary with health status and info
        """
        try:
            ping_result = self.repository.ping()
            info = self.repository.info("server")

            return {
                "status": "healthy",
                "ping": ping_result,
                "redis_version": info.get("redis_version"),
                "uptime_in_seconds": info.get("uptime_in_seconds"),
                "mode": self.repository.mode
            }
        except RedisException as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "mode": self.repository.mode
            }

    # Cache operations
    def cache_set(
            self,
            key: str,
            value: Any,
            ttl: Optional[int] = None
    ) -> bool:
        """
        Set cache value with optional TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default: use default_ttl)

        Returns:
            True if successful
        """
        try:
            return self.repository.set(key, value, ttl=ttl)
        except RedisException as e:
            logger.error(f"Failed to set cache for key '{key}': {e}")
            return False

    def cache_get(self, key: str, default: Any = None) -> Any:
        """
        Get cached value.

        Args:
            key: Cache key
            default: Default value if not found

        Returns:
            Cached value or default
        """
        try:
            return self.repository.get(key, default=default)
        except RedisException as e:
            logger.error(f"Failed to get cache for key '{key}': {e}")
            return default

    def cache_delete(self, *keys: str) -> int:
        """
        Delete cached values.

        Args:
            *keys: Cache keys to delete

        Returns:
            Number of keys deleted
        """
        try:
            return self.repository.delete(*keys)
        except RedisException as e:
            logger.error(f"Failed to delete cache: {e}")
            return 0

    def cache_exists(self, *keys: str) -> int:
        """
        Check if cache keys exist.

        Args:
            *keys: Cache keys to check

        Returns:
            Number of keys that exist
        """
        try:
            return self.repository.exists(*keys)
        except RedisException as e:
            logger.error(f"Failed to check cache existence: {e}")
            return 0

    def cache_clear(self, pattern: str = "*") -> int:
        """
        Clear cache by pattern.

        Args:
            pattern: Key pattern to match (default: "*" for all)

        Returns:
            Number of keys deleted
        """
        try:
            keys = self.repository.keys(pattern)
            if keys:
                return self.repository.delete(*keys)
            return 0
        except RedisException as e:
            logger.error(f"Failed to clear cache: {e}")
            return 0

    # Counter operations
    def increment_counter(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """
        Increment counter.

        Args:
            key: Counter key
            amount: Amount to increment (default: 1)
            ttl: Optional TTL in seconds

        Returns:
            New counter value
        """
        try:
            value = self.repository.incr(key, amount)
            if ttl is not None and ttl > 0:
                self.repository.expire(key, ttl)
            return value
        except RedisException as e:
            logger.error(f"Failed to increment counter '{key}': {e}")
            raise

    def decrement_counter(self, key: str, amount: int = 1) -> int:
        """
        Decrement counter.

        Args:
            key: Counter key
            amount: Amount to decrement (default: 1)

        Returns:
            New counter value
        """
        try:
            return self.repository.decr(key, amount)
        except RedisException as e:
            logger.error(f"Failed to decrement counter '{key}': {e}")
            raise

    def get_counter(self, key: str) -> int:
        """
        Get counter value.

        Args:
            key: Counter key

        Returns:
            Counter value (0 if not found)
        """
        try:
            value = self.repository.get(key, default=0)
            return int(value) if value is not None else 0
        except (RedisException, ValueError) as e:
            logger.error(f"Failed to get counter '{key}': {e}")
            return 0

    # Hash operations
    def hash_set(self, name: str, key: str, value: Any) -> int:
        """
        Set hash field.

        Args:
            name: Hash name
            key: Field key
            value: Field value

        Returns:
            Number of fields added
        """
        try:
            return self.repository.hset(name, key, value)
        except RedisException as e:
            logger.error(f"Failed to set hash field '{name}.{key}': {e}")
            raise

    def hash_get(self, name: str, key: str, default: Any = None) -> Any:
        """
        Get hash field.

        Args:
            name: Hash name
            key: Field key
            default: Default value if not found

        Returns:
            Field value or default
        """
        try:
            return self.repository.hget(name, key, default=default)
        except RedisException as e:
            logger.error(f"Failed to get hash field '{name}.{key}': {e}")
            return default

    def hash_get_all(self, name: str) -> Dict[str, Any]:
        """
        Get all hash fields.

        Args:
            name: Hash name

        Returns:
            Dictionary of all fields
        """
        try:
            return self.repository.hgetall(name)
        except RedisException as e:
            logger.error(f"Failed to get all hash fields '{name}': {e}")
            return {}

    def hash_delete(self, name: str, *keys: str) -> int:
        """
        Delete hash fields.

        Args:
            name: Hash name
            *keys: Field keys to delete

        Returns:
            Number of fields deleted
        """
        try:
            return self.repository.hdel(name, *keys)
        except RedisException as e:
            logger.error(f"Failed to delete hash fields '{name}': {e}")
            return 0

    # List operations
    def list_push(self, key: str, *values: Any, left: bool = True) -> int:
        """
        Push values to list.

        Args:
            key: List key
            *values: Values to push
            left: Push to left/head (True) or right/tail (False)

        Returns:
            Length of list after push
        """
        try:
            if left:
                return self.repository.lpush(key, *values)
            else:
                return self.repository.rpush(key, *values)
        except RedisException as e:
            logger.error(f"Failed to push to list '{key}': {e}")
            raise

    def list_pop(self, key: str, left: bool = True, default: Any = None) -> Any:
        """
        Pop value from list.

        Args:
            key: List key
            left: Pop from left/head (True) or right/tail (False)
            default: Default value if list empty

        Returns:
            Popped value or default
        """
        try:
            if left:
                return self.repository.lpop(key, default=default)
            else:
                return self.repository.rpop(key, default=default)
        except RedisException as e:
            logger.error(f"Failed to pop from list '{key}': {e}")
            return default

    def list_range(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """
        Get range of values from list.

        Args:
            key: List key
            start: Start index (default: 0)
            end: End index (default: -1 for end of list)

        Returns:
            List of values
        """
        try:
            return self.repository.lrange(key, start, end)
        except RedisException as e:
            logger.error(f"Failed to get list range '{key}': {e}")
            return []

    # Set operations
    def set_add(self, key: str, *members: Any) -> int:
        """
        Add members to set.

        Args:
            key: Set key
            *members: Members to add

        Returns:
            Number of members added
        """
        try:
            return self.repository.sadd(key, *members)
        except RedisException as e:
            logger.error(f"Failed to add to set '{key}': {e}")
            raise

    def set_members(self, key: str) -> set:
        """
        Get all members of set.

        Args:
            key: Set key

        Returns:
            Set of members
        """
        try:
            return self.repository.smembers(key)
        except RedisException as e:
            logger.error(f"Failed to get set members '{key}': {e}")
            return set()

    def set_remove(self, key: str, *members: Any) -> int:
        """
        Remove members from set.

        Args:
            key: Set key
            *members: Members to remove

        Returns:
            Number of members removed
        """
        try:
            return self.repository.srem(key, *members)
        except RedisException as e:
            logger.error(f"Failed to remove from set '{key}': {e}")
            return 0

    # Session management
    def create_session(self, session_id: str, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """
        Create session.

        Args:
            session_id: Session ID
            data: Session data
            ttl: Time-to-live in seconds (default: 3600)

        Returns:
            True if successful
        """
        try:
            session_key = f"session:{session_id}"
            return self.repository.set(session_key, data, ttl=ttl)
        except RedisException as e:
            logger.error(f"Failed to create session '{session_id}': {e}")
            return False

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.

        Args:
            session_id: Session ID

        Returns:
            Session data or None if not found
        """
        try:
            session_key = f"session:{session_id}"
            return self.repository.get(session_key)
        except RedisException as e:
            logger.error(f"Failed to get session '{session_id}': {e}")
            return None

    def update_session(self, session_id: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Update session data.

        Args:
            session_id: Session ID
            data: Updated session data
            ttl: Optional new TTL in seconds

        Returns:
            True if successful
        """
        try:
            session_key = f"session:{session_id}"
            return self.repository.set(session_key, data, ttl=ttl)
        except RedisException as e:
            logger.error(f"Failed to update session '{session_id}': {e}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session.

        Args:
            session_id: Session ID

        Returns:
            True if successful
        """
        try:
            session_key = f"session:{session_id}"
            return self.repository.delete(session_key) > 0
        except RedisException as e:
            logger.error(f"Failed to delete session '{session_id}': {e}")
            return False

    def extend_session(self, session_id: str, ttl: int) -> bool:
        """
        Extend session TTL.

        Args:
            session_id: Session ID
            ttl: New TTL in seconds

        Returns:
            True if successful
        """
        try:
            session_key = f"session:{session_id}"
            return self.repository.expire(session_key, ttl)
        except RedisException as e:
            logger.error(f"Failed to extend session '{session_id}': {e}")
            return False

    # Rate limiting
    def check_rate_limit(
            self,
            key: str,
            max_requests: int,
            window_seconds: int
    ) -> Dict[str, Any]:
        """
        Check rate limit for a key.

        Args:
            key: Rate limit key (e.g., user ID, IP address)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Dictionary with rate limit status:
            {
                "allowed": bool,
                "current": int (current request count),
                "limit": int (max requests),
                "remaining": int (remaining requests),
                "reset_in": int (seconds until reset)
            }
        """
        try:
            rate_key = f"rate_limit:{key}"
            current = self.increment_counter(rate_key, amount=1, ttl=window_seconds)
            ttl = self.repository.ttl(rate_key)

            allowed = current <= max_requests
            remaining = max(0, max_requests - current)

            return {
                "allowed": allowed,
                "current": current,
                "limit": max_requests,
                "remaining": remaining,
                "reset_in": ttl if ttl > 0 else window_seconds
            }
        except RedisException as e:
            logger.error(f"Failed to check rate limit for '{key}': {e}")
            # On error, allow the request
            return {
                "allowed": True,
                "current": 0,
                "limit": max_requests,
                "remaining": max_requests,
                "reset_in": window_seconds,
                "error": str(e)
            }

    def reset_rate_limit(self, key: str) -> bool:
        """
        Reset rate limit for a key.

        Args:
            key: Rate limit key

        Returns:
            True if successful
        """
        try:
            rate_key = f"rate_limit:{key}"
            return self.repository.delete(rate_key) > 0
        except RedisException as e:
            logger.error(f"Failed to reset rate limit for '{key}': {e}")
            return False

    # Utility methods
    def get_keys(self, pattern: str = "*") -> List[str]:
        """
        Get keys matching pattern.

        Args:
            pattern: Key pattern (default: "*" for all keys)

        Returns:
            List of matching keys
        """
        try:
            return self.repository.keys(pattern)
        except RedisException as e:
            logger.error(f"Failed to get keys: {e}")
            return []

    def get_ttl(self, key: str) -> int:
        """
        Get TTL for a key.

        Args:
            key: Key name

        Returns:
            TTL in seconds (-1 if no expiration, -2 if key doesn't exist)
        """
        try:
            return self.repository.ttl(key)
        except RedisException as e:
            logger.error(f"Failed to get TTL for '{key}': {e}")
            return -2

    def set_ttl(self, key: str, ttl: int) -> bool:
        """
        Set TTL for a key.

        Args:
            key: Key name
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        try:
            return self.repository.expire(key, ttl)
        except RedisException as e:
            logger.error(f"Failed to set TTL for '{key}': {e}")
            return False