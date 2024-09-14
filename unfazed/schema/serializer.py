import typing as t

from pydantic import BaseModel


class Result(BaseModel):
    count: int
    data: t.List[BaseModel]
