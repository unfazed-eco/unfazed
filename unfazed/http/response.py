import os
import typing as t
from datetime import datetime
from functools import partial
from pathlib import Path
from urllib.parse import quote, urlparse
from zoneinfo import ZoneInfo

import anyio
import orjson as json
from pydantic import BaseModel
from starlette.background import BackgroundTask
from starlette.concurrency import iterate_in_threadpool
from starlette.responses import Response

from unfazed.protocol import ASGIType
from unfazed.type import ContentStream, PathLike, Receive, Scope, Send

T = t.TypeVar("T", bound=t.Union[t.Dict, t.List, str, bytes, BaseModel, ContentStream])


class HttpResponse[T](Response):
    """
    Base HTTP response class that extends Starlette's Response.

    This class provides a foundation for all HTTP responses in the Unfazed framework.
    It supports various content types and can be extended for specific response formats.

    Args:
        content: The response content, can be of various types.
        status_code: HTTP status code, defaults to 200.
        headers: Optional HTTP headers.
        media_type: Content type of the response, defaults to "text/plain".
        background: Optional background task to run after the response is sent.
    """

    media_type = "text/plain"

    def __init__(
        self,
        content: T | None = None,
        status_code: int = 200,
        headers: t.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)


class PlainTextResponse(HttpResponse[str]):
    """
    Response class for plain text content.

    This response type is suitable for simple text-based responses.
    The content type is set to "text/plain".
    """

    pass


class HtmlResponse(HttpResponse[str]):
    """
    Response class for HTML content.

    This response type is suitable for HTML-based responses.
    The content type is set to "text/html".
    """

    media_type = "text/html"


class JsonResponse(HttpResponse[t.Union[BaseModel, t.Dict, t.List, t.Any]]):
    """
    Response class for JSON content.

    This response type is suitable for JSON-based responses.
    It supports serializing Pydantic models, dictionaries, and lists.

    Usage:
    ```python
    from pydantic import BaseModel

    # Dictionary response
    resp = JsonResponse({"foo": "bar"})

    # List response
    resp2 = JsonResponse([1, 2, 3])

    # Pydantic model response
    class Resp(BaseModel):
        name: str

    resp3 = JsonResponse(Resp(name="unfazed"))
    ```

    Args:
        content: The response content, must be a Pydantic model, dictionary, or list.
        status_code: HTTP status code, defaults to 200.
        headers: Optional HTTP headers.
        background: Optional background task to run after the response is sent.
    """

    media_type = "application/json"

    def render(self, content: T) -> bytes:
        if isinstance(content, BaseModel):
            ret = json.dumps(content.model_dump())
        elif isinstance(content, (dict, list)):
            ret = json.dumps(content)
        else:
            raise ValueError(f"content {content!r} must be dumpable in JsonResponse")
        return ret


class RedirectResponse(HttpResponse):
    """
    Response class for HTTP redirects.

    This response type is suitable for redirecting clients to another URL.
    It properly sets the Location header and handles URL encoding.

    Usage:
    ```python
    from unfazed.http import RedirectResponse

    # Redirect to Google
    resp = RedirectResponse("https://www.google.com")

    # Redirect with custom status code (e.g., 301 for permanent redirect)
    resp2 = RedirectResponse("https://example.com", status_code=301)
    ```

    Args:
        url: The URL to redirect to.
        status_code: HTTP status code, defaults to 302 (Found).
        headers: Optional HTTP headers.
        background: Optional background task to run after the response is sent.

    Raises:
        ValueError: If the URL is invalid or potentially unsafe.
    """

    def __init__(
        self,
        url: str,
        status_code: int = 302,
        headers: t.Mapping[str, str] | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        # Validate URL to prevent open redirect vulnerabilities
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"Invalid redirect URL: {url}")

        super().__init__(
            content=b"", status_code=status_code, headers=headers, background=background
        )
        self.headers["location"] = quote(str(url), safe=":/%#?=@[]!$&'()*+,;")


class StreamingResponse(HttpResponse[ContentStream]):
    """
    Response class for streaming content.

    This response type is suitable for streaming large amounts of data,
    such as file downloads or real-time data streams.

    Usage:
    ```python
    from unfazed.http import StreamingResponse

    async def stream_large_file(request) -> StreamingResponse:
        def content():
            for chunk in large_file:
                yield chunk

        return StreamingResponse(content())
    ```

    Args:
        content: An iterable or async iterable that yields content chunks.
        status_code: HTTP status code, defaults to 200.
        headers: Optional HTTP headers.
        media_type: Content type of the response.
        background: Optional background task to run after the response is sent.
    """

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

    async def listen_for_disconnect(self, receive: Receive) -> None:
        """
        Listen for client disconnection events.

        Args:
            receive: The ASGI receive callable.
        """
        while True:
            message = await receive()
            if message["type"] == ASGIType.HTTP_DISCONNECT:
                break

    async def stream_response(self, send: Send) -> None:
        """
        Stream the response content to the client.

        Args:
            send: The ASGI send callable.
        """
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

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        ASGI callable implementation.

        Args:
            scope: The ASGI scope.
            receive: The ASGI receive callable.
            send: The ASGI send callable.
        """
        async with anyio.create_task_group() as task_group:

            async def wrap(func: t.Callable[[], t.Awaitable[None]]) -> None:
                await func()
                task_group.cancel_scope.cancel()

            task_group.start_soon(wrap, partial(self.stream_response, send))
            await wrap(partial(self.listen_for_disconnect, receive))

        if self.background is not None:
            await self.background()


class RangeFileHandler:
    """
    Handler for file streaming with range request support.

    This class manages file streaming with support for HTTP range requests,
    allowing clients to request specific portions of a file.

    Args:
        path: Path to the file to stream.
        download_name: Optional name for the downloaded file.
        chunk_size: Size of each chunk to stream, defaults to 65536 bytes.
    """

    def __init__(
        self,
        path: PathLike,
        download_name: str | None = None,
        chunk_size: int = 65536,
    ) -> None:
        resolved_path = Path(path).resolve()
        if not resolved_path.exists():
            raise FileNotFoundError(f"File {resolved_path} not found")

        self.path = resolved_path
        self.stat = os.stat(resolved_path)

        self._file_name = download_name or resolved_path.name.split("/")[-1]
        self.chunk_size = chunk_size

        self.range_start = 0
        self.range_end = self.stat.st_size
        self._content_length = self.stat.st_size

        self.downloaded = 0
        self.file = open(self.path, "rb")

    @property
    def file_name(self) -> str:
        """Get the name of the file for download."""
        return self._file_name

    @property
    def content_length(self) -> int:
        """Get the content length of the file or range."""
        return self._content_length

    @property
    def file_size(self) -> int:
        """Get the total size of the file."""
        return self.stat.st_size

    @property
    def etag(self) -> str:
        """Generate an ETag for the file based on size and modification time."""
        modified = int(self.stat.st_mtime * 1000)
        return f'W/"{self.file_size}-{modified}"'

    @property
    def last_modified(self) -> str:
        """Get the last modified time of the file in RFC 2822 format."""
        # Use UTC for consistency across different timezones
        tz = ZoneInfo("UTC")
        modified = int(self.stat.st_mtime)

        return datetime.fromtimestamp(modified, tz).strftime("%a, %d %b %Y %H:%M:%S %Z")

    @property
    def content_range(self) -> str:
        """Get the Content-Range header value for the current range."""
        return f"bytes {self.range_start}-{self.range_end - 1}/{self.file_size}"

    def close(self) -> None:
        """Close the file handle."""
        self.file.close()

    def set_range(self, start: int, end: int) -> None:
        """
        Set the range to stream.

        Args:
            start: Start byte position.
            end: End byte position (exclusive).
        """
        self.range_start = start
        self.range_end = end
        self._content_length = self.range_end - self.range_start

        self.file.seek(self.range_start)

    def __iter__(self) -> t.Iterator[bytes]:
        """Make the handler iterable."""
        return self

    def __next__(self) -> bytes:
        """
        Get the next chunk of data.

        Returns:
            bytes: The next chunk of data.

        Raises:
            StopIteration: When all data has been streamed.
        """
        if self.downloaded >= self.range_end - self.range_start:
            self.close()
            raise StopIteration

        chunk_size = min(self.chunk_size, self.range_end - self.downloaded)
        data = self.file.read(chunk_size)
        self.downloaded += len(data)
        return data


def parse_request(
    handler: RangeFileHandler, headers: t.Dict[str, str]
) -> t.Tuple[int, int, int]:
    """
    Parse HTTP range request headers.

    This function handles the parsing of Range and If-Range headers
    to determine which portion of a file to serve.

    Args:
        handler: The RangeFileHandler instance.
        headers: The HTTP request headers.

    Returns:
        Tuple containing:
        - range_start: Start byte position.
        - range_end: End byte position (exclusive).
        - status_code: HTTP status code (200, 206, or 416).
    """
    header_if_range = headers.get("If-Range", None)
    header_range = headers.get("Range", None)

    range_start: int | str
    range_end: int | str
    range_start, range_end = 0, handler.file_size

    # Compare If-Range and etag if If-Range exists
    # If they are not equal, download the whole file
    continue_download = True
    status_code = 200
    if header_if_range:
        if header_if_range == handler.etag:
            status_code = 206
        else:
            continue_download = False

    if header_range and continue_download:
        # We only support "bytes=start-end"
        # If other range format, download the whole file
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
        except ValueError:
            range_start = 0
            range_end = handler.file_size
            status_code = 200

        if range_start > range_end:
            status_code = 416  # Requested Range Not Satisfiable

    return range_start, range_end, status_code


class FileResponse(StreamingResponse):
    """
    Response class for file downloads with range request support.

    This response type is suitable for streaming files to clients,
    with support for HTTP range requests to allow resumable downloads.

    Usage:
    ```python
    from unfazed.http import FileResponse

    async def download_file(request) -> FileResponse:
        return FileResponse("path/to/file.pdf", filename="document.pdf")
    ```

    Args:
        path: Path to the file to stream.
        filename: Optional name for the downloaded file.
        chunk_size: Size of each chunk to stream, defaults to 65536 bytes.
        headers: Optional HTTP headers.
        background: Optional background task to run after the response is sent.
    """

    def __init__(
        self,
        path: PathLike,
        filename: str | None = None,
        *,
        chunk_size: int = 65536,
        headers: t.Dict[str, str] | None = None,
        background: BackgroundTask | None = None,
        media_type: str = "application/octet-stream",
    ) -> None:
        handler = RangeFileHandler(path, filename, chunk_size)

        headers = headers or {}
        range_start, range_end, status_code = parse_request(handler, headers)
        self.status_code = status_code
        handler.set_range(range_start, range_end)
        resp_headers = self.build_headers(handler)

        super().__init__(
            handler,
            status_code,
            resp_headers,
            background=background,
            media_type=media_type,
        )

    def build_headers(self, handler: RangeFileHandler) -> t.Dict[str, str]:
        """
        Build HTTP headers for the file response.

        Args:
            handler: The RangeFileHandler instance.

        Returns:
            Dictionary of HTTP headers.
        """
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
