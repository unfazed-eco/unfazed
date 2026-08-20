"""
reference: https://tortoise.github.io/databases.html

"""

import typing as t

from pydantic import BaseModel, Field


class SqliteCredential(BaseModel):
    file_path: str = Field(..., alias="FILE_PATH")
    journal_mode: str | None = Field(default=None, alias="JOURNAL_MODE")
    journal_size_limit: int | None = Field(default=None, alias="JOURNAL_SIZE_LIMIT")
    foreign_keys: str | None = Field(default=None, alias="FOREIGN_KEYS")
    synchronous: str | None = Field(default=None, alias="SYNCHRONOUS")
    busy_timeout: int | None = Field(default=None, alias="BUSY_TIMEOUT")
    cache_size: int | None = Field(default=None, alias="CACHE_SIZE")
    temp_store: int | None = Field(default=None, alias="TEMP_STORE")
    wal_autocheckpoint: int | None = Field(default=None, alias="WAL_AUTOCHECKPOINT")
    mmap_size: int | None = Field(default=None, alias="MMAP_SIZE")
    locking_mode: str | None = Field(default=None, alias="LOCKING_MODE")


class BaseCredential(BaseModel):
    user: str = Field(..., alias="USER")
    password: str = Field(..., alias="PASSWORD")
    host: str = Field(..., alias="HOST")
    port: int = Field(..., alias="PORT")
    database: str = Field(..., alias="DATABASE")
    minsize: int | None = Field(default=None, alias="MIN_SIZE")
    maxsize: int | None = Field(default=None, alias="MAX_SIZE")


class PgsqlCredential(BaseCredential):
    max_queries: int | None = Field(default=None, alias="MAX_QUERIES")
    max_inactive_connection_lifetime: float | None = Field(
        default=None, alias="MAX_INACTIVE_CONNECTION_LIFETIME"
    )
    ssl: bool | None = Field(default=None, alias="SSL")
    command_timeout: float | None = Field(default=None, alias="COMMAND_TIMEOUT")
    timeout: float | None = Field(default=None, alias="TIMEOUT")
    statement_cache_size: int | None = Field(default=None, alias="STATEMENT_CACHE_SIZE")
    max_cached_statement_lifetime: int | None = Field(
        default=None, alias="MAX_CACHED_STATEMENT_LIFETIME"
    )
    max_cacheable_statement_size: int | None = Field(
        default=None, alias="MAX_CACHEABLE_STATEMENT_SIZE"
    )
    application_name: str | None = Field(default=None, alias="APPLICATION_NAME")
    server_settings: dict[str, t.Any] | None = Field(
        default=None, alias="SERVER_SETTINGS"
    )


class MysqlCredential(BaseCredential):
    connect_timeout: int | None = Field(default=None, alias="CONNECT_TIMEOUT")
    charset: str | None = Field(default=None, alias="CHARSET")
    ssl: dict[str, t.Any] | None = Field(default=None, alias="SSL")
    echo: bool | None = Field(default=None, alias="ECHO")
    pool_recycle: int | None = Field(default=None, alias="POOL_RECYCLE")
    read_timeout: int | None = Field(default=None, alias="READ_TIMEOUT")
    use_unicode: bool | None = Field(default=None, alias="USE_UNICODE")
    init_command: str | None = Field(default=None, alias="INIT_COMMAND")
    sql_mode: str | None = Field(default=None, alias="SQL_MODE")


class Connection(BaseModel):
    engine: str = Field(..., alias="ENGINE")
    credentials: t.Union[SqliteCredential, MysqlCredential, PgsqlCredential] = Field(
        ..., alias="CREDENTIALS"
    )


class AppModels(BaseModel):
    models: t.List[str] = Field(..., alias="MODELS")
    default_connection: str = Field(default="default", alias="DEFAULT_CONNECTION")


class Database(BaseModel):
    connections: t.Dict[str, Connection] = Field(..., alias="CONNECTIONS")
    driver: str = Field(default="unfazed.db.tortoise.Driver", alias="DRIVER")
    apps: t.Dict[str, AppModels] | None = Field(default=None, alias="APPS")
    routers: t.List[str] | None = Field(default=None, alias="ROUTERS")
    use_tz: bool | None = Field(default=None, alias="USE_TZ")
    timezone: str | None = Field(default=None, alias="TIMEZONE")
