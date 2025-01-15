services
====

在上一节中已经定义好了 schema 和 endpoints，本节将阐述如何实现业务逻辑

在 unfazed 的文件设计中，services.py 的作用是实现具体的业务逻辑共 endpoints 调用


### services 实现

services 业务逻辑实现如下

```python

import typing as t

from . import models as m
from . import serializers as s


class EnrollService:
    @classmethod
    async def list_student(
        cls,
        page: int,
        size: int,
    ) -> t.Dict:
        result = await s.StudentSerializer.list_from_ctx({}, page, size)

        return {
            "status": "ok",
            "message": "student list",
            "data": result.data,
        }

    @classmethod
    async def list_course(
        cls,
        page: int,
        size: int,
    ) -> t.Dict:
        result = await s.CourseSerializer.list_from_ctx({}, page, size)

        return {
            "status": "ok",
            "message": "course list",
            "data": result.data,
        }

    @classmethod
    async def bind(
        cls,
        student_id: int,
        course_id: int,
    ) -> t.Dict:
        student = await m.Student.get_or_none(id=student_id)
        course = await m.Course.get_or_none(id=course_id)

        if not student:
            raise ValueError(f"student {student_id} not found")

        if not course:
            raise ValueError(f"course {course_id} not found")

        await student.courses.add(course)

        return {
            "status": "ok",
            "message": "bind success",
            "data": {},
        }

```

### 注册到 endpoints 里


将 EnrollService 下的方法写到 endpoints 中的接口中


```python

import typing as t

from unfazed.http import HttpRequest, JsonResponse, PlainTextResponse
from unfazed.route import params as p

from . import schema as s
from . import services as svc


async def hello(request: HttpRequest) -> PlainTextResponse:
    return PlainTextResponse("Hello, world!")


async def list_student(
    request: HttpRequest,
    page: t.Annotated[int, p.Query(default=1)],
    size: t.Annotated[int, p.Query(default=10)],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.StudentListResponse)]:
    ret = await svc.EnrollService.list_student(page, size)
    return JsonResponse(ret)


async def list_course(
    request: HttpRequest,
    page: t.Annotated[int, p.Query(default=1)],
    size: t.Annotated[int, p.Query(default=10)],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.CourseListResponse)]:
    ret = await svc.EnrollService.list_course(page, size)
    return JsonResponse(ret)


async def bind(
    request: HttpRequest,
    ctx: t.Annotated[s.BindRequest, p.Json()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.BindResponse)]:
    ret = await svc.EnrollService.bind(ctx.student_id, ctx.course_id)
    return JsonResponse(ret)


```

至此，我们就完成了所有的业务代码，接下来将对已经写好的代码进行测试。
