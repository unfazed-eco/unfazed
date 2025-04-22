Unfazed OpenAPI
=====

Unfazed 内置 OpenAPI 组件，用于生成 OpenAPI 文档。


## 快速开始

1、在 `settings.py` 中配置 `OPENAPI` 项

```python

# settings.py

UNFAZED_SETTINGS = {
    "OPENAPI": {
        "servers": [{"url": "http://127.0.0.1:9527", "description": "Local dev"}],
    }
}

```

2、在 `endpoints.py` 中编写函数


```python

# endpoints.py
from unfazed.http import HttpRequest, JsonResponse
from pydantic import BaseModel
from unfazed.route import params

class Ctx(BaseModel):
    page: int
    size: int
    search: str


class Hdr(BaseModel):
    token: str
    token2: str
    token3: str


class Body1(BaseModel):
    name: str
    age: int


class Resp(BaseModel):
    message: str
    ctx: Ctx = Ctx(page=1, size=10, search="hello")


async def endpoint1(
    request: HttpRequest, ctx: Ctx, hdr: t.Annotated[Hdr, params.Header()]
) -> t.Annotated[JsonResponse, ResponseSpec(model=Resp)]:
    data = Resp(message="Hello, World!")
    return JsonResponse(data)

```


3、配置路由

```python

# routes.py

from unfazed.route import path
from .endpoints import endpoint1

patterns = [
    path("/api", endpoint=endpoint1),
]

```

4、启动服务

```bash

>>> unfazed-cli runserver --host 0.0.0.0 --port 9527

```


5、访问 `http://127.0.0.0.1:9527/openapi/docs` 即可查看生成的 OpenAPI 文档。


## OpenAPI 配置

OpenAPI 完成配置项见 [OpenAPIConfig](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/schema/openapi.py)。

swagger 和 redoc 相关的静态资源支持配置，当前使用 jsdelivr 作为默认的 CDN 服务，国内用户可以自行配置。


## route 配置

在 `unfazed.route.path` 中，支持 openapi 相关参数。

- include_in_schema: 是否包含在 OpenAPI 文档中，默认为 `True`。
- response_models: 响应模型，用于生成 OpenAPI 文档，如果此项有值，则会自动忽略 endpoint 函数中的相关配置。
- tags: 标签，用于生成 OpenAPI 文档。
