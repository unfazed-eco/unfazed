import typing as t

from redis.asyncio import Redis
from redis.asyncio.connection import parse_url
from unfazed.schema import RedisOptions


class DefaultBackend:
    """A full-featured Redis cache backend implementation.

    This class provides a high-level interface to interact with Redis, supporting
    all standard Redis commands and additional features like key prefixing and
    connection management.

    Key Features:
        - Automatic key prefixing
        - Connection pooling
        - SSL/TLS support
        - Retry mechanism
        - Health check monitoring
        - Async context manager support

    Example:
        ```python
        from unfazed.cache import caches

        # Get the default cache backend
        cache = caches["default"]

        # Set a value with prefix
        await cache.set(cache.make_key("user:1"), {"name": "John"})

        # Get a value
        user = await cache.get(cache.make_key("user:1"))

        # Use as context manager
        async with cache:
            await cache.set("key", "value")
        ```

    Note:
        Since Redis doesn't natively support key prefixes, this class handles
        prefixing manually through the `make_key` method. Always use `make_key`
        when setting or getting values to ensure proper key prefixing.

    Args:
        location (str): Redis connection URL (e.g., 'redis://localhost:6379/0')
        options (Dict[str, Any], optional): Additional Redis configuration options.
            See `RedisOptions` for available options.
    """

    def __init__(self, location: str, options: t.Dict[str, t.Any] | None = None):
        """Initialize the Redis backend with connection details and options.

        Args:
            location (str): Redis connection URL
            options (Dict[str, Any], optional): Redis configuration options
        """
        kw = parse_url(location)
        if options is None:
            options = {}

        options_model = RedisOptions(**options)
        retry_cls = options_model.retry or None

        self.prefix = options_model.prefix or ""

        self.client = Redis(
            host=kw.get("host", "localhost"),
            port=kw.get("port", 6379),
            db=kw.get("db", 0),
            password=kw.get("password", None),
            username=kw.get("username"),
            retry=retry_cls,
            socket_timeout=options_model.socket_timeout,
            socket_connect_timeout=options_model.socket_connect_timeout,
            socket_keepalive=options_model.socket_keepalive,
            socket_keepalive_options=options_model.socket_keepalive_options,
            decode_responses=options_model.decode_responses,
            retry_on_timeout=options_model.retry_on_timeout,
            retry_on_error=options_model.retry_on_error,
            max_connections=options_model.max_connections,
            single_connection_client=options_model.single_connection_client,
            health_check_interval=options_model.health_check_interval,
            ssl=options_model.ssl,
            ssl_keyfile=options_model.ssl_keyfile,
            ssl_certfile=options_model.ssl_certfile,
            ssl_cert_reqs=options_model.ssl_cert_reqs,
            ssl_ca_certs=options_model.ssl_ca_certs,
            ssl_ca_data=options_model.ssl_ca_data,
            ssl_check_hostname=options_model.ssl_check_hostname,
            ssl_min_version=options_model.ssl_min_version,
            ssl_ciphers=options_model.ssl_ciphers,
        )

    async def __aenter__(self) -> t.Self:
        """Enter the async context manager.

        Returns:
            Self: The current instance
        """
        return self

    async def __aexit__(self, *args: t.Any, **kw: t.Any) -> None:
        """Exit the async context manager and close the connection.

        Args:
            *args: Exception information if an exception was raised
            **kw: Additional keyword arguments
        """
        await self.client.aclose()

    async def close(self) -> None:
        """Close the Redis connection.

        This method is provided for compatibility with the cache backend protocol.
        It's recommended to use the context manager (`async with`) instead.
        """
        return await self.client.aclose()

    def make_key(self, key: str) -> str:
        """Add the configured prefix to a key.

        This method ensures that all keys are properly prefixed according to the
        configuration. If no prefix is configured, the original key is returned.

        Args:
            key (str): The original key without prefix

        Returns:
            str: The key with prefix if configured, otherwise the original key

        Example:
            ```python
            cache = DefaultBackend("redis://localhost", {"prefix": "myapp"})
            prefixed_key = cache.make_key("user:1")  # Returns "myapp:user:1"
            ```
        """
        if not self.prefix:
            return key
        return f"{self.prefix}:{key}"

    def __getattr__(self, name: str) -> t.Any:
        """Proxy Redis client methods.

        This method allows direct access to all Redis client methods through
        the DefaultBackend instance. It automatically handles method delegation
        to the underlying Redis client.

        Args:
            name (str): The name of the Redis command/method to call

        Returns:
            Any: The method from the Redis client

        Raises:
            AttributeError: If the requested method is not found in the Redis client

        Note:
            All standard Redis commands are supported. For a complete list of
            available commands, refer to the Redis documentation:
            https://redis.io/commands
        """
        if not hasattr(self.client, name):
            raise AttributeError(f"Attribute {name} not found in Redis client")
        return getattr(self.client, name)
