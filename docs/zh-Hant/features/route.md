路由
========

unfazed 的路由设计借鉴了 django 的路由设计，有细微差别，并由 starlette 实现，unfazed 路由有以下特点

1. 路由入口支持配置，默认为 `src/backend/entry/routes.py`
2. 路由本身支持中间件
3. unfazed 路由不支持 starlette 的 `Mount` 功能，所有路由均平铺，而非树状结构


### 路由配置

路由入口支持配置，默认为 `entry.routes`，对应的文件为 `src/backend/entry/routes.py`

```python

# src/backend/entry/settings/__init__.py
UNFAZED_SETTINGS = {
    "ROOT_URLCONF": "entry.routes",
}


```

### 路由注册

在 entry 目录以及单个应用目录下，都存在 `routes.py` 文件，用于注册路由，在 entry 目录下的 `routes.py` 用于注册全局路由，在单个应用目录下的 `routes.py` 用于注册应用路由。


#### 全局路由


```python

# src/backend/entry/routes.py

from unfazed.route import path, include

patterns = [
    path("/<app_name>/", routes=include("<app_name>.routes")),
]

```


#### 应用路由


```python

# src/backend/<app_name>/routes.py

from unfazed.route import path, include
from . import endpoints as e

patterns = [
    path("/path1", endpoint=e.endpoint1),
    path("/path2", endpoint=e.endpoint2),
]

```

按上述配置，会生成以下两个路由

```bash

/<app_name>/path1
/<app_name>/path2

```

### path 函数

path 函数用于注册路由，其签名如下

```python

def path(
    path: str,
    *,
    endpoint: t.Callable | None = None,
    routes: t.List[Route] | None = None,
    methods: t.List[HttpMethod] | None = None,
    name: str | None = None,
    app_label: str | None = None,
    middlewares: t.List[CanBeImported] | None = None,
    include_in_schema: bool = True,
    tags: t.List[str] | None = None,
    summary: str | None = None,
    description: str | None = None,
    externalDocs: t.Dict | None = None,
    deprecated: bool | None = None,
) -> Route | t.List[Route]:

```

参数解析

- path: 路由路径，支持路径参数，如 `/foo`、`/{bar}`、`/{bar:int}`
- endpoint: 路由对应的视图函数
- routes: 子路由，用于嵌套路由
- methods: 路由支持的 HTTP 方法，默认为 GET
- name: 路由名称
- app_label: 应用标签，用于区分不同应用的路由，unfazed 会自动填充
- middlewares: 路由中间件
- include_in_schema: openapi 相关配置，是否在 Swagger 中显示
- tags: openapi 相关配置，路由标签
- summary: openapi 相关配置，路由摘要
- description: openapi 相关配置，路由描述
- externalDocs: openapi 相关配置，外部文档
- deprecated: openapi 相关配置，是否弃用

### 正则

unfazed 路由不直接支持正则，但可以通过 `convertor` 实现正则，例如应用希望匹配语言，可以如下配置

1、在 app.py 中注册 convertor

```python

# src/backend/<app_name>/app.py

from unfazed.app import BaseAppConfig
from unfazed.route import register_url_convertor


class LangConvertor(Convertor):
    regex = r"[-_a-zA-Z]+"

    def convert(self, value: str) -> str:
        return value

    def to_string(self, value: str) -> str:
        return value

class AppConfig(BaseAppConfig):
    async def ready(self) -> None:
        register_url_convertor("lang", LangConvertor())

```

2、在 routes.py 中使用 convertor

```python

# src/backend/<app_name>/routes.py

from unfazed.route import path
from . import endpoints as e

patterns = [
    path("/{lang:lang}", endpoint=e.endpoint1),
]

```

3、在 endpoint 中使用 lang

```python

# src/backend/<app_name>/endpoints.py

from unfazed.route import HttpRequest, HttpResponse

async def endpoint1(request: HttpRequest, lang: str) -> HttpResponse:
    return HttpResponse(text=f"lang: {lang}")

```

