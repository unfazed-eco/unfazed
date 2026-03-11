# Part 4: API Interface Design and Schema Definition

In the previous part, we designed data models and serializers. Now we will create complete API endpoints, learn Unfazed's parameter annotation system, define request/response schemas, and see how OpenAPI documentation is generated automatically.

## API Interface Planning

Based on our enrollment system's requirements, we need the following endpoints:

| Endpoint Path              | Method | Description            | Parameter Source      |
| -------------------------- | ------ | ---------------------- | --------------------- |
| `/api/enroll/student-list` | GET    | Get student list       | Query (pagination)    |
| `/api/enroll/course-list`  | GET    | Get course list        | Query (pagination)    |
| `/api/enroll/bind`         | POST   | Student enrolls course | JSON body             |

> **Note on API conventions**: Different teams have different design standards. In this tutorial, we follow a convention where only GET/POST methods are used, URLs follow the pattern `/api/{app}/{resource-action}`, and all responses use HTTP status 200 with a `code` field in the body (0 = success).

## Schema Definition

Schemas define the data contracts for your API — the shapes of requests and responses. They are Pydantic models that also drive OpenAPI documentation generation. See [OpenAPI](../features/openapi.md).

### Creating Schema Models

Edit `enroll/schema.py`:

```python
# enroll/schema.py

import typing as t

from pydantic import BaseModel, Field

from .serializers import StudentSerializer, CourseSerializer


class BaseResponse[T](BaseModel):
    """Unified response wrapper"""
    code: int = Field(0, description="Response code, 0 = success")
    message: str = Field("", description="Response message")
    data: T = Field(description="Response data")


class StudentListResponse(BaseResponse[t.List[StudentSerializer]]):
    pass


class CourseListResponse(BaseResponse[t.List[CourseSerializer]]):
    pass


class BindRequest(BaseModel):
    student_id: int = Field(description="Student ID", gt=0)
    course_id: int = Field(description="Course ID", gt=0)


class BindResponse(BaseResponse[t.Dict]):
    pass
```

Note that `StudentSerializer` and `CourseSerializer` can be used directly as response models since they extend Pydantic's `BaseModel`.

## Endpoint Implementation

### Understanding Parameter Annotations

Unfazed uses `typing.Annotated` with param markers to declare where each parameter comes from. See [Endpoint](../features/endpoint.md) for the full reference.

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

Available param markers: `Path`, `Query`, `Header`, `Cookie`, `Json`, `Form`, `File`. All extend Pydantic's `FieldInfo` and accept the same keyword arguments (`default`, `description`, `ge`, `le`, etc.).

### Writing the Endpoints

Edit `enroll/endpoints.py`:

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
    page: t.Annotated[int, p.Query(default=1, description="Page number", ge=1)],
    size: t.Annotated[int, p.Query(default=10, description="Items per page", ge=1, le=100)],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.StudentListResponse)]:
    """Get paginated student list"""
    return JsonResponse({
        "code": 0,
        "message": "success",
        "data": [],
    })


async def list_course(
    request: HttpRequest,
    page: t.Annotated[int, p.Query(default=1, description="Page number", ge=1)],
    size: t.Annotated[int, p.Query(default=10, description="Items per page", ge=1, le=100)],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.CourseListResponse)]:
    """Get paginated course list"""
    return JsonResponse({
        "code": 0,
        "message": "success",
        "data": [],
    })


async def bind(
    request: HttpRequest,
    ctx: t.Annotated[s.BindRequest, p.Json()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.BindResponse)]:
    """Bind a student to a course"""
    return JsonResponse({
        "code": 0,
        "message": f"Student {ctx.student_id} enrolled in course {ctx.course_id}",
        "data": {
            "student_id": ctx.student_id,
            "course_id": ctx.course_id,
        },
    })
```

Key points:

- Every non-`HttpRequest` parameter must declare its source via `Annotated[Type, p.Source()]`.
- `p.Query(default=1, ge=1)` provides a default value and validation constraint.
- `p.Json()` extracts the parameter from the JSON request body.
- `p.ResponseSpec(model=...)` tells OpenAPI what the response looks like — it does not affect runtime behavior.
- **No bare default values** — use `p.Query(default=...)` instead of `page: int = 1`. See [Endpoint — Gotchas](../features/endpoint.md#gotchas).

### Route Configuration

Edit `enroll/routes.py`:

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

## Automatic API Documentation

### OpenAPI Configuration

To enable the documentation UI, add the `OPENAPI` setting:

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

### Browse the Documentation

After starting the server, visit:

- **Swagger UI** (interactive): `http://127.0.0.1:9527/openapi/docs`
- **ReDoc** (readable): `http://127.0.0.1:9527/openapi/redoc`
- **Raw JSON schema**: `http://127.0.0.1:9527/openapi/openapi.json`

Unfazed generates the OpenAPI 3.1 schema from your endpoint type hints automatically — parameter types, defaults, validation rules, and response models are all included. See [OpenAPI](../features/openapi.md).

## Testing the Endpoints

### Using curl

```bash
# Student list (with default pagination)
curl "http://127.0.0.1:9527/api/enroll/student-list"

# Student list (with custom pagination)
curl "http://127.0.0.1:9527/api/enroll/student-list?page=1&size=5"

# Course list
curl "http://127.0.0.1:9527/api/enroll/course-list"

# Course binding
curl -X POST "http://127.0.0.1:9527/api/enroll/bind" \
     -H "Content-Type: application/json" \
     -d '{"student_id": 1, "course_id": 1}'
```

### Using Python

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

## Next Steps

You have designed complete API endpoints with typed parameter annotations and automatic OpenAPI documentation. In the next part, we will:

- Implement the business logic in the Services layer
- Connect endpoints to the database via serializers
- Handle validation errors and edge cases

Continue to **[Part 5: Business Logic Implementation](part5.md)**.
