# 第五部分：业务逻辑实现

在上一部分中，我们定义了 API endpoint 和 schema 模型。现在将在 Services 层实现核心业务逻辑，通过 serializer 将 endpoint 与数据库连接，并使用自定义异常处理边界情况。

## Services 层

在 Unfazed 的分层架构中，**Services 层**封装业务规则，并向 Endpoints 层提供数据操作：

```
Endpoints (Controller) → Services (Business Logic) → Serializers / Models (Data)
```

这种分离使 endpoint 函数保持精简（仅负责请求解析和响应格式化），并使业务逻辑可独立测试。

## 定义自定义异常

Unfazed 内置异常层次（见 [Exceptions](../features/exception.md)）覆盖常见情况，如 `PermissionDenied` 和 `MethodNotAllowed`。对于应用特定错误，可继承 `BaseUnfazedException`：

创建 `enroll/exceptions.py`：

```python
# enroll/exceptions.py

from unfazed.exception import BaseUnfazedException


class NotFound(BaseUnfazedException):
    def __init__(self, message: str = "Resource not found", code: int = 404):
        super().__init__(message, code)


class ValidationError(BaseUnfazedException):
    def __init__(self, message: str = "Validation failed", code: int = 422):
        super().__init__(message, code)
```

这些异常携带 `message` 和数字 `code`，可在中间件中捕获并构建统一的错误响应。

## 实现 EnrollService

编辑 `enroll/services.py`：

```python
# enroll/services.py

import typing as t

from pydantic import BaseModel

from . import models as m
from . import serializers as s
from .exceptions import NotFound, ValidationError


class EnrollService:

    # --- Request context models ---

    class StudentListQuery(BaseModel):
        name__icontains: str | None = None

    class CourseListQuery(BaseModel):
        is_active: bool | None = None

    class IdCtx(BaseModel):
        id: int

    class CreateStudentCtx(BaseModel):
        name: str
        email: str
        age: int
        student_id: str

    # --- List operations ---

    @classmethod
    async def list_student(
        cls,
        page: int = 1,
        size: int = 10,
        search: str = "",
    ) -> t.Dict:
        cond = {}
        if search:
            cond = {"name__icontains": search}

        result = await s.StudentSerializer.list_from_ctx(
            cond=cond, page=page, size=size
        )
        return {
            "code": 0,
            "message": "success",
            "data": [item.model_dump() for item in result.data],
        }

    @classmethod
    async def list_course(
        cls,
        page: int = 1,
        size: int = 10,
        is_active: bool = True,
    ) -> t.Dict:
        cond = {"is_active": is_active} if is_active else {}

        result = await s.CourseSerializer.list_from_ctx(
            cond=cond, page=page, size=size
        )
        return {
            "code": 0,
            "message": "success",
            "data": [item.model_dump() for item in result.data],
        }

    # --- Detail operations ---

    @classmethod
    async def get_student(cls, student_id: int) -> t.Dict:
        student = await m.Student.get_or_none(id=student_id)
        if not student:
            raise NotFound(f"Student {student_id} does not exist")

        serialized = await s.StudentWithCoursesSerializer.retrieve_from_ctx(
            cls.IdCtx(id=student_id)
        )
        return {
            "code": 0,
            "message": "success",
            "data": serialized.model_dump(),
        }

    # --- Create operations ---

    @classmethod
    async def create_student(cls, data: "EnrollService.CreateStudentCtx") -> t.Dict:
        if await m.Student.get_or_none(student_id=data.student_id):
            raise ValidationError(f"Student ID {data.student_id} already exists")

        if await m.Student.get_or_none(email=data.email):
            raise ValidationError(f"Email {data.email} is already in use")

        student = await s.StudentSerializer.create_from_ctx(data)
        return {
            "code": 0,
            "message": "success",
            "data": student.model_dump(),
        }

    # --- Enrollment operations ---

    @classmethod
    async def bind(cls, student_id: int, course_id: int) -> t.Dict:
        student = await m.Student.get_or_none(id=student_id)
        if not student:
            raise NotFound(f"Student {student_id} does not exist")

        course = await m.Course.get_or_none(id=course_id)
        if not course:
            raise NotFound(f"Course {course_id} does not exist")

        if not course.is_active:
            raise ValidationError(f"Course {course.name} is not active")

        if await student.courses.filter(id=course_id).exists():
            raise ValidationError(
                f"Student {student.name} is already enrolled in {course.name}"
            )

        enrolled_count = await course.students.all().count()
        if enrolled_count >= course.max_students:
            raise ValidationError(f"Course {course.name} is full")

        await student.courses.add(course)

        return {
            "code": 0,
            "message": f"Student {student.name} enrolled in {course.name}",
            "data": {"student_id": student_id, "course_id": course_id},
        }

    @classmethod
    async def unbind(cls, student_id: int, course_id: int) -> t.Dict:
        student = await m.Student.get_or_none(id=student_id)
        if not student:
            raise NotFound(f"Student {student_id} does not exist")

        course = await m.Course.get_or_none(id=course_id)
        if not course:
            raise NotFound(f"Course {course_id} does not exist")

        if not await student.courses.filter(id=course_id).exists():
            raise ValidationError(
                f"Student {student.name} is not enrolled in {course.name}"
            )

        await student.courses.remove(course)

        return {
            "code": 0,
            "message": f"Student {student.name} withdrew from {course.name}",
            "data": {"student_id": student_id, "course_id": course_id},
        }
```

要点：

- `list_from_ctx(cond, page, size)` 返回 `Result`，包含 `.count`（总记录数）和 `.data`（serializer 实例列表）。见 [Serializer — list_from_ctx](../features/serializer.md#list_from_ctx)。
- `retrieve_from_ctx(ctx)` 接受带 `id` 字段的 `BaseModel`，返回 serializer 实例。见 [Serializer — retrieve_from_ctx](../features/serializer.md#retrieve_from_ctx)。
- `create_from_ctx(ctx)` 创建数据库记录并返回序列化实例。
- 自定义异常（`NotFound`、`ValidationError`）用于业务逻辑错误。

## 更新 Endpoint

现在将 endpoint 更新为调用服务层：

```python
# enroll/endpoints.py

import typing as t

from unfazed.http import HttpRequest, JsonResponse, PlainTextResponse
from unfazed.route import params as p

from . import schema as s
from .services import EnrollService


async def hello(request: HttpRequest) -> PlainTextResponse:
    """Hello World endpoint"""
    return PlainTextResponse("Hello, World!")


async def list_student(
    request: HttpRequest,
    page: t.Annotated[int, p.Query(default=1, description="页码", ge=1)],
    size: t.Annotated[int, p.Query(default=10, description="每页条数", ge=1, le=100)],
    search: t.Annotated[str, p.Query(default="", description="按姓名搜索")],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.StudentListResponse)]:
    """获取分页学生列表，支持按姓名搜索"""
    result = await EnrollService.list_student(page, size, search)
    return JsonResponse(result)


async def list_course(
    request: HttpRequest,
    page: t.Annotated[int, p.Query(default=1, description="页码", ge=1)],
    size: t.Annotated[int, p.Query(default=10, description="每页条数", ge=1, le=100)],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.CourseListResponse)]:
    """获取分页课程列表"""
    result = await EnrollService.list_course(page, size)
    return JsonResponse(result)


async def bind(
    request: HttpRequest,
    ctx: t.Annotated[s.BindRequest, p.Json()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.BindResponse)]:
    """学生选课"""
    result = await EnrollService.bind(ctx.student_id, ctx.course_id)
    return JsonResponse(result)


async def unbind(
    request: HttpRequest,
    ctx: t.Annotated[s.BindRequest, p.Json()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.BindResponse)]:
    """学生退课"""
    result = await EnrollService.unbind(ctx.student_id, ctx.course_id)
    return JsonResponse(result)
```

## 更新 Schema

在 `enroll/schema.py` 中添加创建学生的请求模型：

```python
# Add to enroll/schema.py

class CreateStudentRequest(BaseModel):
    name: str = Field(description="学生姓名", min_length=1, max_length=100)
    email: str = Field(description="邮箱地址")
    age: int = Field(description="年龄", ge=16, le=100)
    student_id: str = Field(description="学号", min_length=1, max_length=20)
```

## 更新路由

在 `enroll/routes.py` 中添加新 endpoint：

```python
# enroll/routes.py

from unfazed.route import path

from .endpoints import hello, list_student, list_course, bind, unbind

patterns = [
    path("/hello", endpoint=hello, name="hello"),

    path("/student-list", endpoint=list_student, name="list_students"),
    path("/course-list", endpoint=list_course, name="list_courses"),

    path("/bind", endpoint=bind, methods=["POST"], name="bind_course"),
    path("/unbind", endpoint=unbind, methods=["POST"], name="unbind_course"),
]
```

## 下一步

你已经实现了带数据库操作和错误处理的完整业务逻辑。下一部分我们将：

- 使用 `Requestfactory` 编写全面测试用例
- 测试 Services 层和 Endpoints 层
- 使用 pytest fixtures 和参数化测试

继续阅读 **[第六部分：测试与质量保障](part6.md)**。
