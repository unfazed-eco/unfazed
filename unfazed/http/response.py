import os
import typing as t
from datetime import datetime
from functools import partial
from urllib.parse import quote

import anyio
import orjson as json
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, Scope
from pydantic import BaseModel
from starlette.background import BackgroundTask
from starlette.concurrency import iterate_in_threadpool
from starlette.responses import Response
from zoneinfo import ZoneInfo

from unfazed.protocol import ASGIType

Content = t.Union[str, bytes, memoryview]
SyncContentStream = t.Iterable[Content]
AsyncContentStream = t.AsyncIterable[Content]
ContentStream = t.Union[AsyncContentStream, SyncContentStream]


T = t.TypeVar("T", t.Dict, t.List, str, bytes, BaseModel, ContentStream)


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


# Copy most code from starlette.responses.StreamingResponse


class StreamingResponse(HttpResponse[ContentStream]):
    def __init__(
        self,
        content: ContentStream,
        status_code: int = 200,
        headers: t.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        if isinstance(content, t.AsyncIterable):
            self.body_iterator = content
        else:
            self.body_iterator = iterate_in_threadpool(content)
        self.status_code = status_code
        self.media_type = self.media_type if media_type is None else media_type
        self.background = background
        self.init_headers(headers)

    async def listen_for_disconnect(self, receive: ASGIReceiveCallable) -> None:
        while True:
            message = await receive()
            if message["type"] == ASGIType.HTTP_DISCONNECT:
                break

    async def stream_response(self, send: ASGISendCallable) -> None:
        await send(
            {
                "type": ASGIType.HTTP_RESPONSE_START,
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        async for chunk in self.body_iterator:
            if not isinstance(chunk, (bytes, memoryview)):
                chunk = chunk.encode(self.charset)
            await send(
                {"type": ASGIType.HTTP_RESPONSE_BODY, "body": chunk, "more_body": True}
            )

        await send(
            {"type": ASGIType.HTTP_RESPONSE_BODY, "body": b"", "more_body": False}
        )

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        async with anyio.create_task_group() as task_group:

            async def wrap(func: t.Callable[[], t.Awaitable[None]]) -> None:
                await func()
                task_group.cancel_scope.cancel()

            task_group.start_soon(wrap, partial(self.stream_response, send))
            await wrap(partial(self.listen_for_disconnect, receive))

        if self.background is not None:
            await self.background()


class RangeFileHandler:
    def __init__(
        self, path: str, download_name: str = None, chunk_size: int = 65536
    ) -> None:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {path} not found")

        self.path = path
        self.stat = os.stat(path)

        self._file_name = download_name or path.split("/")[-1]
        self.chunk_size = chunk_size

        self.range_start = 0
        self.range_end = self.stat.st_size
        self._content_length = self.stat.st_size

        self.downloaded = 0

        self.file = open(self.path, "rb")

    @property
    def file_name(self) -> str:
        return self._file_name

    @property
    def content_length(self) -> int:
        return self._content_length

    @property
    def file_size(self) -> int:
        return self.stat.st_size

    @property
    def etag(self) -> str:
        modified = int(self.stat.st_mtime * 1000)
        return f'W/"{self.file_size}-{modified}"'

    @property
    def last_modified(self) -> str:
        tz = ZoneInfo("GMT")
        modified = int(self.stat.st_mtime)

        return datetime.fromtimestamp(modified, tz).strftime("%a, %d %b %Y %H:%M:%S %Z")

    @property
    def content_range(self) -> str:
        return f"bytes {self.range_start}-{self.range_end - 1}/{self.file_size}"

    def close(self) -> None:
        self.file.close()

    def set_range(self, start: int, end: int) -> None:
        self.range_start = start
        self.range_end = end
        self._content_length = self.range_end - self.range_start

        self.file.seek(self.range_start)

    def __iter__(self) -> t.Iterator[bytes]:
        return self

    def __next__(self) -> bytes:
        if self.downloaded >= self.range_end - self.range_start:
            self.close()
            raise StopIteration

        chunk_size = min(self.chunk_size, self.range_end - self.downloaded)
        data = self.file.read(chunk_size)
        self.downloaded += len(data)
        return data


def parse_request(
    handler: RangeFileHandler, headers: t.Dict[str, t.Any]
) -> t.Tuple[int, int, int]:
    header_if_range = headers.get("If-Range", None)
    header_range = headers.get("Range", None)

    range_start, range_end = 0, handler.file_size

    # compare If-Range and etag if If-Range existed
    # if they are not equal, download the whole file
    continue_download = True
    status_code = 200
    if header_if_range:
        if header_if_range == handler.etag:
            status_code = 206
        else:
            continue_download = False

    if header_range and continue_download:
        # we only support "bytes =start-end"
        # if other range format, download the whole file
        try:
            range_start, range_end = header_range.split("=")[1].split("-")
        except Exception:
            range_start, range_end = 0, handler.file_size
        if range_end == "":
            range_end = handler.file_size

        if range_start == "":
            range_start = 0
        try:
            range_start = int(range_start)
            range_end = int(range_end)
            status_code = 206
        except Exception:
            range_start = 0
            range_end = handler.file_size
            status_code = 200

        if range_start > range_end:
            status_code = 416

    return range_start, range_end, status_code


class FileResponse(StreamingResponse):
    def __init__(
        self,
        path: str | os.PathLike[str],
        filename: str | None = None,
        *,
        chunk_size: int = 65536,
        headers: t.Mapping[str, str] | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        handler = RangeFileHandler(path, filename, chunk_size)
        range_start, range_end, status_code = parse_request(handler, headers)
        self.status_code = status_code
        handler.set_range(range_start, range_end)
        resp_headers = self.build_headers(handler)

        super().__init__(
            handler,
            status_code,
            resp_headers,
            background=background,
            media_type="application/octet-stream",
        )

    def build_headers(self, handler: RangeFileHandler) -> dict:
        headers = {
            "ETag": handler.etag,
            "Accept-Ranges": "bytes",
            "Last-Modified": handler.last_modified,
            "Content-Length": str(handler.content_length),
            "Content-Type": "application/octet-stream",
            "Content-Disposition": f"attachment; filename={handler.file_name}",
        }

        if self.status_code == 206:
            headers["Content-Range"] = handler.content_range

        return headers
