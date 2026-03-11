Unfazed OpenAPI
===============

Unfazed 会根据你的 endpoint 类型注解自动生成 [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0) 架构，并通过 Swagger UI 和 Redoc 提供交互式文档。参数注解（`Path`、`Query`、`Header`、`Cookie`、`Json`、`Form`、`File`）和 `ResponseSpec` 返回类型会直接转换为 OpenAPI 规范 — 无需手动编写 schema。

## 快速开始

### 1. 添加 OPENAPI 配置

```python
# settings.py
UNFAZED_SETTINGS = {
    "PROJECT_NAME": "myproject",
    "OPENAPI": {
        "info": {
            "title": "My Project API",
            "version": "1.0.0",
            "description": "API documentation for My Project",
        },
    },
}
```

### 2. 浏览文档

服务启动后，访问：

- **Swagger UI：** [http://localhost:8000/openapi/docs](http://localhost:8000/openapi/docs)
- **Redoc：** [http://localhost:8000/openapi/redoc](http://localhost:8000/openapi/redoc)
- **原始 JSON schema：** [http://localhost:8000/openapi/openapi.json](http://localhost:8000/openapi/openapi.json)

当存在 `OPENAPI` 配置且 `allow_public` 为 `True` 时，这些路由会自动添加。

## 配置

完整的 `OPENAPI` 配置：

```python
"OPENAPI": {
    # OpenAPI 规范字段
    "openapi": "3.1.1",                     # 规范版本（默认 "3.1.1"）
    "info": {
        "title": "My API",                  # 必填
        "version": "1.0.0",                 # 必填
        "description": "API description",
        "termsOfService": "https://example.com/terms",
        "contact": {"name": "Support", "email": "support@example.com"},
        "license": {"name": "MIT"},
    },
    "servers": [
        {"url": "/", "description": "Default"},
        {"url": "https://api.example.com", "description": "Production"},
    ],
    "externalDocs": {
        "url": "https://docs.example.com",
        "description": "Full documentation",
    },

    # UI 配置
    "json_route": "/openapi/openapi.json",  # JSON schema endpoint 路径
    "swagger_ui": {
        "css": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        "js": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        "favicon": "https://www.openapis.org/wp-content/uploads/sites/3/2016/11/favicon.png",
    },
    "redoc": {
        "js": "https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js",
    },

    # 访问控制
    "allow_public": True,                   # 生产环境请设为 False
}
```

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `openapi` | `str` | `"3.1.1"` | OpenAPI 规范版本（`"3.1.0"` 或 `"3.1.1"`）。 |
| `info` | `dict` | 必填 | API 元数据（`title` 和 `version` 必填）。 |
| `servers` | `List[dict]` | `[{"url": "/"}]` | API 的服务器 URL 列表。 |
| `externalDocs` | `dict \| None` | `None` | 外部文档链接。 |
| `json_route` | `str` | `"/openapi/openapi.json"` | 原始 JSON schema 的 URL 路径。 |
| `swagger_ui` | `dict` | CDN 默认值 | Swagger UI 的 CSS/JS/favicon URL。 |
| `redoc` | `dict` | CDN 默认值 | Redoc 的 JS URL。 |
| `allow_public` | `bool` | `True` | 是否启用文档 endpoint。 |

## 工作原理

Unfazed 在启动时检查每个已注册的 `Route`，并根据 endpoint 签名构建 OpenAPI schema：

1. **参数** — `Path`、`Query`、`Header` 和 `Cookie` 注解会变为 OpenAPI 的 `parameters`，包含类型、默认值和是否必填。

2. **请求体** — `Json`、`Form` 和 `File` 注解会变为 OpenAPI 的 `requestBody`。Pydantic 模型的 JSON schema 会作为 `$ref` 包含在 `components/schemas` 中。

3. **响应** — 返回类型注解中的 `ResponseSpec` 会变为 OpenAPI 的 `responses`。每个 spec 映射到一个状态码，模型的 JSON schema 作为响应体。

4. **标签** — `Route` 或 `path()` 上的 `tags` 参数会变为 OpenAPI 的 tags，用于对 endpoint 分组。

例如，以下 endpoint：

```python
import typing as t
from pydantic import BaseModel
from unfazed.http import HttpRequest, JsonResponse
from unfazed.route import params as p


class UserBody(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: int
    name: str


async def create_user(
    request: HttpRequest,
    body: t.Annotated[UserBody, p.Json()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=UserResponse, code="201")]:
    return JsonResponse({"id": 1, "name": body.name}, status_code=201)
```

会生成包含以下内容的 OpenAPI path：
- 以 `UserBody` 作为 JSON schema 的 `requestBody`
- 以 `UserResponse` 作为 JSON schema 的 `201` 响应

### 路由级 OpenAPI 元数据

路由支持在 schema 中显示的额外字段：

```python
from unfazed.route import path

routes = [
    path(
        "/users",
        endpoint=create_user,
        methods=["POST"],
        tags=["users"],
        summary="Create a new user",
        description="Register a new user account",
        deprecated=False,
        externalDocs={"url": "https://docs.example.com/users"},
    ),
]
```

### 从 schema 中排除路由

设置 `include_in_schema=False` 可将路由从 OpenAPI 规范中隐藏：

```python
path("/health", endpoint=health_check, include_in_schema=False)
```

## 导出 Schema

使用 `export-openapi` CLI 命令将 schema 写入 YAML 文件（需要 `pyyaml`）：

```bash
unfazed-cli export-openapi -l ./docs
# OpenAPI schema exported to ./docs/openapi.yaml
```

## 在生产环境中禁用

将 `allow_public` 设为 `False` 可阻止文档 endpoint 被注册：

```python
"OPENAPI": {
    "info": {"title": "My API", "version": "1.0.0"},
    "allow_public": False,
}
```

当 `allow_public` 为 `False` 时，不会创建 `/openapi/docs`、`/openapi/redoc` 和 `/openapi/openapi.json` 路由。Schema 仍会在内部生成（供 `export-openapi` 使用），但不会通过 HTTP 提供。

## API 参考

### OpenApi

```python
class OpenApi:
    schema: Dict[str, Any] | None = None
```

用于生成和存储 OpenAPI schema 的类。由框架内部使用。

**类方法：**

- `create_schema(routes: List[Route], openapi_setting: OpenAPI) -> Dict`: 根据路由和配置生成完整 OpenAPI schema。将结果存储在 `OpenApi.schema`。
- `create_openapi_model(routes: List[Route], openapi_setting: OpenAPI) -> openapi_pydantic.OpenAPI`: 将 schema 生成为 Pydantic 模型。
- `create_pathitem_from_route(route: Route) -> PathItem`: 将单个路由转换为 OpenAPI path item。
- `create_tags_from_route(route: Route, tags: Dict) -> None`: 从路由中提取 tags。
- `create_schema_from_route_resp_model(route: Route) -> Dict`: 提取响应模型 schema。
- `create_schema_from_route_request_model(route: Route) -> Dict`: 提取请求体 schema。

### OpenAPI（配置模型）

```python
class OpenAPI(BaseModel):
    openapi: Literal["3.1.0", "3.1.1"] = "3.1.1"
    servers: List[Server] = [Server(url="/")]
    info: Info
    externalDocs: ExternalDocumentation | None = None
    json_route: str = "/openapi/openapi.json"
    swagger_ui: SwaggerUI = SwaggerUI()
    redoc: Redoc = Redoc()
    allow_public: bool = True
```

`OPENAPI` 配置的 Pydantic 模型。

### SwaggerUI

```python
class SwaggerUI(BaseModel):
    css: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"
    js: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"
    favicon: str = "https://www.openapis.org/wp-content/uploads/sites/3/2016/11/favicon.png"
```

Swagger UI 资源的 CDN URL。可覆盖以自托管。

### Redoc

```python
class Redoc(BaseModel):
    js: str = "https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"
```

Redoc JS 包的 CDN URL。可覆盖以自托管。
