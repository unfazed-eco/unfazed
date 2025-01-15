Unfazed Response
====

Unfazed 包含了一系列的 HttpResponse 类，用于处理请求的返回值，unfazed 要求所有的 endpoint 返回值都是 HttpResponse 类型。


## 签名

> resp = HttpResponse(content: Any, status: int = 200, headers: Optional[Dict[str, str]] = None, media_type: str = None)


## HttpResponse 类型


基本的使用代码如下

```python

from unfazed.http import HttpResponse, HttpRequest

async def endpoint(request: HttpRequest) -> HttpResponse:
    return HttpResponse(content="Hello, World!")

```


HttpResponse 类型包含了以下几种类型

- PlainTextResponse
- HtmlResponse
- JsonResponse
- RedirectResponse
- StreamingResponse
- FileResponse

以下是每种类型的详细介绍。


### PlainTextResponse

使用 `PlainTextResponse` 返回纯文本内容。

```python

from unfazed.http import PlainTextResponse, HttpRequest

async def endpoint(request: HttpRequest) -> PlainTextResponse:
    return PlainTextResponse(content="Hello, World!")

```


### HtmlResponse

使用 `HtmlResponse` 返回 HTML 内容。

```python

from unfazed.http import HtmlResponse, HttpRequest

async def endpoint(request: HttpRequest) -> PlainTextResponse:
    return HtmlResponse(content="<h1>hello, world</h1>")

```

### JsonResponse

JsonResponse 可以处理 `Dict`、`List`、`BaseModel` 类型的数据。

```python

from unfazed.http import JsonResponse, HttpRequest
from pydantic import BaseModel

async def endpoint1(request: HttpRequest) -> JsonResponse:
    return JsonResponse(content={"hello": "world"})


async def endpoint2(request: HttpRequest) -> JsonResponse:
    return JsonResponse(content=[{"hello": "world"}])


class User(BaseModel):
    name: str
    age: int

async def endpoint3(request: HttpRequest) -> JsonResponse:
    return JsonResponse(User(name="foo", age=20))


```


### RedirectResponse

RedirectResponse 用于重定向。

```python

from unfazed.http import RedirectResponse, HttpRequest

async def endpoint(request: HttpRequest) -> RedirectResponse:
    return RedirectResponse(url="/api")

```

### StreamingResponse

StreamingResponse 用于处理流式数据。

```python

import typing as t
from unfazed.http import StreamingResponse, HttpRequest

async def asynccontent() -> t.AsyncGenerator[bytes, None]:
        yield b"hello, "
        yield b"world"

async def endpoint(request: HttpRequest) -> RedirectResponse:
    resp = StreamingResponse(content=asynccontent())
    return resp


```

### FileResponse

FileResponse 用于处理文件下载，FileResponse 内置自动支持断点下载。

```python

from unfazed.http import FileResponse, HttpRequest


async def endpoint(request: HttpRequest) -> RedirectResponse:
    file_path = "/path/to/file"
    resp = FileResponse(file_path)
    return resp

```

