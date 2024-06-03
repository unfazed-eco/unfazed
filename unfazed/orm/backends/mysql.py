import typing as t

from pydantic import BaseModel

from .base import DataBaseWapper
from ..settings import BaseSettings as _BaseSettings


class Options(BaseModel):
    min_size: int | None = None
    max_size: int | None = None
    pool_recycle: int | None = None
    ssl: bool | None = None


class BaseSettings(_BaseSettings):
    OPTIONS: Options = Options()


class MysqlWrapper(DataBaseWapper):
    def __init__(self, settings_dict: dict[str, t.Any]):
        self.config = BaseSettings(**settings_dict)
