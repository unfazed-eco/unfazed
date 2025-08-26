Unfazed 路由系统
========

Unfazed 的路由系统基于 Starlette 构建，设计理念借鉴了 Django 路由，并进行了大量增强。路由系统提供了强大的参数解析、中间件集成、OpenAPI 支持等功能，是构建 Web 应用的核心组件。

## 系统概述

### 核心特性

- **Django 风格设计**: 熟悉的路由配置模式，易于学习和使用
- **强大的参数解析**: 自动解析路径、查询、头部、Cookie、请求体参数
- **中间件集成**: 支持全局和路由级中间件
- **OpenAPI 原生支持**: 内置 OpenAPI 文档生成和 Swagger UI
- **类型安全**: 完整的类型注解和验证支持
- **灵活的组织**: 支持应用级路由组织和模块化开发

### 路由系统架构

```python
路由系统组件架构:
├── path() - 路由定义函数
├── include() - 路由模块包含函数
├── Route - 核心路由类（扩展自 Starlette）
├── EndpointHandler - 视图函数处理器
├── EndPointDefinition - 视图函数定义和参数解析
├── static() - 静态文件路由
└── mount() - ASGI 应用挂载
```

### 设计特点

1. **平铺式路由**: 所有路由最终展开为扁平结构，便于管理和调试
2. **应用隔离**: 每个应用的路由独立管理，支持命名空间
3. **参数化增强**: 强大的参数解析和验证系统
4. **中间件支持**: 路由级中间件，精确控制请求处理流程

## 路由配置

### 全局路由配置

路由入口通过 `ROOT_URLCONF` 配置，默认为 `entry.routes`：

```python
# settings.py
UNFAZED_SETTINGS = {
    "ROOT_URLCONF": "entry.routes",  # 指定路由入口文件
    "DEBUG": True,
    "INSTALLED_APPS": [
        "myapp1",
        "myapp2",
    ]
}
```

### 项目结构

```
project/
├── backend/
│   ├── entry/
│   │   ├── __init__.py
│   │   ├── routes.py          # 全局路由入口
│   │   └── settings.py
│   ├── myapp1/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── routes.py          # 应用路由
│   │   ├── endpoints.py       # 视图函数
│   │   └── models.py
│   └── myapp2/
│       ├── __init__.py
│       ├── routes.py
│       └── endpoints.py
└── main.py
```

## 路由定义

### 基本路由定义

```python
# myapp/endpoints.py
import typing as t
from unfazed.http import HttpRequest, JsonResponse

async def hello_world(request: HttpRequest) -> JsonResponse:
    """简单的Hello World"""
    return JsonResponse({"message": "Hello, World!"})

async def get_user(request: HttpRequest) -> JsonResponse:
    """获取用户信息"""
    user_id = request.path_params.get("user_id")
    return JsonResponse({"user_id": user_id, "name": f"User {user_id}"})
```

```python
# myapp/routes.py
from unfazed.route import path
from . import endpoints as e

patterns = [
    # 基本路由
    path("/hello", endpoint=e.hello_world),
    
    # 带路径参数的路由
    path("/users/{user_id}", endpoint=e.get_user),
    
    # 指定HTTP方法
    path("/users", endpoint=e.create_user, methods=["POST"]),
    
    # 带OpenAPI文档信息
    path(
        "/users/{user_id}",
        endpoint=e.update_user,
        methods=["PUT"],
        summary="更新用户信息",
        description="根据用户ID更新用户的基本信息",
        tags=["用户管理"],
    ),
]
```

### 全局路由组织

```python
# entry/routes.py
from unfazed.route import path, include

patterns = [
    # 包含应用路由
    path("/api/v1/users", routes=include("myapp1.routes")),
    path("/api/v1/orders", routes=include("myapp2.routes")),
    
    # 直接定义的全局路由
    path("/health", endpoint=health_check),
    path("/metrics", endpoint=get_metrics),
    
    # 静态文件路由
    static("/static", directory="static"),
    
    # 挂载外部ASGI应用
    mount("/admin", app=admin_app),
]
```

### 路由命名和组织

```python
# 命名路由，便于反向解析
patterns = [
    path(
        "/users/{user_id}",
        endpoint=e.get_user,
        name="user_detail",
        app_label="users"
    ),
    path(
        "/users/{user_id}/posts",
        endpoint=e.get_user_posts,
        name="user_posts",
        app_label="users"
    ),
]
```

## path 函数详解

### 完整签名

```python
def path(
    path: str,
    *,
    # 端点配置
    endpoint: Callable | None = None,
    routes: List[Route] | None = None,
    
    # HTTP 配置
    methods: List[HttpMethod] | None = None,
    
    # 路由元信息
    name: str | None = None,
    app_label: str | None = None,
    
    # 中间件配置
    middlewares: List[CanBeImported] | None = None,
    
    # OpenAPI 配置
    include_in_schema: bool = True,
    tags: List[str] | None = None,
    summary: str | None = None,
    description: str | None = None,
    externalDocs: Dict | None = None,
    deprecated: bool = False,
    operation_id: str | None = None,
    response_models: List[ResponseSpec] | None = None,
) -> Route | List[Route]:
```

### 参数详解

| 参数                | 类型          | 说明                         | 示例                                |
| ------------------- | ------------- | ---------------------------- | ----------------------------------- |
| `path`              | `str`         | 路由路径，支持路径参数       | `"/users/{user_id:int}"`            |
| `endpoint`          | `Callable`    | 视图函数（与routes互斥）     | `get_user`                          |
| `routes`            | `List[Route]` | 子路由列表（与endpoint互斥） | `include("app.routes")`             |
| `methods`           | `List[str]`   | 支持的HTTP方法，默认["GET"]  | `["GET", "POST"]`                   |
| `name`              | `str`         | 路由名称，用于反向解析       | `"user_detail"`                     |
| `app_label`         | `str`         | 应用标签，自动设置           | `"users"`                           |
| `middlewares`       | `List[str]`   | 路由级中间件                 | `["app.middleware.AuthMiddleware"]` |
| `include_in_schema` | `bool`        | 是否包含在OpenAPI文档中      | `True`                              |
| `tags`              | `List[str]`   | OpenAPI标签                  | `["用户管理"]`                      |
| `summary`           | `str`         | OpenAPI摘要                  | `"获取用户详情"`                    |
| `description`       | `str`         | OpenAPI描述                  | `"根据用户ID获取用户详细信息"`      |
| `deprecated`        | `bool`        | 是否已弃用                   | `False`                             |

### 路径参数支持

```python
patterns = [
    # 基本路径参数
    path("/users/{user_id}", endpoint=get_user),
    
    # 类型转换器
    path("/users/{user_id:int}", endpoint=get_user),
    path("/posts/{slug:str}", endpoint=get_post),
    path("/files/{file_path:path}", endpoint=download_file),
    
    # 多个路径参数
    path("/users/{user_id:int}/posts/{post_id:int}", endpoint=get_user_post),
    
    # 可选参数（通过查询参数实现）
    path("/search", endpoint=search),  # ?q=keyword&page=1
]
```

## 高级路由功能

### 路由中间件

```python
# middleware/auth.py
from unfazed.middleware import BaseMiddleware
from unfazed.http import JsonResponse

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        request = HttpRequest(scope, receive)
        
        # 检查认证
        auth_header = request.headers.get("authorization")
        if not auth_header:
            response = JsonResponse({"error": "未授权访问"}, status_code=401)
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)

# routes.py
patterns = [
    # 需要认证的路由
    path(
        "/admin/users",
        endpoint=admin_users,
        middlewares=["myapp.middleware.AuthMiddleware"]
    ),
    
    # 多个中间件（按顺序执行）
    path(
        "/api/sensitive",
        endpoint=sensitive_api,
        middlewares=[
            "myapp.middleware.AuthMiddleware",
            "myapp.middleware.RateLimitMiddleware",
            "myapp.middleware.LoggingMiddleware"
        ]
    ),
]
```

### OpenAPI 集成

```python
from unfazed.route.params import ResponseSpec
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class ErrorResponse(BaseModel):
    error: str
    code: int

patterns = [
    path(
        "/users/{user_id:int}",
        endpoint=get_user,
        methods=["GET"],
        summary="获取用户详情",
        description="根据用户ID获取用户的详细信息，包括用户名、邮箱等",
        tags=["用户管理"],
        response_models=[
            ResponseSpec(
                model=UserResponse,
                code="200",
                description="成功获取用户信息"
            ),
            ResponseSpec(
                model=ErrorResponse,
                code="404",
                description="用户不存在"
            ),
        ],
        externalDocs={
            "description": "用户API详细文档",
            "url": "https://docs.example.com/users"
        }
    ),
]
```

## 参数解析系统

Unfazed 路由系统的核心特色是强大的参数解析功能。详细内容请参考 [endpoint 文档](./endpoint.md)。

### 基本参数类型

```python
import typing as t
from pydantic import BaseModel, Field
from unfazed.route import params as p

# 路径参数
class UserPathParams(BaseModel):
    user_id: int = Field(..., description="用户ID")

# 查询参数
class UserQuery(BaseModel):
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页数量")

# 请求体
class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="邮箱地址")

async def create_user(
    request: HttpRequest,
    path_params: t.Annotated[UserPathParams, p.Path()],
    query: t.Annotated[UserQuery, p.Query()],
    user_data: t.Annotated[UserCreateRequest, p.Json()]
) -> JsonResponse:
    return JsonResponse({
        "user_id": path_params.user_id,
        "page": query.page,
        "username": user_data.username
    })
```

## 静态文件和挂载

### 静态文件服务

```python
from unfazed.route import static

patterns = [
    # 静态文件服务
    static("/static", directory="static", name="static"),
    static("/media", directory="uploads", name="media"),
    
    # 支持HTML文件（SPA应用）
    static("/", directory="dist", html=True, name="frontend"),
]
```

### 挂载外部应用

```python
from unfazed.route import mount
from starlette.applications import Starlette

# 创建外部ASGI应用
admin_app = Starlette()

patterns = [
    # 挂载到特定路径
    mount("/admin", app=admin_app, name="admin"),
    
    # 挂载子路由
    mount("/api/v2", routes=api_v2_routes, name="api_v2"),
]
```

## 自定义转换器

### 内置转换器

Unfazed 支持以下内置路径参数转换器：

- `str`: 字符串（默认）
- `int`: 整数
- `float`: 浮点数
- `uuid`: UUID
- `path`: 路径（包含斜杠）
- `slug`: URL slug

### 自定义转换器

```python
# converters.py
from starlette.convertors import Convertor
from unfazed.route import register_url_convertor

class LanguageConvertor(Convertor):
    """语言代码转换器"""
    regex = r"[a-z]{2}(-[A-Z]{2})?"  # zh, en, zh-CN, en-US

    def convert(self, value: str) -> str:
        return value.lower()

    def to_string(self, value: str) -> str:
        return value

class YearConvertor(Convertor):
    """年份转换器"""
    regex = r"[0-9]{4}"

    def convert(self, value: str) -> int:
        return int(value)

    def to_string(self, value: int) -> str:
        return str(value)

# app.py
from unfazed.app import BaseAppConfig

class AppConfig(BaseAppConfig):
    async def ready(self) -> None:
        # 注册自定义转换器
        register_url_convertor("lang", LanguageConvertor())
        register_url_convertor("year", YearConvertor())
```

### 使用自定义转换器

```python
# routes.py
patterns = [
    # 使用语言转换器
    path("/{lang:lang}/posts", endpoint=get_posts_by_language),
    
    # 使用年份转换器
    path("/archive/{year:year}", endpoint=get_posts_by_year),
    
    # 组合使用
    path("/{lang:lang}/archive/{year:year}/{month:int}", endpoint=get_monthly_posts),
]

# endpoints.py
async def get_posts_by_language(request: HttpRequest) -> JsonResponse:
    lang = request.path_params["lang"]  # 已转换为小写
    return JsonResponse({"language": lang, "posts": []})

async def get_posts_by_year(request: HttpRequest) -> JsonResponse:
    year = request.path_params["year"]  # 已转换为int
    return JsonResponse({"year": year, "posts": []})
```


通过 Unfazed 的路由系统，您可以构建出结构清晰、功能强大、易于维护的 Web 应用。路由系统提供了从简单的静态路由到复杂的参数化路由的完整解决方案，同时与 OpenAPI、中间件、参数解析等系统无缝集成。

