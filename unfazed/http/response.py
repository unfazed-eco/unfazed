import typing as t
from urllib.parse import quote

import orjson as json
from pydantic import BaseModel
from starlette.background import BackgroundTask
from starlette.responses import Response

T = t.TypeVar(
    "T",
    t.Dict,
    t.List,
    str,
    bytes,
    BaseModel,
)


class HttpResponse[T](Response):
    media_type = "text/plain"

    def __init__(
        self,
        content: T = None,
        status_code: int = 200,
        headers: t.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)


class PlainTextResponse(HttpResponse[T]):
    pass


class HtmlResponse(HttpResponse[str]):
    media_type = "text/html"


class JsonResponse(HttpResponse[T]):
    media_type = "application/json"

    def render(self, content: T) -> bytes:
        if isinstance(content, (str, bytes)):
            raise ValueError(f"content {content} must be dumpable in JsonResponse")
        if isinstance(content, BaseModel):
            content = content.model_dump()
        return json.dumps(content)


class RedirctResponse(HttpResponse):
    def __init__(
        self,
        url: str,
        status_code: int = 302,
        headers: t.Mapping[str, str] | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(
            content=b"", status_code=status_code, headers=headers, background=background
        )
        self.headers["location"] = quote(str(url), safe=":/%#?=@[]!$&'()*+,;")


# TODO
# streaming response
# file response support range
