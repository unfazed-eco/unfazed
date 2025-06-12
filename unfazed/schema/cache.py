import typing as t

from pydantic import BaseModel, Field

from unfazed.type import CanBeImported


class Cache(BaseModel):
    BACKEND: CanBeImported
    LOCATION: t.List[str] | str | None = None
    OPTIONS: t.Dict[str, t.Any] | None = None


class LocOptions(BaseModel):
    TIMEOUT: int | None = None
    PREFIX: str | None = None
    VERSION: int | None = None
    MAX_ENTRIES: int = 300


class RedisOptions(BaseModel):
    retry: t.Any = None

    socket_timeout: int | None = None
    socket_connect_timeout: int | None = None
    socket_keepalive: bool | None = None
    socket_keepalive_options: t.Mapping[int, t.Union[int, bytes]] | None = None

    # set decode responses to True
    decode_responses: bool = False
    retry_on_timeout: bool = False
    retry_on_error: t.List | None = None
    max_connections: int = 10
    single_connection_client: bool = False
    health_check_interval: int = 30

    ssl: bool = False
    ssl_keyfile: str | None = None
    ssl_certfile: str | None = None
    ssl_cert_reqs: str = "required"
    ssl_ca_certs: str | None = None
    ssl_ca_data: str | None = None
    ssl_check_hostname: bool = False
    ssl_min_version: t.Any = None
    ssl_ciphers: str | None = None

    serializer: CanBeImported | None = Field(
        "unfazed.cache.serializers.pickle.PickleSerializer",
        alias="SERIALIZER",
        description="serialize data before save",
    )

    compressor: CanBeImported | None = Field(
        "unfazed.cache.compressors.zlib.ZlibCompressor",
        alias="COMPRESSOR",
        description="compress data before save",
    )

    prefix: str | None = Field(
        None,
        alias="PREFIX",
        description="its strongly recommended to set prefix",
    )
