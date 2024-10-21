import typing as t

from pydantic import BaseModel

from unfazed.route.params import ResponseSpec


class StudentQuery(BaseModel):
    page: int
    size: int
    search: str


class Student(BaseModel):
    name: str
    age: int
    email: str


class StudentUpdate(BaseModel):
    name: str
    age: int


class StudentDelete(BaseModel):
    name: str


class StudentResponse(BaseModel):
    count: int
    data: t.List[Student]


StudentResponseMeta = ResponseSpec(
    model=StudentResponse,
    code="200",
)
