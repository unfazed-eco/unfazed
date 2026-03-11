# 第二部分：创建应用与 Hello World

在上一部分中，我们创建并启动了 Unfazed 项目。现在我们将创建第一个应用，实现一个 "Hello, World" API，并理解 Unfazed 如何组织代码。

## 什么是应用？

在 Unfazed 中，**应用（App）** 是组织业务逻辑的基本单元。每个应用都是一个独立的 Python 包，包含 models、endpoints、routes、serializers 和 tests。这种模块化设计使代码库保持清晰，并支持跨项目复用。完整参考见 [App System](../features/app.md)。

## 创建 enroll 应用

我们将为选课系统创建一个名为 `enroll` 的应用。

### 使用 CLI 创建应用

```bash
# 确保在 backend 目录下
cd tutorial/src/backend

# 创建 enroll 应用
unfazed-cli startapp -n enroll -t simple
```

`-t simple` 使用基础模板。你也可以使用 `-t standard` 获得更结构化的子包布局。详见 [Command](../features/command.md)。

### 应用目录结构

```
enroll/
├── admin.py         # Admin 面板注册
├── app.py           # AppConfig 类（必需）
├── endpoints.py     # API endpoint 函数
├── models.py        # Tortoise ORM 模型定义
├── routes.py        # URL 路由声明
├── schema.py        # Pydantic 请求/响应模型
├── serializers.py   # CRUD 操作的数据 serializer
├── services.py      # 业务逻辑层
├── settings.py      # 应用级设置
└── test_all.py      # 测试用例
```

### 关键文件

| 文件             | 用途                                                          | 功能参考                              |
| ---------------- | ------------------------------------------------------------- | ------------------------------------- |
| `app.py`         | AppConfig 类 — 每个应用必需。                                 | [App](../features/app.md)             |
| `endpoints.py`   | 处理 HTTP 请求的异步函数。                                    | [Endpoint](../features/endpoint.md)  |
| `routes.py`      | URL 路径到 endpoint 的映射。                                  | [Routing](../features/route.md)       |
| `models.py`      | 数据库表结构与关系。                                          | [Tortoise ORM](../features/tortoise-orm.md) |
| `serializers.py` | 带 CRUD 操作的自动生成 Pydantic 模型。                        | [Serializer](../features/serializer.md) |
| `schema.py`      | 用于 OpenAPI 文档的请求/响应 Pydantic 模型。                  | [OpenAPI](../features/openapi.md)     |
| `admin.py`       | Admin 面板配置。                                              | [Admin](../features/contrib/admin.md) |

## 实现 Hello World

### 步骤 1：定义 endpoint 函数

编辑 `enroll/endpoints.py`：

```python
# enroll/endpoints.py

from unfazed.http import HttpRequest, PlainTextResponse, JsonResponse


async def hello(request: HttpRequest) -> PlainTextResponse:
    """简单纯文本响应"""
    return PlainTextResponse("Hello, World!")


async def hello_json(request: HttpRequest) -> JsonResponse:
    """JSON 格式响应"""
    return JsonResponse({
        "message": "Hello, World!",
        "framework": "Unfazed",
    })
```

要点：
- `HttpRequest` 是 Unfazed 的请求类，继承自 Starlette。见 [Request](../features/request.md)。
- `PlainTextResponse` 和 `JsonResponse` 是响应类。见 [Response](../features/response.md)。
- 所有 endpoint 函数都是 `async` — Unfazed 原生支持异步编程。

### 步骤 2：配置路由

编辑 `enroll/routes.py`：

```python
# enroll/routes.py

from unfazed.route import path

from .endpoints import hello, hello_json

patterns = [
    path("/hello", endpoint=hello),
    path("/hello-json", endpoint=hello_json),
]
```

`patterns` 列表定义 URL 到 endpoint 的映射。未指定 `methods` 时，`path()` 默认支持 `GET` 和 `HEAD`。见 [Routing](../features/route.md)。

### 步骤 3：在根 URL 配置中注册应用路由

编辑 `entry/routes.py`：

```python
# entry/routes.py

from unfazed.route import path, include

patterns = [
    path("/api/enroll", routes=include("enroll.routes")),
]
```

`include()` 从 `enroll.routes` 导入 `patterns` 列表，并为其添加 `/api/enroll` 前缀。因此 `/api/enroll/hello` 会映射到 `hello` endpoint。

### 步骤 4：在设置中注册应用

编辑 `entry/settings/__init__.py`，将 `enroll` 加入 `INSTALLED_APPS`：

```python
# entry/settings/__init__.py

UNFAZED_SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "Tutorial Project",
    "ROOT_URLCONF": "entry.routes",
    "INSTALLED_APPS": [
        "enroll",
    ],
    "MIDDLEWARE": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
}
```

`INSTALLED_APPS` 告诉 Unfazed 在启动时加载哪些应用。每个应用必须包含带 `AppConfig` 类的 `app.py`。`ROOT_URLCONF` 指向包含根 `patterns` 列表的模块。见 [Settings](../features/settings.md)。

## 测试 API

### 启动服务器

```bash
make run
# 或：uvicorn asgi:application --host 127.0.0.1 --port 9527 --reload
```

### 发送请求

```bash
curl http://127.0.0.1:9527/api/enroll/hello
# 输出：Hello, World!

curl http://127.0.0.1:9527/api/enroll/hello-json
# 输出：{"message":"Hello, World!","framework":"Unfazed"}
```

## 请求-响应架构

通过这个简单示例，可以看到 Unfazed 的分层架构：

```
HTTP Request → Routes → Endpoints (Controller) → Services (Business Logic) → Models (Data) → Database
                                                                                    ↓
HTTP Response ← Routes ← Endpoints ← Response
```

| 层级                     | 职责                              |
| ------------------------ | --------------------------------- |
| **Routes**               | URL 路径到处理函数的映射          |
| **Endpoints (Controller)** | 处理 HTTP 请求，调用业务逻辑      |
| **Services (Business)**  | 实现核心业务规则                  |
| **Models (Data)**        | 数据模型与数据库操作              |

各层职责清晰，便于测试和维护。

## 自动 API 文档

Unfazed 内置 OpenAPI 支持。启动项目后，可访问以下交互式 API 文档：

- **Swagger UI**：`http://127.0.0.1:9527/openapi/docs`
- **ReDoc**：`http://127.0.0.1:9527/openapi/redoc`

这些文档会根据 endpoint 的类型注解自动生成。配置选项见 [OpenAPI](../features/openapi.md)。

> **注意**：仅当配置了 `OPENAPI` 设置且 `allow_public` 为 `True` 时，OpenAPI 文档路由才可用。

## 下一步

你已经创建了第一个 Unfazed 应用并实现了 Hello World API。下一部分我们将：

- 定义数据模型（Student 和 Course）
- 使用 Tortoise ORM 进行数据库操作
- 创建用于数据验证和 CRUD 的 serializer

继续阅读 **[第三部分：数据模型与 Serializer](part3.md)**。
