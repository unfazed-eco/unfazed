Unfazed Endpoint
=====

Endpoint 是 unfazed 中上承路由分发，下接 service 逻辑处理的中间层，其作用具体为：

1. 定义路由请求参数和响应
2. 连接 route 路由分发
3. 连接 service 逻辑处理
4. 供 openapi 文档生成


## 快速开始

创建一个简单的 endpoint。

```python

# endpoints.py
import typing as t
from unfazed.http import HttpRequest, HttpResponse


async def endpoint1(request: HttpRequest) -> HttpResponse:
    return HttpResponse(content="Hello, World!")

```

将其连接到 route。

```python

# routes.py
from unfazed.route import path
from .endpoints import endpoint1

patterns = [
    path("/", endpoint=endpoint1),
]

```

以上便是一个简单的 endpoint 的创建。


## 请求参数

endpoint 可以预定义请求参数，用于校验请求参数以及 openapi 文档生成。目前请求参数支持

1. Path
2. Query
3. Body
4. Header
5. Cookie
6. Form
7. File

请求参数使用 typing.Annotated 注解进行定义, 比如 `ctx: typing.Annotated[Context, Query()]`，以此来表示这是一个 Query 参数。unfazed 会自行解析请求参数，并将其传递给 endpoint 函数。

下面分别介绍这些请求参数的使用。


### Path


```python

import typing as t
from pydantic import BaseModel, Field
from unfazed.http import HttpRequest, JsonResponse
from unfazed.route import params as p


# 1
class Pth1(BaseModel):
    path1: str
    path2: int = Field(default=1)


class Pth2(BaseModel):
    path3: int
    path4: str = Field(default="123")


class RespE1(BaseModel):
    path1: str
    path2: int
    path3: int
    path4: str
    path5: str
    path6: str


async def endpoint1(
    request: HttpRequest,
    pth1: t.Annotated[Pth1, p.Path()],  # 2
    pth2: t.Annotated[Pth2, p.Path()],
    path5: t.Annotated[str, p.Path(default="foo")],
    path6: str,  # 3
) -> JsonResponse:
    r = RespE1(
        path1=pth1.path1,
        path2=pth1.path2,
        path3=pth2.path3,
        path4=pth2.path4,
        path5=path5,
        path6=path6,
    )
    return JsonResponse(r)


# routes.py

from unfazed.route import path
from .endpoints import endpoint1

patterns = [
    path("/{path1}/{path2}/{path3}/{path4}/{path5}/{path6}", endpoint=endpoint1),
]

```

解释

1. 请求参数可以采用 BaseModel 类型或者 python 基本类型
2. 使用 t.Annotated[Pth1, p.Path()] 定义参数类型，p.Path() 用于标记此为路径参数
3. path6 是因为在 path 中定义了 `{path6}`，unfazed 会优先解析为路径参数
4. 参数定义可以为多个不同的 BaseModel 类型以及 python 基本类型的组合
5. 参数定义可以使用 Field 定义默认值


### Query

```python

class Qry1(BaseModel):
    query1: str
    query2: int = Field(default=1)


class Qry2(BaseModel):
    query3: int
    query4: str = Field(default="123")


class RespE2(BaseModel):
    query1: str
    query2: int
    query3: int
    query4: str
    query5: str
    query6: str


async def endpoint2(
    request: HttpRequest,
    qry1: t.Annotated[Qry1, p.Query()],
    qry2: t.Annotated[Qry2, p.Query()],
    query5: t.Annotated[str, p.Query(default="foo")],
    query6: str,
) -> JsonResponse:
    r = RespE2(
        query1=qry1.query1,
        query2=qry1.query2,
        query3=qry2.query3,
        query4=qry2.query4,
        query5=query5,
        query6=query6,
    )
    return JsonResponse(r)


# routes.py

patterns = [
    path("/query", endpoint=endpoint2),
]

# >>> http://domain/query?query1=foo&query2=1&query3=2&query4=bar&query5=baz&query6=qux

```

解释

1. 参数定义中未使用 t.Annotated 时，如果类型为 python 基本类型，会被自动识别为 Query 参数


### Header

```python


class Hdr1(BaseModel):
    header1: str
    header2: int = Field(default=1)


class Hdr2(BaseModel):
    header3: int
    header4: str = Field(default="123")


class RespE3(BaseModel):
    header1: str
    header2: int
    header3: int
    header4: str
    header5: str


async def endpoint3(
    request: HttpRequest,
    hdr1: t.Annotated[Hdr1, p.Header()],
    hdr2: t.Annotated[Hdr2, p.Header()],
    header5: t.Annotated[str, p.Header(default="foo")],
) -> JsonResponse:
    r = RespE3(
        header1=hdr1.header1,
        header2=hdr1.header2,
        header3=hdr2.header3,
        header4=hdr2.header4,
        header5=header5,
    )
    return JsonResponse(r)


# routes.py

"""
scope = {
        "type": "http",
        "method": "GET",
        "scheme": "https",
        "server": ("www.example.org", 80),
        "path": "/header",
        "headers": [
            (b"header1", b"foo"),
            (b"header2", b"1"),
            (b"header3", b"2"),
            (b"header4", b"foo2"),
            (b"header5", b"foo3"),
        ],
        "query_string": b"",
    }
"""
patterns = [
    path("/header", endpoint=endpoint3),
]


```


### Cookie

```python


class Ckie1(BaseModel):
    cookie1: str
    cookie2: int = Field(default=1)


class Ckie2(BaseModel):
    cookie3: int
    cookie4: str = Field(default="123")


class RespE4(BaseModel):
    cookie1: str
    cookie2: int
    cookie3: int
    cookie4: str
    cookie5: str


async def endpoint4(
    request: HttpRequest,
    ck1: t.Annotated[Ckie1, p.Cookie()],
    ck2: t.Annotated[Ckie2, p.Cookie()],
    cookie5: t.Annotated[str, p.Cookie(default="foo")],
) -> JsonResponse:
    r = RespE4(
        cookie1=ck1.cookie1,
        cookie2=ck1.cookie2,
        cookie3=ck2.cookie3,
        cookie4=ck2.cookie4,
        cookie5=cookie5,
    )
    return JsonResponse(r)


# routes.py

"""
    scope = {
        "type": "http",
        "method": "GET",
        "scheme": "https",
        "server": ("www.example.org", 80),
        "path": "/",
        "headers": [
            (
                b"cookie",
                b"cookie1=foo; cookie2=1; cookie3=2; cookie4=foo2; cookie5=foo3",
            ),
        ],
        "query_string": b"",
    }

"""

patterns = [
    path("/", endpoint=endpoint4),
]

```


### Json

```python


class Body1(BaseModel):
    body1: str
    body2: int = Field(default=1)

    model_config = {
        "json_schema_extra": {"foo": "bar"},
    }


class Body2(BaseModel):
    body3: int
    body4: str = Field(default="123")


class Body3(BaseModel):
    body5: str


class RespE5(BaseModel):
    body1: str
    body2: int
    body3: int
    body4: str
    body5: str


async def endpoint5(
    request: HttpRequest,
    bd1: t.Annotated[Body1, p.Json()],
    bd2: t.Annotated[Body2, p.Json()],
    bd3: Body3,
    body6: t.Annotated[str, p.Json(default="foo")],
) -> JsonResponse:
    r = RespE5(
        body1=bd1.body1,
        body2=bd1.body2,
        body3=bd2.body3,
        body4=bd2.body4,
        body5=bd3.body5,
    )
    return JsonResponse(r)


# scope

{
    "type": "http.request",
    "body": b'{"body1": "foo", "body2": 1, "body3": 2, "body4": "foo2", "body5": "foo3"}',
    "more_body": False,
}

```

解释：

1. Body 中 media 类型为 application/json 参数使用 p.Json() 标记
2. 在没有 t.Annotated 的情况下，如果参数类型为 BaseModel，则会被自动识别为 Json 参数    


### Form

```python


class Form1(BaseModel):
    form1: str
    form2: int = Field(default=1)


class Form2(BaseModel):
    form3: int
    form4: str = Field(default="123")


class RespE6(BaseModel):
    form1: str
    form2: int
    form3: int
    form4: str
    form5: str


async def endpoint6(
    request: HttpRequest,
    form1: t.Annotated[Form1, p.Form()],
    form2: t.Annotated[Form2, p.Form()],
    form5: t.Annotated[str, p.Form(default="foo")],
    *args: t.Any,
    **kw: t.Any,
) -> JsonResponse:
    r = RespE6(
        form1=form1.form1,
        form2=form1.form2,
        form3=form2.form3,
        form4=form2.form4,
        form5=form5,
    )
    return JsonResponse(r)

# scope

{
    "type": "http.request",
    "body": b"form1=foo&form2=1&form3=2&form4=foo2&form5=foo3",
    "more_body": False,
}

```


### File

```python


from unfazed.file import UploadFile

class RespFile(BaseModel):
    file_name: str | None


async def endpoint19(
    request: HttpRequest,
    file1: t.Annotated[UploadFile, p.File()],
) -> JsonResponse:
    return JsonResponse(
        RespFile(
            file_name=file1.filename,
        )
    )

```

1. UploadFile 直接继承自 starlette.datastructures.UploadFile
2. 参数类型为 UploadFile 时，使用 p.File() 标记
