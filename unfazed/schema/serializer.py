import typing as t

from pydantic import BaseModel


class Result(BaseModel):
    count: int
    data: t.List[BaseModel]


class Relation(BaseModel):
    to: str
    source_field: str
    dest_field: str
    relation: t.Literal["m2m", "fk", "o2o", "bk_fk", "bk_o2o"]
