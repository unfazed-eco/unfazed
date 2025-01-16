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


class BaseCredential(BaseModel):
    user: str = Field(..., alias="USER")
    password: str = Field(..., alias="PASSWORD")
    host: str = Field(..., alias="HOST")
    port: int = Field(..., alias="PORT")
    database: str = Field(..., alias="DATABASE")
    minsize: int | None = Field(default=None, alias="MIN_SIZE")
    maxsize: int | None = Field(default=None, alias="MAX_SIZE")
    ssl: t.Optional[bool] = Field(default=None, alias="SSL")


class PgsqlCredential(BaseCredential):
    max_queries: int | None = Field(default=None, alias="MAX_QUERIES")
    max_inactive_connection_lifetime: float | None = Field(
        default=None, alias="MAX_INACTIVE_CONNECTION_LIFETIME"
    )
    # schema: _[t.Any] = Field(None, alias="SCHEMA")


class MysqlCredential(BaseCredential):
    connect_timeout: int | None = Field(default=None, alias="CONNECT_TIMEOUT")
    echo: bool | None = Field(default=None, alias="ECHO")
    charset: str | None = Field(default=None, alias="CHARSET")


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
