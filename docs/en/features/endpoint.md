Unfazed Endpoints
=================

Endpoints in Unfazed are async (or sync) functions that handle HTTP requests. What makes them powerful is **automatic parameter resolution**: you declare typed parameters in your function signature using `typing.Annotated` and param markers (`Path`, `Query`, `Header`, `Cookie`, `Json`, `Form`, `File`), and Unfazed extracts, validates, and injects them from the incoming request automatically. All validation is powered by Pydantic.

## Quick Start

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
    # body.name and body.email are already validated
    return JsonResponse({"id": 1, "name": body.name, "email": body.email})
```

```python
# myapp/routes.py
from unfazed.route import Route, path

routes = [
    path("/users", endpoint=create_user, methods=["POST"]),
]
```

## Parameter Sources

Every non-`HttpRequest` parameter in an endpoint signature must declare where its value comes from. You do this with `typing.Annotated[Type, p.Source()]`.

## Custom Request Classes

You can inject a custom request type by subclassing `HttpRequest` and using that subclass as the first endpoint parameter.

```python
from unfazed.http import HttpRequest, JsonResponse


class CustomRequest(HttpRequest):
    @property
    def trace_id(self) -> str:
        return self.headers.get("x-trace-id", "")


async def get_trace(request: CustomRequest) -> JsonResponse:
    return JsonResponse({"trace_id": request.trace_id})
```

Rules:

- The request parameter must be the first parameter in the endpoint signature.
- Only one `HttpRequest` or `HttpRequest` subclass parameter is allowed per endpoint.

### Path Parameters

Extracted from URL path segments. The parameter name must match a `{name}` placeholder in the route path.

```python
async def get_user(
    request: HttpRequest,
    user_id: t.Annotated[int, p.Path()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=UserResponse)]:
    return JsonResponse({"id": user_id, "name": "Alice", "email": "alice@example.com"})

# Route: path("/users/{user_id}", endpoint=get_user)
```

You can also use a Pydantic model to group multiple path parameters:

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

### Query Parameters

Extracted from the URL query string (`?key=value`).

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

Scalar query params work too:

```python
async def search(
    request: HttpRequest,
    keyword: t.Annotated[str, p.Query()],
    page: t.Annotated[int, p.Query(default=1)],
) -> JsonResponse:
    return JsonResponse({"keyword": keyword, "page": page})
```

### Header Parameters

Extracted from HTTP headers.

```python
async def check_auth(
    request: HttpRequest,
    authorization: t.Annotated[str, p.Header()],
    x_request_id: t.Annotated[str, p.Header(default="")],
) -> JsonResponse:
    return JsonResponse({"token": authorization})
```

You can also group headers into a model:

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

### Cookie Parameters

Extracted from request cookies.

```python
async def get_session(
    request: HttpRequest,
    session_id: t.Annotated[str, p.Cookie()],
) -> JsonResponse:
    return JsonResponse({"session": session_id})
```

### JSON Body

Extracted from the request body parsed as JSON. Use `p.Json()` or simply pass a `BaseModel` type (see [Auto-Detection](#auto-detection-rules)).

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

You can also mix model params with scalar params in the same body:

```python
async def create_item(
    request: HttpRequest,
    item: t.Annotated[ItemModel, p.Json()],
    priority: t.Annotated[int, p.Json(default=0)],
) -> JsonResponse:
    return JsonResponse({"name": item.name, "priority": priority})
```

### Form Data

Extracted from `application/x-www-form-urlencoded` request bodies.

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

### File Upload

Extracted from `multipart/form-data` requests. Use `UploadFile` with `p.File()`:

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

File uploads can be combined with form fields in the same endpoint.

## Auto-Detection Rules

When a parameter does **not** use `Annotated`, Unfazed infers its source automatically:

| Parameter type | Condition | Inferred source |
|----------------|-----------|-----------------|
| `str`, `int`, `float` | Name matches a `{placeholder}` in the route path | `Path` |
| `str`, `int`, `float` | Name does NOT match a path placeholder | `Query` |
| `BaseModel` subclass | Always | `Json` body |

```python
# Equivalent to explicit annotations:
async def get_user(
    request: HttpRequest,
    user_id: int,           # auto-detected as Path (matches {user_id} in route)
    include_posts: str,     # auto-detected as Query
    body: UpdateProfile,    # auto-detected as Json body
) -> JsonResponse:
    ...

# Route: path("/users/{user_id}", endpoint=get_user, methods=["PUT"])
```

While convenient, explicit `Annotated` annotations are recommended for clarity and to support defaults and OpenAPI metadata.

## Response Typing

Use `ResponseSpec` in the return type annotation to document the response for OpenAPI:

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

You can specify multiple response models for different status codes:

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

`ResponseSpec` fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model` | `Type[BaseModel]` | required | Pydantic model for the response body. |
| `code` | `str` | `"200"` | HTTP status code. |
| `content_type` | `str` | `"application/json"` | Response content type. |
| `description` | `str` | `""` | Description for OpenAPI docs. |

## Examples

### Full CRUD endpoint with multiple param sources

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

### File upload with metadata

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

## Gotchas

**No bare default values.** Use `Annotated` with `Param(default=...)` instead:

```python
# Wrong — raises ValueError
async def bad(request: HttpRequest, page: int = 1) -> JsonResponse: ...

# Correct
async def good(
    request: HttpRequest,
    page: t.Annotated[int, p.Query(default=1)],
) -> JsonResponse: ...
```

**Cannot mix Json and Form** in the same endpoint. You will get a `ValueError` at startup if you try.

**Custom request parameters must come first.** If you use a custom `HttpRequest` subclass, declare it as the first parameter and only once.

**All parameters require type hints.** Missing type hints raise `TypeHintRequired`.

**Supported scalar types:** `str`, `int`, `float`, `list`, `BaseModel`, `UploadFile`. Other types (e.g. `bytes`, `dict`) are not supported as direct parameter types.

**Return type is required.** Every endpoint must have a return type annotation. If you don't need OpenAPI response models, just annotate with `-> JsonResponse`.

## API Reference

### Param markers

All param markers extend Pydantic's `FieldInfo` and accept the same keyword arguments (e.g. `default`, `alias`, `title`, `description`, `example`).

```python
class Path(**kwargs)
```
Extract from URL path segments.

```python
class Query(**kwargs)
```
Extract from query string.

```python
class Header(**kwargs)
```
Extract from HTTP headers.

```python
class Cookie(**kwargs)
```
Extract from cookies.

```python
class Json(**kwargs)
```
Extract from JSON request body. Sets `media_type="application/json"`.

```python
class Form(**kwargs)
```
Extract from form-encoded body. Sets `media_type="application/x-www-form-urlencoded"`.

```python
class File(**kwargs)
```
Extract from multipart form data. Sets `media_type="multipart/form-data"`. Use with `UploadFile`.

### ResponseSpec

```python
class ResponseSpec(BaseModel):
    model: Type[BaseModel]
    content_type: str = "application/json"
    code: str = "200"
    description: str = ""
    headers: Dict[str, Header] | None = None
```

Describes an endpoint's response for OpenAPI documentation. Place in the return type's `Annotated` metadata.
