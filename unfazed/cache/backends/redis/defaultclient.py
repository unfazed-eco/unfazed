import typing as t

from redis.asyncio import Redis
from redis.asyncio.connection import parse_url
from redis.asyncio.retry import Retry
from redis.backoff import ConstantBackoff
from unfazed.protocol import CacheBackend as CacheBackendProtocol
from unfazed.schema import RedisOptions
from unfazed.utils import import_string


class AsyncDefaultBackend(CacheBackendProtocol):
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

        if options_model.serializer:
            serializer = import_string(options_model.serializer)()
        else:
            serializer = None
        self.serializer = serializer

        if options_model.compressor:
            compressor = import_string(options_model.compressor)()
        else:
            compressor = None
        self.compressor = compressor

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

    async def close(self) -> None:
        # for compatibility with cache backend protocol
        return await self.client.aclose()

    def make_key(self, key: str) -> str:
        if not self.prefix:
            return key
        return f"{self.prefix}:{key}"

    def encode(self, value: t.Any) -> t.Union[int, float, bytes]:
        if isinstance(value, (int, float)):
            return value

        if self.serializer:
            value = self.serializer.dumps(value)

        if self.compressor:
            value = self.compressor.compress(value)

        return value

    def decode(self, value: bytes):
        value = value.decode()
        if isinstance(value, (int, float)):
            return value
        if self.compressor:
            value = self.compressor.decompress(value)

        if self.serializer:
            value = self.serializer.loads(value)

        return value

    # redis commands

    async def get(self, name: str):
        key = self.make_key(name)
        value = await self.client.get(key)

        return self.decode(value)

    async def set(self, name: str, value: t.Any, *args, **kw):
        key = self.make_key(name)
        value = self.encode(value)
        await self.client.set(key, value, *args, **kw)
