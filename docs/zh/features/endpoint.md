Unfazed Endpoint 详解
=====================

Unfazed 中的 endpoint 是处理 HTTP 请求的异步（或同步）函数。其强大之处在于**自动参数解析**：你使用 `typing.Annotated` 和参数标记（`Path`、`Query`、`Header`、`Cookie`、`Json`、`Form`、`File`）在函数签名中声明类型化参数，Unfazed 会自动从传入请求中提取、验证并注入它们。所有验证由 Pydantic 驱动。

## 快速开始

```python
# myapp/endpoints.py
import typing as t

from pydantic import BaseModel
from unfazed.http import HttpRequest, JsonResponse
from unfazed.route import params as p


class CreateUserBody(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


async def create_user(
    request: HttpRequest,
    body: t.Annotated[CreateUserBody, p.Json()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=UserResponse)]:
    # body.name 和 body.email 已通过验证
    return JsonResponse({"id": 1, "name": body.name, "email": body.email})
```

```python
# myapp/routes.py
from unfazed.route import Route, path

routes = [
    path("/users", endpoint=create_user, methods=["POST"]),
]
```

## 参数来源

endpoint 签名中每个非 `HttpRequest` 的参数都必须声明其值来源。使用 `typing.Annotated[Type, p.Source()]` 实现。

## 自定义 Request 类

你可以继承 `HttpRequest` 并将该子类作为 endpoint 的第一个参数，从而注入自定义 request 类型。

```python
from unfazed.http import HttpRequest, JsonResponse


class CustomRequest(HttpRequest):
    @property
    def trace_id(self) -> str:
        return self.headers.get("x-trace-id", "")


async def get_trace(request: CustomRequest) -> JsonResponse:
    return JsonResponse({"trace_id": request.trace_id})
```

规则如下：

- request 参数必须是 endpoint 签名中的第一个参数。
- 每个 endpoint 只能声明一个 `HttpRequest` 或其子类参数。

### 路径参数

从 URL 路径段提取。参数名必须与路由路径中的 `{name}` 占位符匹配。

```python
async def get_user(
    request: HttpRequest,
    user_id: t.Annotated[int, p.Path()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=UserResponse)]:
    return JsonResponse({"id": user_id, "name": "Alice", "email": "alice@example.com"})

# Route: path("/users/{user_id}", endpoint=get_user)
```

也可以使用 Pydantic 模型分组多个路径参数：

```python
class UserPath(BaseModel):
    org_id: int
    user_id: int


async def get_org_user(
    request: HttpRequest,
    ctx: t.Annotated[UserPath, p.Path()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=UserResponse)]:
    return JsonResponse({"id": ctx.user_id, "org_id": ctx.org_id})

# Route: path("/orgs/{org_id}/users/{user_id}", endpoint=get_org_user)
```

### 查询参数

从 URL 查询字符串（`?key=value`）提取。

```python
class SearchQuery(BaseModel):
    keyword: str
    page: int = 1
    limit: int = 20


async def search_users(
    request: HttpRequest,
    q: t.Annotated[SearchQuery, p.Query()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=UserListResponse)]:
    # GET /search?keyword=alice&page=2&limit=10
    return JsonResponse({"keyword": q.keyword, "page": q.page})
```

标量查询参数同样支持：

```python
async def search(
    request: HttpRequest,
    keyword: t.Annotated[str, p.Query()],
    page: t.Annotated[int, p.Query(default=1)],
) -> JsonResponse:
    return JsonResponse({"keyword": keyword, "page": page})
```

### Header 参数

从 HTTP headers 提取。

```python
async def check_auth(
    request: HttpRequest,
    authorization: t.Annotated[str, p.Header()],
    x_request_id: t.Annotated[str, p.Header(default="")],
) -> JsonResponse:
    return JsonResponse({"token": authorization})
```

也可以将 headers 分组到模型中：

```python
class AuthHeaders(BaseModel):
    authorization: str
    x_request_id: str = ""


async def check_auth(
    request: HttpRequest,
    headers: t.Annotated[AuthHeaders, p.Header()],
) -> JsonResponse:
    return JsonResponse({"token": headers.authorization})
```

### Cookie 参数

从请求 cookies 提取。

```python
async def get_session(
    request: HttpRequest,
    session_id: t.Annotated[str, p.Cookie()],
) -> JsonResponse:
    return JsonResponse({"session": session_id})
```

### JSON Body

从解析为 JSON 的请求体提取。使用 `p.Json()` 或直接传入 `BaseModel` 类型（参见 [自动检测规则](#auto-detection-rules)）。

```python
class UpdateProfile(BaseModel):
    display_name: str
    bio: str = ""


async def update_profile(
    request: HttpRequest,
    data: t.Annotated[UpdateProfile, p.Json()],
) -> JsonResponse:
    return JsonResponse({"name": data.display_name, "bio": data.bio})
```

也可以在同一 body 中混合模型参数与标量参数：

```python
async def create_item(
    request: HttpRequest,
    item: t.Annotated[ItemModel, p.Json()],
    priority: t.Annotated[int, p.Json(default=0)],
) -> JsonResponse:
    return JsonResponse({"name": item.name, "priority": priority})
```

### 表单数据

从 `application/x-www-form-urlencoded` 请求体提取。

```python
class LoginForm(BaseModel):
    username: str
    password: str


async def login(
    request: HttpRequest,
    form: t.Annotated[LoginForm, p.Form()],
) -> JsonResponse:
    return JsonResponse({"user": form.username})
```

### 文件上传

从 `multipart/form-data` 请求提取。使用 `UploadFile` 配合 `p.File()`：

```python
from unfazed.file import UploadFile


async def upload_avatar(
    request: HttpRequest,
    file: t.Annotated[UploadFile, p.File()],
    description: t.Annotated[str, p.Form(default="")],
) -> JsonResponse:
    content = await file.read()
    return JsonResponse({
        "filename": file.filename,
        "size": len(content),
        "description": description,
    })
```

文件上传可与同一 endpoint 中的表单字段组合使用。

## 自动检测规则

当参数**未**使用 `Annotated` 时，Unfazed 会自动推断其来源：

| 参数类型 | 条件 | 推断来源 |
|----------------|-----------|-----------------|
| `str`、`int`、`float` | 名称与路由路径中的 `{placeholder}` 匹配 | `Path` |
| `str`、`int`、`float` | 名称与路径占位符不匹配 | `Query` |
| `BaseModel` 子类 | 始终 | `Json` body |

```python
# 等价于显式注解：
async def get_user(
    request: HttpRequest,
    user_id: int,           # 自动检测为 Path（与路由中的 {user_id} 匹配）
    include_posts: str,     # 自动检测为 Query
    body: UpdateProfile,    # 自动检测为 Json body
) -> JsonResponse:
    ...

# Route: path("/users/{user_id}", endpoint=get_user, methods=["PUT"])
```

虽然方便，但建议使用显式 `Annotated` 注解以提高清晰度，并支持默认值和 OpenAPI 元数据。

## 响应类型

在返回类型注解中使用 `ResponseSpec` 为 OpenAPI 记录响应：

```python
class UserResponse(BaseModel):
    id: int
    name: str


async def get_user(
    request: HttpRequest,
    user_id: t.Annotated[int, p.Path()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=UserResponse)]:
    return JsonResponse({"id": user_id, "name": "Alice"})
```

可为不同状态码指定多个响应模型：

```python
class ErrorResponse(BaseModel):
    detail: str


async def get_user(
    request: HttpRequest,
    user_id: t.Annotated[int, p.Path()],
) -> t.Annotated[
    JsonResponse,
    p.ResponseSpec(model=UserResponse, code="200", description="Success"),
    p.ResponseSpec(model=ErrorResponse, code="404", description="Not found"),
]:
    return JsonResponse({"id": user_id, "name": "Alice"})
```

`ResponseSpec` 字段：

| 字段 | 类型 | 默认值 | 描述 |
|-------|------|---------|-------------|
| `model` | `Type[BaseModel]` | 必填 | 响应体的 Pydantic 模型。 |
| `code` | `str` | `"200"` | HTTP 状态码。 |
| `content_type` | `str` | `"application/json"` | 响应内容类型。 |
| `description` | `str` | `""` | OpenAPI 文档描述。 |

## 示例

### 多参数来源的完整 CRUD endpoint

```python
# myapp/endpoints.py
import typing as t

from pydantic import BaseModel, Field
from unfazed.http import HttpRequest, JsonResponse
from unfazed.route import params as p


class ArticleBody(BaseModel):
    title: str
    content: str
    tags: t.List[str] = Field(default_factory=list)


class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: t.List[str]


async def update_article(
    request: HttpRequest,
    article_id: t.Annotated[int, p.Path()],
    body: t.Annotated[ArticleBody, p.Json()],
    x_editor_id: t.Annotated[str, p.Header(default="")],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=ArticleResponse)]:
    return JsonResponse({
        "id": article_id,
        "title": body.title,
        "content": body.content,
        "tags": body.tags,
    })
```

### 带元数据的文件上传

```python
from unfazed.file import UploadFile


class UploadMeta(BaseModel):
    name: str
    category: str = "general"


class UploadResponse(BaseModel):
    filename: str
    size: int
    category: str


async def upload_document(
    request: HttpRequest,
    file: t.Annotated[UploadFile, p.File()],
    meta: t.Annotated[UploadMeta, p.Form()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=UploadResponse)]:
    content = await file.read()
    return JsonResponse({
        "filename": file.filename,
        "size": len(content),
        "category": meta.category,
    })
```

## 注意事项

**不能使用裸默认值。** 应使用带 `Param(default=...)` 的 `Annotated`：

```python
# 错误 — 会抛出 ValueError
async def bad(request: HttpRequest, page: int = 1) -> JsonResponse: ...

# 正确
async def good(
    request: HttpRequest,
    page: t.Annotated[int, p.Query(default=1)],
) -> JsonResponse: ...
```

**不能在同一 endpoint 中混用 Json 和 Form**。尝试时会在启动时抛出 `ValueError`。

**自定义 request 参数必须放在第一个位置。** 如果使用 `HttpRequest` 子类，它必须是第一个参数，且只能声明一次。

**所有参数都需要类型提示。** 缺少类型提示会抛出 `TypeHintRequired`。

**支持的标量类型：** `str`、`int`、`float`、`list`、`BaseModel`、`UploadFile`。其他类型（如 `bytes`、`dict`）不能作为直接参数类型。

**必须声明返回类型。** 每个 endpoint 必须具有返回类型注解。若不需要 OpenAPI 响应模型，可仅标注为 `-> JsonResponse`。

## API 参考

### 参数标记

所有参数标记继承自 Pydantic 的 `FieldInfo`，接受相同关键字参数（如 `default`、`alias`、`title`、`description`、`example`）。

```python
class Path(**kwargs)
```
从 URL 路径段提取。

```python
class Query(**kwargs)
```
从查询字符串提取。

```python
class Header(**kwargs)
```
从 HTTP headers 提取。

```python
class Cookie(**kwargs)
```
从 cookies 提取。

```python
class Json(**kwargs)
```
从 JSON 请求体提取。设置 `media_type="application/json"`。

```python
class Form(**kwargs)
```
从 URL 编码表单体提取。设置 `media_type="application/x-www-form-urlencoded"`。

```python
class File(**kwargs)
```
从 multipart 表单数据提取。设置 `media_type="multipart/form-data"`。与 `UploadFile` 配合使用。

### ResponseSpec

```python
class ResponseSpec(BaseModel):
    model: Type[BaseModel]
    content_type: str = "application/json"
    code: str = "200"
    description: str = ""
    headers: Dict[str, Header] | None = None
```

描述 endpoint 的响应，用于 OpenAPI 文档。放在返回类型的 `Annotated` 元数据中。
