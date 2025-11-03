"""
Redis Repository
Provides Redis operations with support for standalone and cluster modes.
"""
import logging
import json
from typing import Any, Optional, Union, List, Dict
import ssl

import redis
from redis.cluster import RedisCluster
from redis.exceptions import (
    RedisError,
    ConnectionError,
    TimeoutError,
    ResponseError
)

from settings import settings

logger = logging.getLogger(__name__)


class RedisException(Exception):
    """Base exception for Redis operations"""
    pass


class RedisConnectionException(RedisException):
    """Redis connection exception"""
    pass


class RedisOperationException(RedisException):
    """Redis operation exception"""
    pass


class RedisRepository:
    """
    Redis repository with support for standalone and cluster modes.
    Provides common Redis operations with error handling and automatic serialization.
    """

    def __init__(
            self,
            mode: Optional[str] = None,
            host: Optional[str] = None,
            port: Optional[int] = None,
            password: Optional[str] = None,
            db: Optional[int] = None,
            cluster_nodes: Optional[str] = None,
            max_connections: Optional[int] = None,
            socket_timeout: Optional[int] = None,
            socket_connect_timeout: Optional[int] = None,
            decode_responses: Optional[bool] = None,
            ssl_enabled: Optional[bool] = None,
            ssl_cert_reqs: Optional[str] = None,
            key_prefix: Optional[str] = None,
            default_ttl: Optional[int] = None
    ):
        """
        Initialize Redis repository.

        Args:
            mode: Redis mode - "standalone" or "cluster" (default: from settings)
            host: Redis host for standalone mode (default: from settings)
            port: Redis port for standalone mode (default: from settings)
            password: Redis password (default: from settings)
            db: Redis database number for standalone mode (default: from settings)
            cluster_nodes: Comma-separated cluster nodes "host1:port1,host2:port2" (default: from settings)
            max_connections: Maximum connections in pool (default: from settings)
            socket_timeout: Socket timeout in seconds (default: from settings)
            socket_connect_timeout: Socket connect timeout in seconds (default: from settings)
            decode_responses: Automatically decode responses to strings (default: from settings)
            ssl_enabled: Enable SSL/TLS (default: from settings)
            ssl_cert_reqs: SSL certificate requirements (default: from settings)
            key_prefix: Prefix for all keys (default: from settings)
            default_ttl: Default TTL in seconds (default: from settings)
        """
        # Load configuration from settings or parameters
        self.mode = mode or settings.redis_mode
        self.host = host or settings.redis_host
        self.port = port or settings.redis_port
        self.password = password or settings.redis_password
        self.db = db if db is not None else settings.redis_db
        self.cluster_nodes = cluster_nodes or settings.redis_cluster_nodes
        self.max_connections = max_connections or settings.redis_max_connections
        self.socket_timeout = socket_timeout or settings.redis_socket_timeout
        self.socket_connect_timeout = socket_connect_timeout or settings.redis_socket_connect_timeout
        self.decode_responses = decode_responses if decode_responses is not None else settings.redis_decode_responses
        self.ssl_enabled = ssl_enabled if ssl_enabled is not None else settings.redis_ssl
        self.ssl_cert_reqs = ssl_cert_reqs or settings.redis_ssl_cert_reqs
        self.key_prefix = key_prefix or settings.redis_key_prefix
        self.default_ttl = default_ttl or settings.redis_default_ttl

        # Initialize Redis client
        self._client: Optional[Union[redis.Redis, RedisCluster]] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Redis client based on mode"""
        try:
            if self.mode == "cluster":
                self._client = self._create_cluster_client()
                logger.info("Redis cluster client initialized successfully")
            else:
                self._client = self._create_standalone_client()
                logger.info("Redis standalone client initialized successfully")

            # Test connection
            self._client.ping()
            logger.info(f"Redis connection test successful (mode: {self.mode})")

        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            raise RedisConnectionException(f"Failed to connect to Redis: {e}")

    def _create_standalone_client(self) -> redis.Redis:
        """Create Redis standalone client"""
        ssl_config = {}
        if self.ssl_enabled:
            ssl_config = {
                'ssl': True,
                'ssl_cert_reqs': getattr(ssl, f'CERT_{self.ssl_cert_reqs.upper()}', ssl.CERT_REQUIRED)
            }

        return redis.Redis(
            host=self.host,
            port=self.port,
            password=self.password if self.password else None,
            db=self.db,
            max_connections=self.max_connections,
            socket_timeout=self.socket_timeout,
            socket_connect_timeout=self.socket_connect_timeout,
            decode_responses=self.decode_responses,
            **ssl_config
        )

    def _create_cluster_client(self) -> RedisCluster:
        """Create Redis cluster client"""
        if not self.cluster_nodes:
            raise RedisConnectionException("REDIS_CLUSTER_NODES must be set for cluster mode")

        # Parse cluster nodes
        startup_nodes = []
        for node in self.cluster_nodes.split(','):
            node = node.strip()
            if ':' in node:
                host, port = node.split(':')
                startup_nodes.append({"host": host.strip(), "port": int(port.strip())})

        if not startup_nodes:
            raise RedisConnectionException("No valid cluster nodes found")

        ssl_config = {}
        if self.ssl_enabled:
            ssl_config = {
                'ssl': True,
                'ssl_cert_reqs': getattr(ssl, f'CERT_{self.ssl_cert_reqs.upper()}', ssl.CERT_REQUIRED)
            }

        return RedisCluster(
            startup_nodes=startup_nodes,
            password=self.password if self.password else None,
            max_connections=self.max_connections,
            socket_timeout=self.socket_timeout,
            socket_connect_timeout=self.socket_connect_timeout,
            decode_responses=self.decode_responses,
            **ssl_config
        )

    def _get_key(self, key: str) -> str:
        """Get key with prefix"""
        return f"{self.key_prefix}:{key}"

    @property
    def client(self) -> Union[redis.Redis, RedisCluster]:
        """Get Redis client"""
        if self._client is None:
            raise RedisConnectionException("Redis client not initialized")
        return self._client

    def ping(self) -> bool:
        """
        Ping Redis server.

        Returns:
            True if ping successful

        Raises:
            RedisOperationException: If ping fails
        """
        try:
            return self.client.ping()
        except RedisError as e:
            logger.error(f"Redis ping failed: {e}")
            raise RedisOperationException(f"Redis ping failed: {e}")

    def set(
            self,
            key: str,
            value: Any,
            ttl: Optional[int] = None,
            nx: bool = False,
            xx: bool = False
    ) -> bool:
        """
        Set a key-value pair.

        Args:
            key: Key name
            value: Value (will be JSON-serialized if not string)
            ttl: Time-to-live in seconds (default: use default_ttl)
            nx: Only set if key does not exist
            xx: Only set if key exists

        Returns:
            True if set successful

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            # Serialize value if not string
            if not isinstance(value, (str, bytes)):
                value = json.dumps(value)

            ttl = ttl if ttl is not None else self.default_ttl
            full_key = self._get_key(key)

            result = self.client.set(
                full_key,
                value,
                ex=ttl if ttl > 0 else None,
                nx=nx,
                xx=xx
            )
            return bool(result)
        except RedisError as e:
            logger.error(f"Redis SET failed for key '{key}': {e}")
            raise RedisOperationException(f"Redis SET failed: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value by key.

        Args:
            key: Key name
            default: Default value if key not found

        Returns:
            Value (JSON-deserialized if possible) or default

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_key = self._get_key(key)
            value = self.client.get(full_key)

            if value is None:
                return default

            # Try to deserialize JSON
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value

            return value
        except RedisError as e:
            logger.error(f"Redis GET failed for key '{key}': {e}")
            raise RedisOperationException(f"Redis GET failed: {e}")

    def delete(self, *keys: str) -> int:
        """
        Delete one or more keys.

        Args:
            *keys: Key names to delete

        Returns:
            Number of keys deleted

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_keys = [self._get_key(key) for key in keys]
            return self.client.delete(*full_keys)
        except RedisError as e:
            logger.error(f"Redis DELETE failed: {e}")
            raise RedisOperationException(f"Redis DELETE failed: {e}")

    def exists(self, *keys: str) -> int:
        """
        Check if keys exist.

        Args:
            *keys: Key names to check

        Returns:
            Number of keys that exist

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_keys = [self._get_key(key) for key in keys]
            return self.client.exists(*full_keys)
        except RedisError as e:
            logger.error(f"Redis EXISTS failed: {e}")
            raise RedisOperationException(f"Redis EXISTS failed: {e}")

    def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time for a key.

        Args:
            key: Key name
            ttl: Time-to-live in seconds

        Returns:
            True if expiration was set

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_key = self._get_key(key)
            return bool(self.client.expire(full_key, ttl))
        except RedisError as e:
            logger.error(f"Redis EXPIRE failed for key '{key}': {e}")
            raise RedisOperationException(f"Redis EXPIRE failed: {e}")

    def ttl(self, key: str) -> int:
        """
        Get time-to-live for a key.

        Args:
            key: Key name

        Returns:
            TTL in seconds (-1 if no expiration, -2 if key doesn't exist)

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_key = self._get_key(key)
            return self.client.ttl(full_key)
        except RedisError as e:
            logger.error(f"Redis TTL failed for key '{key}': {e}")
            raise RedisOperationException(f"Redis TTL failed: {e}")

    def incr(self, key: str, amount: int = 1) -> int:
        """
        Increment value by amount.

        Args:
            key: Key name
            amount: Amount to increment (default: 1)

        Returns:
            New value after increment

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_key = self._get_key(key)
            return self.client.incr(full_key, amount)
        except RedisError as e:
            logger.error(f"Redis INCR failed for key '{key}': {e}")
            raise RedisOperationException(f"Redis INCR failed: {e}")

    def decr(self, key: str, amount: int = 1) -> int:
        """
        Decrement value by amount.

        Args:
            key: Key name
            amount: Amount to decrement (default: 1)

        Returns:
            New value after decrement

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_key = self._get_key(key)
            return self.client.decr(full_key, amount)
        except RedisError as e:
            logger.error(f"Redis DECR failed for key '{key}': {e}")
            raise RedisOperationException(f"Redis DECR failed: {e}")

    def hset(self, name: str, key: str, value: Any) -> int:
        """
        Set field in hash.

        Args:
            name: Hash name
            key: Field key
            value: Field value (will be JSON-serialized if not string)

        Returns:
            Number of fields added

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            if not isinstance(value, (str, bytes)):
                value = json.dumps(value)

            full_name = self._get_key(name)
            return self.client.hset(full_name, key, value)
        except RedisError as e:
            logger.error(f"Redis HSET failed for hash '{name}', key '{key}': {e}")
            raise RedisOperationException(f"Redis HSET failed: {e}")

    def hget(self, name: str, key: str, default: Any = None) -> Any:
        """
        Get field from hash.

        Args:
            name: Hash name
            key: Field key
            default: Default value if field not found

        Returns:
            Field value (JSON-deserialized if possible) or default

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_name = self._get_key(name)
            value = self.client.hget(full_name, key)

            if value is None:
                return default

            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value

            return value
        except RedisError as e:
            logger.error(f"Redis HGET failed for hash '{name}', key '{key}': {e}")
            raise RedisOperationException(f"Redis HGET failed: {e}")

    def hgetall(self, name: str) -> Dict[str, Any]:
        """
        Get all fields from hash.

        Args:
            name: Hash name

        Returns:
            Dictionary of all fields (values JSON-deserialized if possible)

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_name = self._get_key(name)
            data = self.client.hgetall(full_name)

            # Try to deserialize JSON values
            result = {}
            for k, v in data.items():
                if isinstance(v, str):
                    try:
                        result[k] = json.loads(v)
                    except json.JSONDecodeError:
                        result[k] = v
                else:
                    result[k] = v

            return result
        except RedisError as e:
            logger.error(f"Redis HGETALL failed for hash '{name}': {e}")
            raise RedisOperationException(f"Redis HGETALL failed: {e}")

    def hdel(self, name: str, *keys: str) -> int:
        """
        Delete fields from hash.

        Args:
            name: Hash name
            *keys: Field keys to delete

        Returns:
            Number of fields deleted

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_name = self._get_key(name)
            return self.client.hdel(full_name, *keys)
        except RedisError as e:
            logger.error(f"Redis HDEL failed for hash '{name}': {e}")
            raise RedisOperationException(f"Redis HDEL failed: {e}")

    def lpush(self, key: str, *values: Any) -> int:
        """
        Push values to head of list.

        Args:
            key: List key
            *values: Values to push (will be JSON-serialized if not string)

        Returns:
            Length of list after push

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            serialized = [
                json.dumps(v) if not isinstance(v, (str, bytes)) else v
                for v in values
            ]
            full_key = self._get_key(key)
            return self.client.lpush(full_key, *serialized)
        except RedisError as e:
            logger.error(f"Redis LPUSH failed for key '{key}': {e}")
            raise RedisOperationException(f"Redis LPUSH failed: {e}")

    def rpush(self, key: str, *values: Any) -> int:
        """
        Push values to tail of list.

        Args:
            key: List key
            *values: Values to push (will be JSON-serialized if not string)

        Returns:
            Length of list after push

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            serialized = [
                json.dumps(v) if not isinstance(v, (str, bytes)) else v
                for v in values
            ]
            full_key = self._get_key(key)
            return self.client.rpush(full_key, *serialized)
        except RedisError as e:
            logger.error(f"Redis RPUSH failed for key '{key}': {e}")
            raise RedisOperationException(f"Redis RPUSH failed: {e}")

    def lpop(self, key: str, default: Any = None) -> Any:
        """
        Pop value from head of list.

        Args:
            key: List key
            default: Default value if list empty

        Returns:
            Popped value (JSON-deserialized if possible) or default

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_key = self._get_key(key)
            value = self.client.lpop(full_key)

            if value is None:
                return default

            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value

            return value
        except RedisError as e:
            logger.error(f"Redis LPOP failed for key '{key}': {e}")
            raise RedisOperationException(f"Redis LPOP failed: {e}")

    def rpop(self, key: str, default: Any = None) -> Any:
        """
        Pop value from tail of list.

        Args:
            key: List key
            default: Default value if list empty

        Returns:
            Popped value (JSON-deserialized if possible) or default

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_key = self._get_key(key)
            value = self.client.rpop(full_key)

            if value is None:
                return default

            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value

            return value
        except RedisError as e:
            logger.error(f"Redis RPOP failed for key '{key}': {e}")
            raise RedisOperationException(f"Redis RPOP failed: {e}")

    def lrange(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """
        Get range of values from list.

        Args:
            key: List key
            start: Start index (default: 0)
            end: End index (default: -1 for end of list)

        Returns:
            List of values (JSON-deserialized if possible)

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_key = self._get_key(key)
            values = self.client.lrange(full_key, start, end)

            result = []
            for v in values:
                if isinstance(v, str):
                    try:
                        result.append(json.loads(v))
                    except json.JSONDecodeError:
                        result.append(v)
                else:
                    result.append(v)

            return result
        except RedisError as e:
            logger.error(f"Redis LRANGE failed for key '{key}': {e}")
            raise RedisOperationException(f"Redis LRANGE failed: {e}")

    def sadd(self, key: str, *members: Any) -> int:
        """
        Add members to set.

        Args:
            key: Set key
            *members: Members to add (will be JSON-serialized if not string)

        Returns:
            Number of members added

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            serialized = [
                json.dumps(m) if not isinstance(m, (str, bytes)) else m
                for m in members
            ]
            full_key = self._get_key(key)
            return self.client.sadd(full_key, *serialized)
        except RedisError as e:
            logger.error(f"Redis SADD failed for key '{key}': {e}")
            raise RedisOperationException(f"Redis SADD failed: {e}")

    def smembers(self, key: str) -> set:
        """
        Get all members of set.

        Args:
            key: Set key

        Returns:
            Set of members (JSON-deserialized if possible)

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_key = self._get_key(key)
            members = self.client.smembers(full_key)

            result = set()
            for m in members:
                if isinstance(m, str):
                    try:
                        result.add(json.loads(m))
                    except json.JSONDecodeError:
                        result.add(m)
                else:
                    result.add(m)

            return result
        except RedisError as e:
            logger.error(f"Redis SMEMBERS failed for key '{key}': {e}")
            raise RedisOperationException(f"Redis SMEMBERS failed: {e}")

    def srem(self, key: str, *members: Any) -> int:
        """
        Remove members from set.

        Args:
            key: Set key
            *members: Members to remove (will be JSON-serialized if not string)

        Returns:
            Number of members removed

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            serialized = [
                json.dumps(m) if not isinstance(m, (str, bytes)) else m
                for m in members
            ]
            full_key = self._get_key(key)
            return self.client.srem(full_key, *serialized)
        except RedisError as e:
            logger.error(f"Redis SREM failed for key '{key}': {e}")
            raise RedisOperationException(f"Redis SREM failed: {e}")

    def keys(self, pattern: str = "*") -> List[str]:
        """
        Get keys matching pattern.

        Args:
            pattern: Key pattern (default: "*" for all keys)

        Returns:
            List of matching keys (with prefix removed)

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            full_pattern = self._get_key(pattern)
            keys = self.client.keys(full_pattern)

            # Remove prefix from keys
            prefix_len = len(self.key_prefix)
            return [k[prefix_len:] if k.startswith(self.key_prefix) else k for k in keys]
        except RedisError as e:
            logger.error(f"Redis KEYS failed for pattern '{pattern}': {e}")
            raise RedisOperationException(f"Redis KEYS failed: {e}")

    def flushdb(self) -> bool:
        """
        Delete all keys in current database.

        Returns:
            True if successful

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            return bool(self.client.flushdb())
        except RedisError as e:
            logger.error(f"Redis FLUSHDB failed: {e}")
            raise RedisOperationException(f"Redis FLUSHDB failed: {e}")

    def info(self, section: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Redis server information.

        Args:
            section: Info section to retrieve (default: all)

        Returns:
            Server information dictionary

        Raises:
            RedisOperationException: If operation fails
        """
        try:
            return self.client.info(section)
        except RedisError as e:
            logger.error(f"Redis INFO failed: {e}")
            raise RedisOperationException(f"Redis INFO failed: {e}")

    def close(self) -> None:
        """Close Redis connection"""
        if self._client:
            try:
                self._client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

