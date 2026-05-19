import os
import typing as t
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
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


@dataclass(frozen=True)
class ByteRange:
    """A normalized byte range with an exclusive end."""

    start: int
    end: int


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
        self.range_end = self.file_size
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
        self.downloaded = 0

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
        if self.downloaded >= self.content_length:
            self.close()
            raise StopIteration

        chunk_size = min(self.chunk_size, self.content_length - self.downloaded)
        data = self.file.read(chunk_size)
        if not data:
            self.close()
            raise StopIteration

        self.downloaded += len(data)
        return data


class MultipartRangeFileHandler:
    """
    Iterator for RFC 7233 multipart/byteranges responses.
    """

    def __init__(
        self,
        path: PathLike,
        ranges: t.Sequence[ByteRange],
        *,
        boundary: str,
        content_type: str,
        file_size: int,
        chunk_size: int = 65536,
    ) -> None:
        self.path = Path(path).resolve()
        self.ranges = ranges
        self.boundary = boundary
        self.content_type = content_type
        self.file_size = file_size
        self.chunk_size = chunk_size

    @property
    def content_length(self) -> int:
        total = 0
        for byte_range in self.ranges:
            total += len(self._part_header(byte_range))
            total += byte_range.end - byte_range.start
            total += 2  # trailing CRLF after each part body
        total += len(self._closing_boundary())
        return total

    def _part_header(self, byte_range: ByteRange) -> bytes:
        return (
            f"--{self.boundary}\r\n"
            f"Content-Type: {self.content_type}\r\n"
            f"Content-Range: bytes {byte_range.start}-{byte_range.end - 1}/"
            f"{self.file_size}\r\n"
            "\r\n"
        ).encode("latin-1")

    def _closing_boundary(self) -> bytes:
        return f"--{self.boundary}--\r\n".encode("latin-1")

    def __iter__(self) -> t.Iterator[bytes]:
        with open(self.path, "rb") as file:
            for byte_range in self.ranges:
                yield self._part_header(byte_range)
                file.seek(byte_range.start)

                remaining = byte_range.end - byte_range.start
                while remaining > 0:
                    chunk = file.read(min(self.chunk_size, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

                yield b"\r\n"

        yield self._closing_boundary()


def _get_header(headers: t.Mapping[str, str], name: str) -> str | None:
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return None


def _if_range_allows_range(
    handler: RangeFileHandler, header_if_range: str | None
) -> bool:
    if not header_if_range:
        return True

    header_if_range = header_if_range.strip()
    if header_if_range == handler.etag:
        return True

    try:
        if_range_date = parsedate_to_datetime(header_if_range)
    except (TypeError, ValueError):
        return False

    if if_range_date.tzinfo is None:
        if_range_date = if_range_date.replace(tzinfo=ZoneInfo("UTC"))

    last_modified = datetime.fromtimestamp(int(handler.stat.st_mtime), ZoneInfo("UTC"))
    return last_modified <= if_range_date


def _parse_ranges_header(
    header_range: str | None, file_size: int
) -> tuple[t.Sequence[ByteRange] | None, bool]:
    """
    Parse a Range header.

    Returns:
        (None, False): malformed or unsupported range, ignore Range header.
        ([], True): syntactically valid but unsatisfiable range.
        ([ByteRange, ...], True): satisfiable ranges.
    """
    if not header_range:
        return None, False

    unit, separator, range_set = header_range.partition("=")
    if separator != "=" or unit.strip().lower() != "bytes":
        return None, False

    ranges: list[ByteRange] = []
    unsatisfiable = False
    for raw_item in range_set.split(","):
        item = raw_item.strip()
        if not item:
            return None, False

        first, dash, last = item.partition("-")
        if dash != "-":
            return None, False

        first = first.strip()
        last = last.strip()

        if first == "":
            if not last.isdigit():
                return None, False

            suffix_length = int(last)
            if suffix_length <= 0:
                unsatisfiable = True
                continue

            start = max(file_size - suffix_length, 0)
            end = file_size
        else:
            if not first.isdigit() or (last and not last.isdigit()):
                return None, False

            start = int(first)
            if last == "":
                end = file_size
            else:
                last_byte = int(last)
                if start > last_byte:
                    unsatisfiable = True
                    continue
                end = min(last_byte + 1, file_size)

            if start >= file_size:
                unsatisfiable = True
                continue

        if start < end:
            ranges.append(ByteRange(start, end))
        else:
            unsatisfiable = True

    if ranges:
        return ranges, True
    return [], unsatisfiable


def parse_range_request(
    handler: RangeFileHandler, headers: t.Mapping[str, str]
) -> tuple[t.Sequence[ByteRange], int]:
    header_range = _get_header(headers, "Range")
    header_if_range = _get_header(headers, "If-Range")

    if not _if_range_allows_range(handler, header_if_range):
        return [ByteRange(0, handler.file_size)], 200

    ranges, is_range_request = _parse_ranges_header(header_range, handler.file_size)
    if not is_range_request:
        return [ByteRange(0, handler.file_size)], 200

    if not ranges:
        return [], 416

    return ranges, 206


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
    ranges, status_code = parse_range_request(handler, headers)
    if not ranges:
        return 0, handler.file_size, status_code

    byte_range = ranges[0]
    return byte_range.start, byte_range.end, status_code


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
        status_code: int = 200,
        chunk_size: int = 65536,
        headers: t.Dict[str, str] | None = None,
        background: BackgroundTask | None = None,
        media_type: str = "application/octet-stream",
        content_disposition_type: str = "attachment",
    ) -> None:
        handler = RangeFileHandler(path, filename, chunk_size)
        self.filename = filename
        self.content_disposition_type = content_disposition_type
        self.media_type = media_type

        headers = headers or {}
        if status_code == 200:
            ranges, status_code = parse_range_request(handler, headers)
        else:
            ranges = [ByteRange(0, handler.file_size)]

        self.status_code = status_code
        boundary = "unfazed-boundary"

        content: ContentStream
        if status_code == 206 and len(ranges) > 1:
            content = MultipartRangeFileHandler(
                path,
                ranges,
                boundary=boundary,
                content_type=media_type,
                file_size=handler.file_size,
                chunk_size=chunk_size,
            )
            handler.close()
        else:
            if ranges:
                byte_range = ranges[0]
                handler.set_range(byte_range.start, byte_range.end)
            else:
                handler.set_range(0, 0)
            content = handler

        resp_headers = self.build_headers(handler, ranges, boundary)

        super().__init__(
            content,
            status_code,
            resp_headers,
            background=background,
            media_type=media_type,
        )

    def build_headers(
        self,
        handler: RangeFileHandler,
        ranges: t.Sequence[ByteRange],
        boundary: str,
    ) -> t.Dict[str, str]:
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
            "Content-Type": self.media_type,
        }

        if self.filename is not None:
            content_disposition_filename = quote(self.filename)
            if content_disposition_filename != self.filename:
                headers["Content-Disposition"] = (
                    f"{self.content_disposition_type}; "
                    f"filename*=utf-8''{content_disposition_filename}"
                )
            else:
                headers["Content-Disposition"] = (
                    f'{self.content_disposition_type}; filename="{self.filename}"'
                )

        if self.status_code == 206 and len(ranges) == 1:
            headers["Content-Range"] = handler.content_range
        elif self.status_code == 206 and len(ranges) > 1:
            multipart = MultipartRangeFileHandler(
                handler.path,
                ranges,
                boundary=boundary,
                content_type=self.media_type,
                file_size=handler.file_size,
                chunk_size=handler.chunk_size,
            )
            headers["Content-Type"] = f"multipart/byteranges; boundary={boundary}"
            headers["Content-Length"] = str(multipart.content_length)
        elif self.status_code == 416:
            headers["Content-Range"] = f"bytes */{handler.file_size}"
            headers["Content-Length"] = "0"

        return headers
