import typing as t

from pydantic import BaseModel
from pydantic.fields import FieldInfo


# for endpoint signature
class ResponseSpec(BaseModel):
    model: t.Union[str, t.List, t.Type[BaseModel], t.Dict]
    content_type: str = "application/json"
    code: str = "200"
    methods: t.List[str] = ["GET"]


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
    pass


class PathField(Param):
    pass


class QueryField(Param):
    pass


class HeaderField(Param):
    pass


class CookieField(Param):
    pass


class BodyField(Param):
    pass


class FormField(Param):
    pass


class FileField(Param):
    pass
