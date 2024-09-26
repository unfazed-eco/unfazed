import typing as t

from pydantic import BaseModel
from pydantic.fields import FieldInfo, _Unset


class Query(BaseModel):
    pass


class Body(BaseModel):
    pass


class Path(BaseModel):
    pass


class Header(BaseModel):
    pass


class Cookie(BaseModel):
    pass


class Form(BaseModel):
    pass


class File(BaseModel):
    pass


class Param(FieldInfo):
    in_: str = None
    style_: str = None

    def __init__(
        self,
        default: t.Any = _Unset,
        *,
        alias: str | None = None,
        title: str | None = None,
        description: str | None = None,
        examples: list[t.Any] | None = None,
        gt: float | None = None,
        ge: float | None = None,
        lt: float | None = None,
        le: float | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        deprecated: bool | None = None,
    ) -> None:
        super().__init__(
            default=default,
            alias=alias,
            title=title,
            description=description,
            examples=examples,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            deprecated=deprecated,
        )


class PathField(Param):
    in_: str = "path"
    style_: str = "form"


class QueryField(Param):
    in_: str = "query"
    style_: str = "simple"


class HeaderField(Param):
    style_: str = "simple"
    in_: str = "header"


class CookieField(Param):
    style_: str = "simple"
    in_: str = "cookie"


class BodyField(Param):
    in_: str = "body"
    style_: str = "simple"


class FormField(Param):
    in_: str = "form"
    style_: str = "simple"


class FileField(Param):
    in_: str = "file"
    style_: str = "simple"
