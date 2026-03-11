# 第四部分：API 接口设计与 Schema 定义

在上一部分中，我们设计了数据模型和 serializer。现在我们将创建完整的 API endpoint，学习 Unfazed 的参数注解系统，定义请求/响应 schema，并了解 OpenAPI 文档如何自动生成。

## API 接口规划

根据选课系统需求，我们需要以下 endpoint：

| Endpoint 路径              | 方法 | 说明            | 参数来源      |
| -------------------------- | ---- | --------------- | ------------- |
| `/api/enroll/student-list` | GET  | 获取学生列表    | Query（分页） |
| `/api/enroll/course-list`  | GET  | 获取课程列表    | Query（分页） |
| `/api/enroll/bind`         | POST | 学生选课        | JSON body     |

> **关于 API 约定**：不同团队有不同设计标准。本教程采用仅使用 GET/POST、URL 遵循 `/api/{app}/{resource-action}` 模式、所有响应使用 HTTP 200 并在 body 中带 `code` 字段（0 表示成功）的约定。

## Schema 定义

Schema 定义 API 的数据契约 — 请求和响应的结构。它们是 Pydantic 模型，同样驱动 OpenAPI 文档生成。见 [OpenAPI](../features/openapi.md)。

### 创建 Schema 模型

编辑 `enroll/schema.py`：

```python
# enroll/schema.py

import typing as t

from pydantic import BaseModel, Field

from .serializers import StudentSerializer, CourseSerializer


class BaseResponse[T](BaseModel):
    """统一响应包装"""
    code: int = Field(0, description="响应码，0 表示成功")
    message: str = Field("", description="响应消息")
    data: T = Field(description="响应数据")


class StudentListResponse(BaseResponse[t.List[StudentSerializer]]):
    pass


class CourseListResponse(BaseResponse[t.List[CourseSerializer]]):
    pass


class BindRequest(BaseModel):
    student_id: int = Field(description="学生 ID", gt=0)
    course_id: int = Field(description="课程 ID", gt=0)


class BindResponse(BaseResponse[t.Dict]):
    pass
```

注意 `StudentSerializer` 和 `CourseSerializer` 可直接作为响应模型使用，因为它们继承自 Pydantic 的 `BaseModel`。

## Endpoint 实现

### 理解参数注解

Unfazed 使用 `typing.Annotated` 配合参数标记声明参数来源。完整参考见 [Endpoint](../features/endpoint.md)。

```python
import typing as t
from unfazed.route import params as p

# Query parameters (from URL query string: ?page=1&size=10)
page: t.Annotated[int, p.Query(default=1)]

# Path parameters (from URL path: /users/{user_id})
user_id: t.Annotated[int, p.Path()]

# JSON body (from request body)
data: t.Annotated[CreateUser, p.Json()]

# Response spec (for OpenAPI documentation)
-> t.Annotated[JsonResponse, p.ResponseSpec(model=UserResponse)]
```

可用参数标记：`Path`、`Query`、`Header`、`Cookie`、`Json`、`Form`、`File`。均继承自 Pydantic 的 `FieldInfo`，支持相同关键字参数（`default`、`description`、`ge`、`le` 等）。

### 编写 Endpoint

编辑 `enroll/endpoints.py`：

```python
# enroll/endpoints.py

import typing as t

from unfazed.http import HttpRequest, JsonResponse, PlainTextResponse
from unfazed.route import params as p

from . import schema as s

async def hello(request: HttpRequest) -> PlainTextResponse:
    """Hello World endpoint"""
    return PlainTextResponse("Hello, World!")


async def list_student(
    request: HttpRequest,
    page: t.Annotated[int, p.Query(default=1, description="页码", ge=1)],
    size: t.Annotated[int, p.Query(default=10, description="每页条数", ge=1, le=100)],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.StudentListResponse)]:
    """获取分页学生列表"""
    return JsonResponse({
        "code": 0,
        "message": "success",
        "data": [],
    })


async def list_course(
    request: HttpRequest,
    page: t.Annotated[int, p.Query(default=1, description="页码", ge=1)],
    size: t.Annotated[int, p.Query(default=10, description="每页条数", ge=1, le=100)],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.CourseListResponse)]:
    """获取分页课程列表"""
    return JsonResponse({
        "code": 0,
        "message": "success",
        "data": [],
    })


async def bind(
    request: HttpRequest,
    ctx: t.Annotated[s.BindRequest, p.Json()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.BindResponse)]:
    """学生选课"""
    return JsonResponse({
        "code": 0,
        "message": f"Student {ctx.student_id} enrolled in course {ctx.course_id}",
        "data": {
            "student_id": ctx.student_id,
            "course_id": ctx.course_id,
        },
    })
```

要点：

- 除 `HttpRequest` 外的每个参数都必须通过 `Annotated[Type, p.Source()]` 声明来源。
- `p.Query(default=1, ge=1)` 提供默认值和验证约束。
- `p.Json()` 从 JSON 请求体中提取参数。
- `p.ResponseSpec(model=...)` 告知 OpenAPI 响应结构 — 不影响运行时行为。
- **不要使用裸默认值** — 使用 `p.Query(default=...)` 而非 `page: int = 1`。见 [Endpoint — Gotchas](../features/endpoint.md#gotchas)。

### 路由配置

编辑 `enroll/routes.py`：

```python
# enroll/routes.py

from unfazed.route import path

from .endpoints import hello, list_student, list_course, bind

patterns = [
    path("/hello", endpoint=hello, name="hello"),
    path("/student-list", endpoint=list_student, name="list_students"),
    path("/course-list", endpoint=list_course, name="list_courses"),
    path("/bind", endpoint=bind, methods=["POST"], name="bind_course"),
]
```

## 自动 API 文档

### OpenAPI 配置

要启用文档 UI，添加 `OPENAPI` 设置：

```python
# entry/settings/__init__.py (add to UNFAZED_SETTINGS)

UNFAZED_SETTINGS = {
    # ... existing settings ...
    "OPENAPI": {
        "info": {
            "title": "Tutorial Project API",
            "version": "1.0.0",
            "description": "Student Course Enrollment System API",
        },
        "servers": [
            {"url": "http://127.0.0.1:9527", "description": "Local dev"},
        ],
        "allow_public": True,
    },
}
```

### 浏览文档

启动服务器后访问：

- **Swagger UI**（交互式）：`http://127.0.0.1:9527/openapi/docs`
- **ReDoc**（可读）：`http://127.0.0.1:9527/openapi/redoc`
- **原始 JSON schema**：`http://127.0.0.1:9527/openapi/openapi.json`

Unfazed 会根据 endpoint 类型注解自动生成 OpenAPI 3.1 schema — 参数类型、默认值、验证规则和响应模型均包含在内。见 [OpenAPI](../features/openapi.md)。

## 测试 Endpoint

### 使用 curl

```bash
# 学生列表（默认分页）
curl "http://127.0.0.1:9527/api/enroll/student-list"

# 学生列表（自定义分页）
curl "http://127.0.0.1:9527/api/enroll/student-list?page=1&size=5"

# 课程列表
curl "http://127.0.0.1:9527/api/enroll/course-list"

# 选课绑定
curl -X POST "http://127.0.0.1:9527/api/enroll/bind" \
     -H "Content-Type: application/json" \
     -d '{"student_id": 1, "course_id": 1}'
```

### 使用 Python

```python
import requests

base_url = "http://127.0.0.1:9527/api/enroll"

# Test student list
resp = requests.get(f"{base_url}/student-list", params={"page": 1, "size": 10})
print("Student list:", resp.json())

# Test binding
resp = requests.post(
    f"{base_url}/bind",
    json={"student_id": 1, "course_id": 1},
)
print("Bind result:", resp.json())
```

## 下一步

你已经设计了带类型化参数注解和自动 OpenAPI 文档的完整 API endpoint。下一部分我们将：

- 在 Services 层实现业务逻辑
- 通过 serializer 将 endpoint 与数据库连接
- 处理验证错误和边界情况

继续阅读 **[第五部分：业务逻辑实现](part5.md)**。
