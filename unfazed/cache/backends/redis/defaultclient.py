import typing as t

from redis.asyncio import Redis
from redis.asyncio.connection import parse_url
from redis.asyncio.retry import Retry
from redis.backoff import ConstantBackoff
from unfazed.schema import RedisOptions


class DefaultBackend:
    """
    Full featured Redis cache backend

    due to redis not support prefix, so we need to handle it manually
    call `make_key` to add prefix to key

    Usage:

    ```python

    from unfazed.cache import caches

    default: DefaultBackend = caches["default"]

    await default.set(default.make_key("key"), "value")

    ret = await default.get(default.make_key("key"))

    ```

    """

    def __init__(self, location: str, options: t.Dict[str, t.Any] | None = None):
        kw = parse_url(location)
        if options is None:
            options = {}

        options_model = RedisOptions(**options)
        if options_model.retry:
            retry_cls = Retry(ConstantBackoff(0.5), 1)
        else:
            retry_cls = None

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
        return self

    async def __aexit__(self, *args: t.Any, **kw: t.Any) -> None:
        await self.client.aclose()

    async def close(self) -> None:
        # for compatibility with cache backend protocol
        return await self.client.aclose()

    def make_key(self, key: str) -> str:
        if not self.prefix:
            return key
        return f"{self.prefix}:{key}"

    def __getattr__(self, name: str) -> t.Any:
        """
        DefaultBackend will call any method of Redis client though this method

        Get all methods of Redis client, refer:
        https://redis-py.readthedocs.io/en/stable/commands.html

        Usage:

        ```python

        default: DefaultBackend = caches["default"]

        await default.set("key", "value")
        await default.get("key")

        ```
        """
        if not hasattr(self.client, name):
            raise AttributeError(f"Attribute {name} not found in Redis client")
        return getattr(self.client, name)
