import typing as t

from redis.asyncio import Redis
from redis.asyncio.connection import parse_url
from redis.asyncio.retry import Retry
from redis.backoff import ConstantBackoff
from unfazed.protocol import CacheBackend as CacheBackendProtocol
from unfazed.schema import RedisOptions


class AsyncDefaultBackend(Redis, CacheBackendProtocol):
    """
    Usage:
        CACHE = {
            "default": {
                "BACKEND": "unfazed.cache.backends.redis.AsyncDefaultBackend",
                "LOCATION": "redis://localhost:6379",
                "OPTIONS": {
                    "retry": True,
                    "max_connections": 10,
                    "health_check_interval": 30
                },
            }
        }

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

        super().__init__(
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

    async def close(self) -> None:
        # for compatibility with cache backend protocol
        return await self.aclose()
