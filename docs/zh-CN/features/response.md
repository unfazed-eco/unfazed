Unfazed HTTP 响应
=================

Unfazed 提供一系列基于 Starlette `Response` 的响应类。每个类对应不同的内容类型 — 纯文本、HTML、JSON、重定向、流式传输以及支持范围请求的文件下载。所有响应都是 ASGI 可调用对象，可直接从 endpoint 返回。

## 快速开始

```python
from unfazed.http import HttpRequest, JsonResponse


async def get_user(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"id": 1, "name": "Alice"}, status_code=200)
```

## 响应类型

### HttpResponse — 纯文本

基础响应类。默认发送 `text/plain` 内容。

```python
from unfazed.http import HttpResponse

async def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world!", status_code=200)
```

### PlainTextResponse

`HttpResponse` 的别名，媒体类型为 `text/plain`。功能相同。

```python
from unfazed.http import PlainTextResponse

async def health(request: HttpRequest) -> PlainTextResponse:
    return PlainTextResponse("ok")
```

### HtmlResponse

发送 `text/html` 内容。

```python
from unfazed.http import HtmlResponse

async def page(request: HttpRequest) -> HtmlResponse:
    return HtmlResponse("<h1>Welcome</h1>")
```

### JsonResponse

发送 `application/json` 内容。接受 dict、list 和 Pydantic 模型。使用 `orjson` 进行序列化。

```python
from pydantic import BaseModel
from unfazed.http import JsonResponse


class User(BaseModel):
    name: str
    age: int


async def get_user(request: HttpRequest) -> JsonResponse:
    # 从 dict
    return JsonResponse({"name": "Alice", "age": 30})

    # 从 list
    return JsonResponse([1, 2, 3])

    # 从 Pydantic 模型
    user = User(name="Alice", age=30)
    return JsonResponse(user)
```

若内容不是 dict、list 或 Pydantic 模型，则抛出 `ValueError`。

### RedirectResponse

发送带有 `Location` 头的重定向。需要完整 URL（包含协议和主机）。

```python
from unfazed.http import RedirectResponse

async def go_home(request: HttpRequest) -> RedirectResponse:
    return RedirectResponse("https://example.com")

    # 永久重定向
    return RedirectResponse("https://example.com/new", status_code=301)
```

若 URL 缺少协议或主机（如 `"/relative/path"`），则抛出 `ValueError`。

### StreamingResponse

从同步或异步可迭代对象流式传输内容。适用于大负载或实时数据。

```python
from unfazed.http import StreamingResponse

async def stream_data(request: HttpRequest) -> StreamingResponse:
    async def generate():
        for i in range(100):
            yield f"line {i}\n"

    return StreamingResponse(generate(), media_type="text/plain")
```

同步生成器也可用 — 会自动在线程池中包装。

### FileResponse

流式传输文件，支持 HTTP 范围请求（可断点续传）。自动设置 `Content-Disposition`、`ETag`、`Last-Modified` 和 `Accept-Ranges` 头。

```python
from unfazed.http import FileResponse

async def download(request: HttpRequest) -> FileResponse:
    return FileResponse("/path/to/report.pdf", filename="report.pdf")
```

范围请求头（`Range`、`If-Range`）会被透明处理：
- 完整文件：`200 OK`
- 部分内容：`206 Partial Content`
- 无效范围：`416 Range Not Satisfiable`

## 通用参数

所有响应类都接受以下构造函数参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `content` | varies | `None` | 响应体。 |
| `status_code` | `int` | `200` | HTTP 状态码。 |
| `headers` | `Mapping[str, str]` | `None` | 额外的 HTTP headers。 |
| `media_type` | `str` | 类默认值 | Content-Type 头的值。 |
| `background` | `BackgroundTask` | `None` | 响应发送后执行的任务。 |

### 后台任务

在响应发送给客户端后执行工作：

```python
from starlette.background import BackgroundTask
from unfazed.http import JsonResponse


async def send_notification(user_id: int) -> None:
    # 发送邮件、推送通知等
    ...


async def create_user(request: HttpRequest) -> JsonResponse:
    task = BackgroundTask(send_notification, user_id=42)
    return JsonResponse({"id": 42}, background=task)
```

## API 参考

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
与 `HttpResponse` 相同。媒体类型：`text/plain`。

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
接受 `dict`、`list` 或 `BaseModel`。使用 `orjson` 序列化。

- `render(content) -> bytes`: 将内容序列化为 JSON 字节。

### RedirectResponse

```python
class RedirectResponse(HttpResponse):
    def __init__(self, url: str, status_code: int = 302, headers=None, background=None)
```
需要完整 URL。相对 URL 会抛出 `ValueError`。

### StreamingResponse

```python
class StreamingResponse(HttpResponse):
    def __init__(self, content: Iterable | AsyncIterable, status_code=200, headers=None, media_type=None, background=None)
```
流式传输内容块。同时支持同步和异步可迭代对象。

### FileResponse

```python
class FileResponse(StreamingResponse):
    def __init__(self, path: str | Path, filename: str | None = None, *, chunk_size: int = 65536, headers: Dict | None = None, background=None, media_type: str = "application/octet-stream")
```
支持 HTTP 范围请求的文件下载。若文件不存在则抛出 `FileNotFoundError`。
