import typing as t

from pydantic import BaseModel


class ErrorCode:
    SUCCESS = 0


class RespContent(BaseModel):
    code: int = 0
    message: str = "success"
    data: t.Union[t.List, t.Dict] = {}
