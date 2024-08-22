"""
reference: https://tortoise.github.io/databases.html

"""

import typing as t

from pydantic import BaseModel
from unfazed.type import 

_ = t.Optional


class SqliteCredential(BaseModel):
    path: str
    journal_mode: _[str] = None
    journal_size_limit: _[int] = None
    foreign_keys: _[str] = None


class BaseCredential(BaseModel):
    user: str
    password: str
    host: str
    port: int
    database: str
    minsize: _[int] = None
    maxsize: _[int] = None
    ssl: t.Optional[bool] = None


class PgsqlCredential(BaseModel):
    max_queries: _[int] = None
    max_inactive_connection_lifetime: _[float] = None
    schema: _[t.Any] = None


class MysqlCredential(BaseCredential):
    connect_timeout: _[int] = None
    echo: _[bool] = None
    charset: _[str] = None


class Connection(BaseModel):
    engine: str
    credentials: t.Union[SqliteCredential, PgsqlCredential, MysqlCredential]


class AppModels(BaseModel):
    models: t.List[str]
    default_connection: str = "default"

class Database(BaseModel):
    connections: t.Dict[str, Connection]
    driver: str = "unfazed.orm.tortoise.Driver"
    apps: _[t.Dict[str, AppModels]] = None
    routers: _[t.List[str]] = None
    use_tz: _[bool] = None
    timezone: _[str] = None
