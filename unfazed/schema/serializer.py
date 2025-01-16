import typing as t

from pydantic import BaseModel

T = t.TypeVar("T", bound=BaseModel)


class Result[T](BaseModel):
    count: int
    data: t.List[T]


class Relation(BaseModel):
    to: str
    source_field: str
    dest_field: str
    relation: t.Literal["m2m", "fk", "o2o", "bk_fk", "bk_o2o"]
