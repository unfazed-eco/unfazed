Unfazed Request
=====

unfazed 继承了 starlette 的 request，默认 endpoint 函数中第一个参数为 `request: HttpRequest`，其包含了请求的所有信息，请求的信息全部来自于 scope 。

## 签名

> request = HttpRequest(scope: dict, receive: Callable = None)


## 基本用法


```python

# endpoints.py
import typing as t
from unfazed.http import HttpRequest, HttpResponse


async def endpoint1(request: HttpRequest) -> HttpResponse:
    return HttpResponse(content="Hello, World!")

```


## 请求信息

`HttpRequest` 包含了请求的所有信息，包括


### Method

可以通过 `request.method` 获取请求的方法。


### URL

URL 包含了请求的 URL 信息，通过 `request.url` 获取。在 URL 对象中包含了以下信息

- request.url.scheme
- request.url.netloc
- request.url.path
- request.url.port
- request.url.query
- request.url.fragment
- request.url.username
- request.url.password
- request.url.hostname
- request.url.is_secure

### unfazed / app

request 包含了当前的 app 对象，可以通过 `request.app` 或者 `request.unfazed` 获取。

### Client

Client 包含了请求的客户端信息，通过 `request.client` 获取，包含

- request.client.host
- request.client.port


### State

State 包含了请求的状态信息，配合 `lifespan` 使用，通过 `request.state` 获取。

> 参考 [lifespan](./lifespan.md)。


### Headers

Headers 包含了请求的头信息，通过 `request.headers` 获取，在实际的项目中，建议通过 unfazed 推荐的参数化方式获取头信息。

> 参考 [endpoint](./endpoint.md)。

```python


class Hdr1(BaseModel):
    header1: str
    header2: int = Field(default=1)


async def endpoint(
    request: HttpRequest,
    hdr1: t.Annotated[Hdr1, p.Header()],
) -> JsonResponse:
    
    return JsonResponse({})


```


直接获取可以通过 `request.headers.get("header1")` 。


### Query Parameters


Query Parameters 包含了请求的查询参数，通过 `request.query_params` 获取，在实际的项目中，建议通过 unfazed 推荐的参数化方式获取query信息。

> 参考 [endpoint](./endpoint.md)。

```python


class Qry1(BaseModel):
    query1: str
    query2: int = Field(default=1)

async def endpoint2(
    request: HttpRequest,
    qry1: t.Annotated[Qry1, p.Query()],
) -> JsonResponse:
    return JsonResponse({})


```

直接获取可以通过 `request.query_params.get("query1")` 。


### Path Parameters

Path Parameters 包含了请求的路径参数，通过 `request.path_params` 获取，在实际的项目中，建议通过 unfazed 推荐的参数化方式获取path信息。

> 参考 [endpoint](./endpoint.md)。

```python

class Pth1(BaseModel):
    path1: str
    path2: int = Field(default=1)



async def endpoint1(
    request: HttpRequest,
    pth1: t.Annotated[Pth1, p.Path()],
) -> JsonResponse:

    return JsonResponse({})

```

直接获取可以通过 `request.path_params.get("path1")` 。


### Cookies

Cookies 包含了请求的 cookie 信息，通过 `request.cookies` 获取，在实际的项目中，建议通过 unfazed 推荐的参数化方式获取cookie信息。

> 参考 [endpoint](./endpoint.md)。

```python




class Ckie1(BaseModel):
    cookie1: str
    cookie2: int = Field(default=1)



async def endpoint4(
    request: HttpRequest,
    ck1: t.Annotated[Ckie1, p.Cookie()],
) -> JsonResponse:
    return JsonResponse({})


```

直接获取可以通过 `request.cookies.get("cookie1")` 。


### Body

Body 包含了请求的 body 信息，通过 `await request.json()` 或者 `await request.form()` 获取，在实际的项目中，建议通过 unfazed 推荐的参数化方式获取body信息。

> 参考 [endpoint](./endpoint.md)。

```python


class Body1(BaseModel):
    body1: str
    body2: int = Field(default=1)


async def endpoint5(
    request: HttpRequest,
    bd1: t.Annotated[Body1, p.Json()],
) -> JsonResponse:
    return JsonResponse({})



class Form1(BaseModel):
    form1: str
    form2: int = Field(default=1)


async def endpoint6(
    request: HttpRequest,
    form1: t.Annotated[Form1, p.Form()],
) -> JsonResponse:
    return JsonResponse({})

```

直接获取可以通过 `await request.json().get("bd1")` 或者 `await request.form().get("frm1")` 。


### Files

Files 包含了请求的文件信息，通过 `await request.form()` 获取，在实际的项目中，建议通过 unfazed 推荐的参数化方式获取文件信息。

```python

from unfazed.file import UploadFile

async def endpoint19(
    request: HttpRequest,
    file1: t.Annotated[UploadFile, p.File()],
) -> JsonResponse:
    return JsonResponse({})


```