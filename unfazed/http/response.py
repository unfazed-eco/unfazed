import typing as t
from urllib.parse import quote

import orjson as json
from starlette.background import BackgroundTask
from starlette.responses import Response


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


class PlainTextResponse(HttpResponse):
    pass


class JsonResponse(HttpResponse):
    media_type = "application/json"

    def render(self, content: t.Any) -> bytes:
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
