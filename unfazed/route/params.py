import typing as t

from pydantic import BaseModel, ConfigDict
from pydantic.fields import FieldInfo


# for endpoint signature
class ResponseSpec(BaseModel):
    model: t.Type[BaseModel]
    content_type: str = "application/json"
    code: str = "200"
    description: str = ""
    headers: t.Dict[str, "Header"] | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Param(FieldInfo):
    def __init__(self, **kwargs: t.Any) -> None:
        self.example = kwargs.get("example", None)
        super().__init__(**kwargs)


class Path(Param):
    pass


class Query(Param):
    pass


class Header(Param):
    pass


class Cookie(Param):
    pass


class Json(Param):
    def __init__(self, **kwargs: t.Any) -> None:
        kwargs["media_type"] = "application/json"
        super().__init__(**kwargs)
        self.media_type = "application/json"


class Form(Param):
    def __init__(self, **kwargs: t.Any) -> None:
        kwargs["media_type"] = "application/x-www-form-urlencoded"
        super().__init__(**kwargs)
        self.media_type = "application/x-www-form-urlencoded"


class File(Param):
    def __init__(self, **kwargs: t.Any) -> None:
        kwargs["media_type"] = "multipart/form-data"
        super().__init__(**kwargs)
        self.media_type = "multipart/form-data"
