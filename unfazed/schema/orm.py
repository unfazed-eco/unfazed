"""
reference: https://tortoise.github.io/databases.html

"""

import typing as t

from pydantic import BaseModel, Field

_ = t.Optional


class SqliteCredential(BaseModel):
    path: str = Field(..., alias="PATH")
    journal_mode: _[str] = Field(None, alias="JOURNAL_MODE")
    journal_size_limit: _[int] = Field(None, alias="JOURNAL_SIZE_LIMIT")
    foreign_keys: _[str] = Field(None, alias="FOREIGN_KEYS")


class BaseCredential(BaseModel):
    user: str = Field(..., alias="USER")
    password: str = Field(..., alias="PASSWORD")
    host: str = Field(..., alias="HOST")
    port: int = Field(..., alias="PORT")
    database: str = Field(..., alias="DATABASE")
    minsize: _[int] = Field(None, alias="MIN_SIZE")
    maxsize: _[int] = Field(None, alias="MAX_SIZE")
    ssl: t.Optional[bool] = Field(None, alias="SSL")


class PgsqlCredential(BaseCredential):
    max_queries: _[int] = Field(None, alias="MAX_QUERIES")
    max_inactive_connection_lifetime: _[float] = Field(
        None, alias="MAX_INACTIVE_CONNECTION_LIFETIME"
    )
    # schema: _[t.Any] = Field(None, alias="SCHEMA")


class MysqlCredential(BaseCredential):
    connect_timeout: _[int] = Field(None, alias="CONNECT_TIMEOUT")
    echo: _[bool] = Field(None, alias="ECHO")
    charset: _[str] = Field(None, alias="CHARSET")


class Connection(BaseModel):
    engine: str = Field(..., alias="ENGINE")
    credentials: t.Union[SqliteCredential, PgsqlCredential, MysqlCredential] = Field(
        ..., alias="CREDENTIALS"
    )


class AppModels(BaseModel):
    models: t.List[str] = Field(..., alias="MODELS")
    default_connection: str = Field("default", alias="DEFAULT_CONNECTION")


class Database(BaseModel):
    connections: t.Dict[str, Connection] = Field(..., alias="CONNECTIONS")
    driver: str = Field("unfazed.db.tortoise.Driver", alias="DRIVER")
    apps: _[t.Dict[str, AppModels]] = Field(None, alias="APPS")
    routers: _[t.List[str]] = Field(None, alias="ROUTERS")
    use_tz: _[bool] = Field(None, alias="USE_TZ")
    timezone: _[str] = Field(None, alias="TIMEZONE")
