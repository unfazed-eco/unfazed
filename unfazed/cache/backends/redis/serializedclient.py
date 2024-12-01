import typing as t
from datetime import datetime

from redis.asyncio import Redis
from redis.asyncio.connection import parse_url
from redis.asyncio.retry import Retry
from redis.backoff import ConstantBackoff
from unfazed.protocol import CacheBackend as CacheBackendProtocol
from unfazed.schema import RedisOptions
from unfazed.utils import import_string


class SerializerBackend(CacheBackendProtocol):
    """
    Redis backend with serializer and compressor

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
            if not serializer:
                raise ValueError(
                    f"Serializer is required for compressor: {options_model.compressor}"
                )
            compressor = import_string(options_model.compressor)()
        else:
            compressor = None
        self.compressor = compressor

        self.prefix = options_model.prefix or ""

        if options_model.decode_responses:
            raise ValueError(
                "SerializerBackend does not support decode_responses = True"
            )

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

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.client.aclose()

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

    def decode(self, value: bytes | str) -> bytes | str | int | float | None:
        if value is None:
            return value

        try:
            value_str = value.decode("utf-8")

            if value_str.isdigit():
                return int(value_str)
            try:
                return float(value_str)
            except ValueError:
                pass
        except UnicodeDecodeError:
            pass

        if self.compressor:
            value = self.compressor.decompress(value)

        if self.serializer:
            value = self.serializer.loads(value)

        return value

    # general commands
    async def flushdb(self, asynchronous: bool = False, **kw) -> t.Any:
        await self.client.flushdb(asynchronous, **kw)

    async def exists(self, name: str) -> int:
        key = self.make_key(name)
        return await self.client.exists(key)

    async def expire(
        self,
        name: str,
        time: int,
        nx: bool = False,
        xx: bool = False,
        gt: bool = False,
        lt: bool = False,
    ) -> t.Any:
        key = self.make_key(name)
        return await self.client.expire(key, time, nx, xx, gt, lt)

    async def touch(self, *args) -> int:
        args = [self.make_key(key) for key in args]
        return await self.client.touch(*args)

    async def ttl(self, name: str):
        key = self.make_key(name)
        return await self.client.ttl(key)

    # string commands with serializer and compressor
    # int and float are not influenced

    # ========  string commands using serializer and compressor  ========

    async def get(self, name: str) -> t.Any:
        key = self.make_key(name)
        value = await self.client.get(key)
        return self.decode(value)

    async def getdel(self, name: str) -> t.Any:
        key = self.make_key(name)
        value = await self.client.getdel(key)
        return self.decode(value)

    async def getex(
        self,
        name: str,
        *,
        ex: int | None = None,
        px: int | None = None,
        exat: int | datetime | None = None,
        pxat: int | datetime | None = None,
        persist: bool = False,
    ) -> t.Any:
        key = self.make_key(name)
        value = await self.client.getex(key, ex, px, exat, pxat, persist)
        return self.decode(value)

    async def getset(self, name: str, value: t.Any) -> t.Any:
        key = self.make_key(name)
        new_value = self.encode(value)
        value = await self.client.getset(key, new_value)
        return self.decode(value)

    async def mget(self, keys: t.List[str], *args) -> t.List:
        keys = [self.make_key(key) for key in keys]
        values = await self.client.mget(keys, *args)
        return [self.decode(value) for value in values]

    async def mset(self, mapping: t.Dict[str, t.Any]) -> str:
        mapping = {
            self.make_key(key): self.encode(value) for key, value in mapping.items()
        }
        return await self.client.mset(mapping)

    async def msetnx(self, mapping: t.Dict[str, t.Any]) -> bool:
        mapping = {
            self.make_key(key): self.encode(value) for key, value in mapping.items()
        }
        return await self.client.msetnx(mapping)

    async def set(
        self,
        name: str,
        value: t.Any,
        ex: int | None = None,
        px: int | None = None,
        nx: bool = False,
        xx: bool = False,
        keepttl: bool = False,
        get: bool = False,
        exat: int | datetime | None = None,
        pxat: int | datetime | None = None,
    ):
        key = self.make_key(name)
        value = self.encode(value)
        await self.client.set(key, value, ex, px, nx, xx, keepttl, get, exat, pxat)

    async def setex(self, name: str, time: int, value: t.Any) -> str:
        key = self.make_key(name)
        value = self.encode(value)
        return await self.client.setex(key, time, value)

    async def setnx(self, name: str, value: t.Any) -> bool:
        key = self.make_key(name)
        value = self.encode(value)
        return await self.client.setnx(key, value)

    async def psetex(self, name: str, time: int, value: t.Any) -> str:
        key = self.make_key(name)
        value = self.encode(value)
        return await self.client.psetex(key, time, value)

    # ==== int and float are
    # not influenced ====
    async def decr(self, name: str, amount: int = 1) -> int:
        key = self.make_key(name)
        return await self.client.decr(key, amount)

    async def decrby(self, name: str, amount: int = 1) -> int:
        key = self.make_key(name)
        return await self.client.decrby(key, amount)

    async def incr(self, name: str, amount: int = 1) -> int:
        key = self.make_key(name)
        return await self.client.incr(key, amount)

    async def incrby(self, name: str, amount: int = 1) -> int:
        key = self.make_key(name)
        return await self.client.incrby(key, amount)

    async def incrbyfloat(self, name: str, amount: float = 1.0) -> float:
        key = self.make_key(name)
        return await self.client.incrbyfloat(key, amount)
