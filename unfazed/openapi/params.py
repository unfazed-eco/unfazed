import typing as t

from pydantic.fields import FieldInfo, _Unset


class Param(FieldInfo):
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


class Path(Param):
    in_: str = "path"
    style_: str = "form"


class Query(Param):
    in_: str = "query"
    style_: str = "simple"


class Header(Param):
    style_: str = "simple"
    in_: str = "header"


class Cookie(Param):
    style_: str = "simple"
    in_: str = "cookie"


class Body[T](Param):
    in_: str = "body"
    style_: str = "simple"


class Form[T](Param):
    in_: str = "form"
    style_: str = "simple"


class File(Param):
    in_: str = "file"
    style_: str = "simple"
