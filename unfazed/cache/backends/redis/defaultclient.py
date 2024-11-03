import typing as t
from datetime import datetime

from redis.asyncio import Redis
from redis.asyncio.connection import parse_url
from redis.asyncio.retry import Retry
from redis.backoff import ConstantBackoff
from unfazed.protocol import CacheBackend as CacheBackendProtocol
from unfazed.schema import RedisOptions
from unfazed.utils import import_string


class AsyncDefaultBackend(CacheBackendProtocol):
    """
    Redis cache backend

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

        have_sp_client = False
        # serializer and compressor are not compatible with decode_responses == True
        # unfazed will init ave two clients, one for raw data, one for serialized and compressed data
        if options_model.decode_responses:
            if serializer:
                self.sp_client = Redis(
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
                    decode_responses=False,
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
                have_sp_client = True
            else:
                self.sp_client = self.client
        else:
            self.sp_client = self.client

        self.have_sp_client = have_sp_client

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.client.close()

    async def close(self) -> None:
        # for compatibility with cache backend protocol
        return await self.client.aclose()

    def make_key(self, key: str) -> str:
        if not self.prefix:
            return key
        return f"{self.prefix}:{key}"

    def encode(self, value: t.Any) -> t.Union[int, float, bytes]:
        if not self.have_sp_client:
            return value

        if isinstance(value, (int, float)):
            return value

        if self.serializer:
            value = self.serializer.dumps(value)

        if self.compressor:
            value = self.compressor.compress(value)

        return value

    def decode(self, value: bytes | str) -> bytes | int | float:
        if not self.have_sp_client:
            return value

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

    async def ping(self, **kw) -> t.Any:
        return await self.client.ping(**kw)

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

    # string commands
    # unfazed split string commands into two parts
    # raw string commands and string commands using serializer and compressor
    # int and float are not influenced

    # =======   raw string commands  =======
    async def append(self, name: str, value: str) -> t.Any:
        """
        Warning:
            use this method with raw_set and raw_get
        """
        key = self.make_key(name)
        return await self.client.append(key, value)

    async def getrange(self, name: str, start: int, end: int) -> t.Any:
        """
        Warning:
            use this method with raw_set and raw_get
        """
        key = self.make_key(name)
        return await self.client.getrange(key, start, end)

    async def setrange(self, name: str, offset: int, value: str) -> int:
        """
        Warning:
            use this method with raw_set and raw_get
        """
        key = self.make_key(name)
        return await self.client.setrange(key, offset, value)

    async def strlen(self, name: str) -> int:
        """
        Warning:
            use this method with raw_set and raw_get
        """
        key = self.make_key(name)
        return await self.client.strlen(key)

    async def substr(self, name: str, start: int, end: int) -> str:
        """
        Warning:
            use this method with raw_set and raw_get
        """
        key = self.make_key(name)
        return await self.client.substr(key, start, end)

    # unfazed provides raw_get and raw_set for users to use redis commands directly
    # if some other commands like getset/getdel are needed
    # PR is welcome
    async def raw_get(self, name: str) -> t.Any:
        key = self.make_key(name)
        return await self.client.get(key)

    async def raw_set(self, name: str, value: t.Any, *args, **kw):
        key = self.make_key(name)
        await self.client.set(key, value, *args, **kw)

    # ========  string commands using serializer and compressor  ========

    async def get(self, name: str) -> t.Any:
        key = self.make_key(name)
        value = await self.sp_client.get(key)
        return self.decode(value)

    async def getdel(self, name: str) -> t.Any:
        key = self.make_key(name)
        value = await self.sp_client.getdel(key)
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
        value = await self.sp_client.getex(key, ex, px, exat, pxat, persist)
        return self.decode(value)

    async def getset(self, name: str, value: t.Any) -> t.Any:
        key = self.make_key(name)
        new_value = self.encode(value)
        value = await self.sp_client.getset(key, new_value)
        return self.decode(value)

    async def mget(self, keys: t.List[str], *args) -> t.List:
        keys = [self.make_key(key) for key in keys]
        values = await self.sp_client.mget(keys, *args)
        return [self.decode(value) for value in values]

    async def mset(self, mapping: t.Dict[str, t.Any]) -> str:
        mapping = {
            self.make_key(key): self.encode(value) for key, value in mapping.items()
        }
        return await self.sp_client.mset(mapping)

    async def msetnx(self, mapping: t.Dict[str, t.Any]) -> bool:
        mapping = {
            self.make_key(key): self.encode(value) for key, value in mapping.items()
        }
        return await self.sp_client.msetnx(mapping)

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
        await self.sp_client.set(key, value, ex, px, nx, xx, keepttl, get, exat, pxat)

    async def setex(self, name: str, time: int, value: t.Any) -> str:
        key = self.make_key(name)
        value = self.encode(value)
        return await self.sp_client.setex(key, time, value)

    async def setnx(self, name: str, value: t.Any) -> bool:
        key = self.make_key(name)
        value = self.encode(value)
        return await self.sp_client.setnx(key, value)

    async def psetex(self, name: str, time: int, value: t.Any) -> str:
        key = self.make_key(name)
        value = self.encode(value)
        return await self.sp_client.psetex(key, time, value)

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

    # hash commands
    async def hget(self, name: str, key: str):
        name = self.make_key(name)
        return await self.client.hget(name, key)

    async def hdel(self, name: str, key: str):
        name = self.make_key(name)
        return await self.client.hdel(name, key)

    async def hexists(self, name: str, key: str) -> bool:
        name = self.make_key(name)
        return await self.client.hexists(name, key)

    async def hexpire(self, name: str, key: str, time: int):
        name = self.make_key(name)
        return await self.client.hexpire(name, key, time)

    async def hexpireat(self, name: str, time: int, *args, **kw):
        name = self.make_key(name)
        return await self.client.hexpireat(name, time, *args, **kw)

    async def hexpiretime(self, name: str, key: str):
        name = self.make_key(name)
        return await self.client.hexpiretime(name, key)

    async def hgetall(self, name: str) -> t.Dict:
        name = self.make_key(name)
        return await self.client.hgetall(name)

    async def hincrby(self, name: str, key: str, amount: int = 1) -> int:
        name = self.make_key(name)
        return await self.client.hincrby(name, key, amount)

    async def hincrbyfloat(self, name: str, key: str, amount: float = 1.0) -> float:
        name = self.make_key(name)
        return await self.client.hincrbyfloat(name, key, amount)

    async def hkeys(self, name: str) -> t.List[str]:
        name = self.make_key(name)
        return await self.client.hkeys(name)

    async def hlen(self, name: str) -> int:
        name = self.make_key(name)
        return await self.client.hlen(name)

    async def hmget(self, name: str, keys: t.List[str], *args) -> t.List:
        name = self.make_key(name)
        return await self.client.hmget(name, keys, *args)

    async def hmset(self, name: str, mapping: t.Dict[str, t.Any]) -> str:
        name = self.make_key(name)
        return await self.client.hmset(name, mapping)

    async def hpersist(self, name: str) -> int:
        name = self.make_key(name)
        return await self.client.hpersist(name)

    async def hpexpire(self, name: str, time: int, *args, **kw) -> t.Any:
        name = self.make_key(name)
        return await self.client.hpexpire(name, time, *args, **kw)

    async def hpexpireat(self, name: str, time: int, *args, **kw) -> t.Any:
        name = self.make_key(name)
        return await self.client.hpexpireat(name, time, *args, **kw)

    async def hpexpiretime(self, key: str, *args) -> t.Any:
        name = self.make_key(key)
        return await self.client.hpexpiretime(name, *args)

    async def hpttl(self, key: str) -> t.Any:
        name = self.make_key(key)
        return await self.client.hpttl(name)

    async def hrandfield(
        self, key: str, count: int = 1, withvalues: bool = True
    ) -> t.Any:
        name = self.make_key(key)
        return await self.client.hrandfield(name, count, withvalues)

    async def hscan(
        self,
        key: str,
        cursor: int = 0,
        match: str = "*",
        count: int = 10,
        no_values: bool | None = None,
    ) -> t.Any:
        name = self.make_key(key)
        return await self.client.hscan(name, cursor, match, count, no_values)

    async def hset(
        self,
        name: str,
        key: str | None = None,
        value: str | None = None,
        mapping: t.Dict | None = None,
        items: t.List | None = None,
    ) -> int:
        name = self.make_key(name)
        return await self.client.hset(name, key, value, mapping, items)

    async def hsetnx(self, name: str, key: str, value: str) -> bool:
        name = self.make_key(name)
        return await self.client.hsetnx(name, key, value)

    async def hstrlen(self, name: str, key: str) -> int:
        name = self.make_key(name)
        return await self.client.hstrlen(name, key)

    async def httl(self, name: str, key: str) -> t.Any:
        name = self.make_key(name)
        return await self.client.httl(name, key)

    async def hvals(self, name: str) -> t.List[str]:
        name = self.make_key(name)
        return await self.client.hvals(name)

    # list commands
    async def blmove(
        self,
        first_list: str,
        second_list: str,
        timeout: int,
        src: str,
        dest: str,
    ) -> t.Any:
        return await self.client.blmove(first_list, second_list, timeout, src, dest)

    async def blmpop(
        self,
        timeout: float,
        numkeys: float,
        *args: t.List[str],
        derection: str,
        count: int | None = 1,
    ) -> t.Any:
        return await self.client.blmpop(timeout, numkeys, *args, derection, count=count)

    async def blpop(self, keys: t.List[str], timeout: int | None = 0) -> t.List:
        return await self.client.blpop(keys, timeout)

    async def brpop(self, keys: t.List[str], timeout: int | None = 0) -> t.List:
        return await self.client.brpop(keys, timeout)

    async def brpoplpush(self, src: str, dest: str, timeout: int) -> t.Optional[str]:
        src = self.make_key(src)
        dest = self.make_key(dest)

        return await self.client.brpoplpush(src, dest, timeout)

    async def lindex(self, name: str, index: int) -> t.Optional[str]:
        name = self.make_key(name)
        return await self.client.lindex(name, index)

    async def linsert(self, name: str, where: str, refvalue: str, value: str) -> int:
        name = self.make_key(name)
        return await self.client.linsert(name, where, refvalue, value)

    async def llen(self, name: str) -> int:
        name = self.make_key(name)
        return await self.client.llen(name)

    async def lmove(
        self, first_list: str, second_list: str, src: str = "LEFT", dest: str = "RIGHT"
    ) -> str:
        return await self.client.lmove(first_list, second_list, src, dest)

    async def lmpop(
        self,
        numkeys: int,
        *args: t.List[str],
        direction: str,
        count: int | None = 1,
    ) -> t.List:
        return await self.client.lmpop(numkeys, *args, direction, count=count)

    async def lpop(self, name: str, count: int | None = None) -> str | t.List | None:
        name = self.make_key(name)
        return await self.client.lpop(name, count)

    async def lpos(
        self,
        name: str,
        value: str,
        rank: int = 0,
        count: int | None = None,
        maxlen: int | None = None,
    ) -> int:
        name = self.make_key(name)
        return await self.client.lpos(name, value, rank, count, maxlen)

    async def lpush(self, name: str, *values) -> int:
        name = self.make_key(name)
        return await self.client.lpush(name, *values)

    async def lpushx(self, name: str, *value: t.List) -> int:
        name = self.make_key(name)
        return await self.client.lpushx(name, *value)

    async def lrange(self, name: str, start: int, stop: int) -> t.List:
        name = self.make_key(name)
        return await self.client.lrange(name, start, stop)

    async def lrem(self, name: str, count: int, value: str) -> int:
        name = self.make_key(name)
        return await self.client.lrem(name, count, value)

    async def lset(self, name: str, index: int, value: str) -> str:
        name = self.make_key(name)
        return await self.client.lset(name, index, value)

    async def ltrim(self, name: str, start: int, stop: int) -> str:
        name = self.make_key(name)
        return await self.client.ltrim(name, start, stop)

    async def rpop(self, name: str, count: int | None = None) -> str | t.List | None:
        name = self.make_key(name)
        return await self.client.rpop(name, count)

    async def rpoplpush(self, src: str, dest: str) -> str:
        src = self.make_key(src)
        dest = self.make_key(dest)
        return await self.client.rpoplpush(src, dest)

    async def rpush(self, name: str, *values) -> int:
        name = self.make_key(name)
        return await self.client.rpush(name, *values)

    async def rpushx(self, name: str, *values) -> int:
        name = self.make_key(name)
        return await self.client.rpushx(name, *values)

    # set commands
    async def sadd(self, name: str, *values) -> int:
        name = self.make_key(name)
        return await self.client.sadd(name, *values)

    async def scard(self, name: str) -> int:
        name = self.make_key(name)
        return await self.client.scard(name)

    async def sdiff(self, keys: t.List[str], *args) -> t.List:
        keys = [self.make_key(key) for key in keys]
        return await self.client.sdiff(*keys, *args)

    async def sdiffstore(self, dest: str, keys: t.List[str], *args) -> int:
        dest = self.make_key(dest)
        keys = [self.make_key(key) for key in keys]
        return await self.client.sdiffstore(dest, *keys, *args)

    async def sinter(self, keys: t.List[str], *args) -> t.List:
        keys = [self.make_key(key) for key in keys]
        return await self.client.sinter(*keys, *args)

    async def sintercard(self, numkeys: int, keys: t.List[str], limit: int) -> int:
        keys = [self.make_key(key) for key in keys]
        return await self.client.sintercard(numkeys, keys, limit)

    async def sinterstore(self, dest: str, keys: t.List[str], *args) -> int:
        dest = self.make_key(dest)
        keys = [self.make_key(key) for key in keys]
        return await self.client.sinterstore(dest, *keys, *args)

    async def sismember(self, name: str, value: str) -> t.Literal[0, 1]:
        name = self.make_key(name)
        return await self.client.sismember(name, value)

    async def smembers(self, name: str) -> t.Set:
        name = self.make_key(name)
        return await self.client.smembers(name)

    async def smismember(
        self, name: str, values: t.List, *args
    ) -> t.List[t.Literal[0, 1]]:
        name = self.make_key(name)
        return await self.client.smismember(name, values, *args)

    async def smove(self, src: str, dest: str, value: str) -> bool:
        src = self.make_key(src)
        dest = self.make_key(dest)
        return await self.client.smove(src, dest, value)

    async def spop(self, name: str, count: int | None = None) -> str | t.List | None:
        name = self.make_key(name)
        return await self.client.spop(name, count)

    async def srandmember(
        self, name: str, count: int | None = None
    ) -> str | t.List | None:
        name = self.make_key(name)
        return await self.client.srandmember(name, count)

    async def srem(self, name: str, *values) -> int:
        name = self.make_key(name)
        return await self.client.srem(name, *values)

    async def sscan(
        self,
        name: str,
        cursor: int = 0,
        match: str | None = None,
        count: int | None = None,
    ) -> t.Any:
        name = self.make_key(name)
        return await self.client.sscan(name, cursor, match, count)

    async def sunion(self, keys: t.List[str], *args) -> t.List:
        keys = [self.make_key(key) for key in keys]
        return await self.client.sunion(keys, *args)

    async def sunionstore(self, dest: str, keys: t.List[str], *args) -> int:
        dest = self.make_key(dest)
        keys = [self.make_key(key) for key in keys]
        return await self.client.sunionstore(dest, keys, *args)

    # sorted set commands
    async def bzmpop(
        self,
        timeout: float,
        numkeys: int,
        keys: t.List[str],
        min: bool | None = None,
        max: bool | None = None,
        count: int | None = 1,
    ) -> t.List | None:
        return await self.client.bzmpop(timeout, numkeys, keys, min, max, count)

    async def bzpopmax(self, keys: t.List[str], timeout: int | None = 0) -> t.Any:
        keys = [self.make_key(key) for key in keys]
        return await self.client.bzpopmax(keys, timeout)

    async def bzpopmin(self, keys: t.List[str], timeout: int | None = 0) -> t.Any:
        keys = [self.make_key(key) for key in keys]
        return await self.client.bzpopmin(keys, timeout)

    async def zadd(self, name: str, mapping: t.Dict[str, float], *args, **kw) -> int:
        name = self.make_key(name)
        return await self.client.zadd(name, mapping, *args, **kw)

    async def zcard(self, name: str) -> t.Any:
        name = self.make_key(name)
        return await self.client.zcard(name)

    async def zcount(self, name: str, min: str | float, max: str | float) -> t.Any:
        name = self.make_key(name)
        return await self.client.zcount(name, min, max)

    async def zdiff(self, keys: t.List[str], withscores: bool = False) -> t.Any:
        keys = [self.make_key(key) for key in keys]
        return await self.client.zdiff(keys, withscores)

    async def zdiffstore(self, dest: str, keys: t.List[str]) -> int:
        dest = self.make_key(dest)
        keys = [self.make_key(key) for key in keys]
        return await self.client.zdiffstore(dest, keys)

    async def zincrby(self, name: str, amount: float, value: str) -> t.Any:
        name = self.make_key(name)
        return await self.client.zincrby(name, amount, value)

    async def zinter(
        self,
        keys: t.List[str],
        aggregate: str | None = None,
        withscores: bool | None = None,
    ) -> t.Any:
        keys = [self.make_key(key) for key in keys]
        return await self.client.zinter(keys, aggregate, withscores)

    async def zintercard(self, numkeys: int, keys: t.List[str], limit: int) -> int:
        keys = [self.make_key(key) for key in keys]
        return await self.client.zintercard(numkeys, keys, limit)

    async def zinterstore(
        self, dest: str, keys: t.List[str], aggregate: str | None = None
    ) -> int:
        dest = self.make_key(dest)
        keys = [self.make_key(key) for key in keys]
        return await self.client.zinterstore(dest, keys, aggregate)

    async def zlexcount(self, name: str, min: str, max: str) -> int:
        name = self.make_key(name)
        return await self.client.zlexcount(name, min, max)

    async def zmpop(
        self,
        numkeys: int,
        keys: t.List[str],
        min: bool | None = None,
        max: bool | None = None,
        count: int | None = 1,
    ) -> t.Any:
        return await self.client.zmpop(numkeys, keys, min, max, count)

    async def zmscore(self, name: str, members: t.List[str]) -> t.Any:
        name = self.make_key(name)
        return await self.client.zmscore(name, members)

    async def zpopmax(self, name: str, count: int | None = 1) -> t.Any:
        name = self.make_key(name)
        return await self.client.zpopmax(name, count)

    async def zpopmin(self, name: str, count: int | None = 1) -> t.Any:
        name = self.make_key(name)
        return await self.client.zpopmin(name, count)

    async def zrandmember(
        self, name: str, count: int | None = 1, withscores: bool = False
    ) -> t.Any:
        name = self.make_key(name)
        return await self.client.zrandmember(name, count, withscores)

    async def zrange(
        self,
        name: str,
        start: int,
        end: int,
        desc: bool = False,
        withscores: bool = False,
        score_cast_func: t.Callable = float,
        byscore: bool = False,
        bylex: bool = False,
        offset: int | None = None,
        num: int | None = None,
    ) -> t.Any:
        name = self.make_key(name)
        return await self.client.zrange(
            name,
            start,
            end,
            desc,
            withscores,
            score_cast_func,
            byscore,
            bylex,
            offset,
            num,
        )

    async def zrangebylex(
        self,
        name: str,
        min: str,
        max: str,
        start: int | None = None,
        num: int | None = None,
    ) -> t.Any:
        name = self.make_key(name)
        return await self.client.zrangebylex(name, min, max, start, num)

    async def zrangebyscore(
        self,
        name: str,
        min: str | float,
        max: str | float,
        start: int | None = None,
        num: int | None = None,
        withscores: bool = False,
        score_cast_func: t.Callable = float,
    ) -> t.Any:
        name = self.make_key(name)
        return await self.client.zrangebyscore(
            name, min, max, start, num, withscores, score_cast_func
        )

    async def zrangestore(
        self,
        dest: str,
        name: str,
        start: int,
        end: int,
        byscore: bool = False,
        bylex: bool = False,
        desc: bool = False,
        offset: int | None = None,
        num: int | None = None,
    ) -> int:
        dest = self.make_key(dest)
        name = self.make_key(name)
        return await self.client.zrangestore(
            dest, name, start, end, byscore, bylex, desc, offset, num
        )

    async def zrank(self, name: str, value: str, withscore: bool = False) -> t.Any:
        name = self.make_key(name)
        return await self.client.zrank(name, value, withscore)

    async def zrem(self, name: str, *values) -> t.Any:
        name = self.make_key(name)
        return await self.client.zrem(name, *values)

    async def zremrangebyrank(self, name: str, min: int, max: int) -> t.Any:
        name = self.make_key(name)
        return await self.client.zremrangebyrank(name, min, max)

    async def zremrangebyscore(
        self, name: str, min: str | float, max: str | float
    ) -> t.Any:
        name = self.make_key(name)
        return await self.client.zremrangebyscore(name, min, max)

    async def zremrangebylex(self, name: str, min: str, max: str) -> t.Any:
        name = self.make_key(name)
        return await self.client.zremrangebylex(name, min, max)

    async def zrevrange(
        self,
        name: str,
        start: int,
        end: int,
        withscores: bool = False,
        score_cast_func: t.Callable = float,
    ) -> t.Any:
        name = self.make_key(name)
        return await self.client.zrevrange(
            name, start, end, withscores, score_cast_func
        )

    async def zrevrangebylex(
        self,
        name: str,
        max: str,
        min: str,
        start: int | None = None,
        num: int | None = None,
    ) -> t.Any:
        name = self.make_key(name)
        return await self.client.zrevrangebylex(name, max, min, start, num)

    async def zrevrangebyscore(
        self,
        name: str,
        max: str | float,
        min: str | float,
        start: int | None = None,
        num: int | None = None,
        withscores: bool = False,
        score_cast_func: t.Callable = float,
    ) -> t.Any:
        name = self.make_key(name)
        return await self.client.zrevrangebyscore(
            name, max, min, start, num, withscores, score_cast_func
        )

    async def zrevrank(self, name: str, value: str, withscore: bool = False) -> t.Any:
        name = self.make_key(name)
        return await self.client.zrevrank(name, value, withscore)

    async def zscan(
        self,
        name: str,
        cursor: int = 0,
        match: str | None = None,
        count: int | None = None,
        score_cast_func: t.Callable = float,
    ) -> t.Any:
        name = self.make_key(name)
        return await self.client.zscan(name, cursor, match, count, score_cast_func)

    async def zscore(self, name: str, value: str) -> t.Any:
        name = self.make_key(name)
        return await self.client.zscore(name, value)

    async def zunion(
        self,
        keys: t.List[str],
        aggregate: str | None = None,
        withscores: bool = False,
    ) -> t.Any:
        keys = [self.make_key(key) for key in keys]
        return await self.client.zunion(keys, aggregate, withscores)

    async def zunionstore(
        self, dest: str, keys: t.List[str], aggregate: str | None = None
    ) -> t.Any:
        dest = self.make_key(dest)
        keys = [self.make_key(key) for key in keys]
        return await self.client.zunionstore(dest, keys, aggregate)
