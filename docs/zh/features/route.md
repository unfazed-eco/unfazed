Unfazed 路由
============

Unfazed 的路由系统将 URL 路径映射到 endpoint 函数。路由使用 `path()` 辅助函数定义，组织到 `patterns` 列表中，并通过 `include()` 组合用于多应用项目。框架还支持通过 `static()` 提供静态文件、通过 `mount()` 挂载外部 ASGI 应用，以及按路由配置中间件。

## 快速开始

### 1. 在应用中定义路由

```python
# myapp/routes.py
from unfazed.route import path
from myapp.endpoints import list_users, get_user, create_user

patterns = [
    path("/users", endpoint=list_users),
    path("/users/{user_id:int}", endpoint=get_user),
    path("/users", endpoint=create_user, methods=["POST"]),
]
```

### 2. 接入根 URL 配置

```python
# routes.py（项目根目录）
from unfazed.route import path, include

patterns = [
    path("/api", routes=include("myapp.routes")),
]
```

### 3. 在配置中设置 ROOT_URLCONF

```python
# settings.py
UNFAZED_SETTINGS = {
    "PROJECT_NAME": "myproject",
    "ROOT_URLCONF": "routes",
}
```

路由模块必须在模块级别定义 `patterns` 列表。

## 定义路由

### 基本路由

```python
from unfazed.route import path

path("/users", endpoint=list_users)
```

未指定 `methods` 时，路由默认支持 `GET` 和 `HEAD`。

### 指定 HTTP 方法

```python
path("/users", endpoint=create_user, methods=["POST"])
path("/users/{user_id}", endpoint=update_user, methods=["PUT", "PATCH"])
```

指定 `GET` 时会自动添加 `HEAD`。

### 路径参数

在路径中使用 `{name}` 或 `{name:type}` 占位符：

```python
path("/users/{user_id:int}", endpoint=get_user)
path("/files/{path:path}", endpoint=serve_file)
```

内置转换器：`str`（默认）、`int`、`float`、`path`。可注册自定义转换器：

```python
from unfazed.route import Convertor, register_url_convertor


class LangConvertor(Convertor):
    regex = r"[-_a-zA-Z]+"

    def convert(self, value: str) -> str:
        return value

    def to_string(self, value: str) -> str:
        return value


register_url_convertor("lang", LangConvertor())

# 使用方式：
path("/docs/{lang:lang}", endpoint=get_docs)
```

### OpenAPI 元数据

路由接受会出现在生成的 OpenAPI 规范中的元数据字段：

```python
path(
    "/users",
    endpoint=list_users,
    tags=["users"],
    summary="List all users",
    description="Returns a paginated list of users",
    deprecated=False,
    operation_id="listUsers",
    externalDocs={"url": "https://docs.example.com/users"},
    include_in_schema=True,
)
```

设置 `include_in_schema=False` 可将路由从 OpenAPI 规范中隐藏。

## 组合路由

### 使用 `routes` 嵌套

使用 `routes` 参数为路由组添加前缀：

```python
user_routes = [
    path("/", endpoint=list_users),
    path("/{user_id}", endpoint=get_user),
]

patterns = [
    path("/api/users", routes=user_routes),
]
# 结果为：/api/users/ 和 /api/users/{user_id}
```

### 使用 `include()` 从其他模块引入

`include()` 导入模块的 `patterns` 列表并自动设置 `app_label`：

```python
from unfazed.route import path, include

patterns = [
    path("/api/blog", routes=include("blog.routes")),
    path("/api/auth", routes=include("unfazed.contrib.auth.routes")),
]
```

目标模块必须定义 `patterns` 列表：

```python
# blog/routes.py
from unfazed.route import path
from blog.endpoints import list_posts, get_post

patterns = [
    path("/posts", endpoint=list_posts),
    path("/posts/{post_id}", endpoint=get_post),
]
```

### 按路由配置中间件

为特定路由或路由组应用中间件：

```python
path(
    "/admin",
    routes=include("admin.routes"),
    middlewares=["myapp.middleware.AdminAuthMiddleware"],
)

# 或单个路由：
path(
    "/secret",
    endpoint=secret_endpoint,
    middlewares=["myapp.middleware.RateLimitMiddleware"],
)
```

中间件按列表逆序应用（与全局 `MIDDLEWARE` 配置相同）。

## 静态文件

从目录提供静态文件：

```python
from unfazed.route import static

patterns = [
    static("/static", "/path/to/staticfiles"),
    static("/media", "/path/to/media", html=True),
]
```

| 参数 | 说明 |
|------|------|
| `path` | URL 前缀（如 `"/static"`）。 |
| `directory` | 文件目录的绝对路径。 |
| `html` | 若为 `True`，对目录请求提供 `index.html`。 |

静态路由会从 OpenAPI schema 中排除。

## 挂载外部应用

在路径前缀下挂载任意 ASGI 应用：

```python
from starlette.applications import Starlette
from unfazed.route import mount

other_app = Starlette(...)

patterns = [
    mount("/legacy", app=other_app),
]
```

也可以挂载路由子组：

```python
patterns = [
    mount("/v2", routes=[
        Route("/users", endpoint=list_users_v2),
    ]),
]
```

挂载路由会从 OpenAPI schema 中排除。

## API 参考

### path()

```python
def path(
    path: str,
    *,
    endpoint: Callable = None,
    routes: List[Route] = None,
    methods: List[str] = None,
    name: str = None,
    app_label: str = None,
    middlewares: List[str] = None,
    include_in_schema: bool = True,
    tags: List[str] = None,
    summary: str = None,
    description: str = None,
    externalDocs: Dict = None,
    deprecated: bool = False,
    operation_id: str = None,
) -> Route | List[Route]
```

创建 `Route`（当提供 `endpoint` 时）或带前缀的路由列表（当提供 `routes` 时）。必须且只能提供 `endpoint` 或 `routes` 之一。

### include()

```python
def include(route_path: str) -> List[Route]
```

导入模块的 `patterns` 列表。模块必须在模块级别定义 `patterns`。

### static()

```python
def static(path: str, directory: str, *, name: str = None, app_label: str = None, html: bool = False) -> Static
```

创建静态文件服务路由。

### mount()

```python
def mount(path: str, app: ASGIApp = None, routes: List[Route] = None, *, name: str = None, app_label: str = None, middlewares: List[str] = None) -> Mount
```

在路径前缀下挂载 ASGI 应用或路由组。

### Route

```python
class Route(starlette.routing.Route):
    def __init__(self, path, endpoint, *, methods=None, name=None, middlewares=None, app_label=None, tags=None, include_in_schema=True, summary=None, description=None, externalDocs=None, deprecated=None, operation_id=None, response_models=None)
```

单个 URL 到 endpoint 的映射。路径必须以 `/` 开头。

### register_url_convertor()

```python
def register_url_convertor(key: str, convertor: Convertor) -> None
```

注册自定义 URL 路径转换器，用于 `{name:type}` 路径参数。
