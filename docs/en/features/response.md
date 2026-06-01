Unfazed HTTP Responses
======================

Unfazed provides a family of response classes built on Starlette's `Response`. Each class targets a different content type — plain text, HTML, JSON, redirects, streaming, and file downloads with range-request support. All responses are ASGI callables and can be returned directly from endpoints.

## Quick Start

```python
from unfazed.http import HttpRequest, JsonResponse


async def get_user(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"id": 1, "name": "Alice"}, status_code=200)
```

## Response Types

### HttpResponse — Plain Text

The base response class. Sends `text/plain` content by default.

```python
from unfazed.http import HttpResponse

async def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world!", status_code=200)
```

### PlainTextResponse

Alias for `HttpResponse` with `text/plain` media type. Functionally identical.

```python
from unfazed.http import PlainTextResponse

async def health(request: HttpRequest) -> PlainTextResponse:
    return PlainTextResponse("ok")
```

### HtmlResponse

Sends `text/html` content.

```python
from unfazed.http import HtmlResponse

async def page(request: HttpRequest) -> HtmlResponse:
    return HtmlResponse("<h1>Welcome</h1>")
```

### JsonResponse

Sends `application/json` content. Accepts dicts, lists, and Pydantic models. Uses `orjson` for serialization.

```python
from pydantic import BaseModel
from unfazed.http import JsonResponse


class User(BaseModel):
    name: str
    age: int


async def get_user(request: HttpRequest) -> JsonResponse:
    # From a dict
    return JsonResponse({"name": "Alice", "age": 30})

    # From a list
    return JsonResponse([1, 2, 3])

    # From a Pydantic model
    user = User(name="Alice", age=30)
    return JsonResponse(user)
```

Raises `ValueError` if the content is not a dict, list, or Pydantic model.

### RedirectResponse

Sends a redirect with a `Location` header. Requires a fully qualified URL (with scheme and host).

```python
from unfazed.http import RedirectResponse

async def go_home(request: HttpRequest) -> RedirectResponse:
    return RedirectResponse("https://example.com")

    # Permanent redirect
    return RedirectResponse("https://example.com/new", status_code=301)
```

Raises `ValueError` if the URL is missing a scheme or host (e.g. `"/relative/path"`).

### StreamingResponse

Streams content from a sync or async iterable. Useful for large payloads or real-time data.

```python
from unfazed.http import StreamingResponse

async def stream_data(request: HttpRequest) -> StreamingResponse:
    async def generate():
        for i in range(100):
            yield f"line {i}\n"

    return StreamingResponse(generate(), media_type="text/plain")
```

Sync generators work too — they are automatically wrapped in a thread pool.

### FileResponse

Streams a file with support for HTTP range requests (resumable downloads). Sets `ETag`, `Last-Modified`, and `Accept-Ranges` headers automatically. By default it behaves like a download response:

- `Content-Type` defaults to `application/octet-stream`
- `Content-Disposition` is added when `filename` is provided
- `content_disposition_type` can be used to switch from `attachment` to `inline`

```python
from unfazed.http import FileResponse

async def download(request: HttpRequest) -> FileResponse:
    return FileResponse(
        "/path/to/report.pdf",
        filename="report.pdf",
        headers=dict(request.headers),
    )


async def preview(request: HttpRequest) -> FileResponse:
    return FileResponse(
        "/path/to/manual.pdf",
        filename="manual.pdf",
        media_type="application/pdf",
        content_disposition_type="inline",
        headers=dict(request.headers),
    )
```

After passing the incoming request headers, `Range` and `If-Range` are handled transparently:

- No range request, or a malformed / unsupported range: `200 OK` with the full file
- A single byte range, such as `Range: bytes=0-1023`, `Range: bytes=1024-`, or `Range: bytes=-512`: `206 Partial Content` with a `Content-Range` header
- Multiple byte ranges, such as `Range: bytes=0-99,200-299`: `206 Partial Content` with a `multipart/byteranges` content type
- A syntactically valid but unsatisfiable range, such as a start offset beyond the file size: `416 Range Not Satisfiable` with `Content-Range: bytes */<size>`
- `If-Range` may use the current file `ETag` or an HTTP date. If validation fails, `Range` is ignored and the full file is returned.

`FileResponse` only parses range requests when `status_code=200`. If you pass a custom status code, the response streams the full file with that status.

## Common Parameters

All response classes accept these constructor arguments:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `content` | varies | `None` | Response body. |
| `status_code` | `int` | `200` | HTTP status code. |
| `headers` | `Mapping[str, str]` | `None` | Additional HTTP headers. |
| `media_type` | `str` | class default | Content-Type header value. |
| `background` | `BackgroundTask` | `None` | Task to run after the response is sent. |

For `FileResponse`, `headers` is used to read `Range` / `If-Range` from the current request. File response headers are generated automatically.

### Background Tasks

Run work after the response has been sent to the client:

```python
from starlette.background import BackgroundTask
from unfazed.http import JsonResponse


async def send_notification(user_id: int) -> None:
    # send email, push notification, etc.
    ...


async def create_user(request: HttpRequest) -> JsonResponse:
    task = BackgroundTask(send_notification, user_id=42)
    return JsonResponse({"id": 42}, background=task)
```

## API Reference

### HttpResponse

```python
class HttpResponse(starlette.responses.Response):
    media_type = "text/plain"
    def __init__(self, content=None, status_code=200, headers=None, media_type=None, background=None)
```

### PlainTextResponse

```python
class PlainTextResponse(HttpResponse)
```
Same as `HttpResponse`. Media type: `text/plain`.

### HtmlResponse

```python
class HtmlResponse(HttpResponse):
    media_type = "text/html"
```

### JsonResponse

```python
class JsonResponse(HttpResponse):
    media_type = "application/json"
```
Accepts `dict`, `list`, or `BaseModel`. Serializes with `orjson`.

- `render(content) -> bytes`: Serialize content to JSON bytes.

### RedirectResponse

```python
class RedirectResponse(HttpResponse):
    def __init__(self, url: str, status_code: int = 302, headers=None, background=None)
```
Requires a fully qualified URL. Raises `ValueError` on relative URLs.

### StreamingResponse

```python
class StreamingResponse(HttpResponse):
    def __init__(self, content: Iterable | AsyncIterable, status_code=200, headers=None, media_type=None, background=None)
```
Streams content chunks. Handles both sync and async iterables.

### FileResponse

```python
class FileResponse(StreamingResponse):
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
    ) -> None
```
File download with HTTP range-request support. Pass the current request headers to `headers` to enable `Range` / `If-Range` handling. Raises `FileNotFoundError` if the file does not exist.
