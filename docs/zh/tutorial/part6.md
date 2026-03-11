# 第六部分：测试与质量保障

在前几部分中，我们构建了完整的学生选课系统。现在将编写全面测试用例，确保代码质量和可靠性。Unfazed 提供 `Requestfactory`，一个异步测试客户端，使 API 测试简单高效。完整参考见 [Test Client](../features/testclient.md)。

## 测试环境配置

### 安装测试依赖

```bash
# 使用 uv
uv add pytest pytest-asyncio pytest-cov

# 使用 pip
pip install pytest pytest-asyncio pytest-cov
```

### Pytest 配置

生成的项目包含 `conftest.py`，用于设置 `unfazed` fixture。该 fixture 创建并初始化应用实例，endpoint 测试需要：

```python
# conftest.py
import os
import sys
import typing as t

import pytest
from unfazed.core import Unfazed


@pytest.fixture(autouse=True)
async def unfazed() -> t.AsyncGenerator[Unfazed, None]:
    root_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(root_path)
    os.environ.setdefault("UNFAZED_SETTINGS_MODULE", "entry.settings")

    app = Unfazed()
    await app.setup()
    yield app
```

该 fixture 与 [Test Client — Setting Up a Pytest Fixture](../features/testclient.md#setting-up-a-pytest-fixture) 中描述的模式一致。

## 编写测试用例

### 测试数据准备

编辑 `enroll/test_all.py`：

```python
# enroll/test_all.py

import typing as t

import pytest
from unfazed.core import Unfazed
from unfazed.test import Requestfactory

from enroll import models as m
from enroll import serializers as s
from enroll.exceptions import NotFound, ValidationError
from enroll.services import EnrollService


@pytest.fixture(autouse=True)
async def setup_enroll() -> t.AsyncGenerator[None, None]:
    """每个测试前创建干净的测试数据"""
    await m.Student.all().delete()
    await m.Course.all().delete()

    students_data = [
        {"name": "Alice", "email": "alice@example.com", "age": 20, "student_id": "2024001"},
        {"name": "Bob", "email": "bob@example.com", "age": 19, "student_id": "2024002"},
        {"name": "Charlie", "email": "charlie@example.com", "age": 21, "student_id": "2024003"},
        {"name": "David", "email": "david@example.com", "age": 20, "student_id": "2024004"},
        {"name": "Eve", "email": "eve@example.com", "age": 22, "student_id": "2024005"},
        {"name": "Frank", "email": "frank@example.com", "age": 19, "student_id": "2024006"},
        {"name": "Grace", "email": "grace@example.com", "age": 20, "student_id": "2024007"},
        {"name": "Helen", "email": "helen@example.com", "age": 21, "student_id": "2024008"},
        {"name": "Ivy", "email": "ivy@example.com", "age": 20, "student_id": "2024009"},
        {"name": "Jack", "email": "jack@example.com", "age": 23, "student_id": "2024010"},
        {"name": "Kevin", "email": "kevin@example.com", "age": 19, "student_id": "2024011"},
    ]
    for data in students_data:
        await m.Student.create(**data)

    courses_data = [
        {"name": "Math", "code": "MATH101", "description": "Basic Mathematics", "credits": 3, "max_students": 5},
        {"name": "Physics", "code": "PHYS101", "description": "Introduction to Physics", "credits": 4, "max_students": 3},
        {"name": "Chemistry", "code": "CHEM101", "description": "General Chemistry", "credits": 3, "max_students": 4},
    ]
    for data in courses_data:
        await m.Course.create(**data)

    yield

    await m.Student.all().delete()
    await m.Course.all().delete()
```

### Services 层测试

直接测试业务逻辑，不经过 HTTP：

```python
class TestEnrollServices:
    """测试 EnrollService 业务逻辑"""

    async def test_list_student(self):
        result = await EnrollService.list_student(page=1, size=10)
        assert result["code"] == 0
        assert len(result["data"]) == 10

        # 第二页
        result = await EnrollService.list_student(page=2, size=10)
        assert len(result["data"]) == 1

        # 按姓名搜索
        result = await EnrollService.list_student(page=1, size=10, search="Alice")
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "Alice"

    async def test_list_course(self):
        result = await EnrollService.list_course(page=1, size=10)
        assert result["code"] == 0
        assert len(result["data"]) == 3

    async def test_get_student(self):
        student = await m.Student.get(name="Alice")

        result = await EnrollService.get_student(student.id)
        assert result["code"] == 0
        assert result["data"]["name"] == "Alice"

        # 不存在的学生
        with pytest.raises(NotFound):
            await EnrollService.get_student(99999)

    async def test_create_student(self):
        ctx = EnrollService.CreateStudentCtx(
            name="New Student",
            email="new@example.com",
            age=20,
            student_id="2024099",
        )
        result = await EnrollService.create_student(ctx)
        assert result["code"] == 0
        assert result["data"]["name"] == "New Student"

        # 重复学号
        with pytest.raises(ValidationError, match="already exists"):
            await EnrollService.create_student(ctx)

        # 重复邮箱
        ctx2 = EnrollService.CreateStudentCtx(
            name="Another", email="alice@example.com", age=21, student_id="2024100"
        )
        with pytest.raises(ValidationError, match="already in use"):
            await EnrollService.create_student(ctx2)

    async def test_bind(self):
        student = await m.Student.get(name="Alice")
        course = await m.Course.get(name="Math")

        result = await EnrollService.bind(student.id, course.id)
        assert result["code"] == 0
        assert "enrolled" in result["message"]

        # 验证关联关系
        enrolled = await student.courses.all()
        assert len(enrolled) == 1

        # 重复选课
        with pytest.raises(ValidationError, match="already enrolled"):
            await EnrollService.bind(student.id, course.id)

        # 填满课程（Math max_students=5）
        students = await m.Student.all()
        for i in range(1, 5):
            await EnrollService.bind(students[i].id, course.id)

        # 课程已满
        with pytest.raises(ValidationError, match="full"):
            await EnrollService.bind(students[5].id, course.id)

        # 不存在的学生/课程
        with pytest.raises(NotFound):
            await EnrollService.bind(99999, course.id)
        with pytest.raises(NotFound):
            await EnrollService.bind(student.id, 99999)

    async def test_unbind(self):
        student = await m.Student.get(name="Bob")
        course = await m.Course.get(name="Physics")

        # 先选课
        await EnrollService.bind(student.id, course.id)

        # 退课
        result = await EnrollService.unbind(student.id, course.id)
        assert result["code"] == 0
        assert "withdrew" in result["message"]

        enrolled = await student.courses.all()
        assert len(enrolled) == 0

        # 再次退课 — 未选课
        with pytest.raises(ValidationError, match="not enrolled"):
            await EnrollService.unbind(student.id, course.id)
```

### Endpoints 层测试

使用 `Requestfactory` 测试完整 HTTP 请求-响应流程：

```python
class TestEnrollEndpoints:
    """通过 HTTP 测试 API endpoint"""

    async def test_hello(self, unfazed: Unfazed):
        async with Requestfactory(unfazed) as client:
            resp = await client.get("/api/enroll/hello")
            assert resp.status_code == 200
            assert resp.text == "Hello, World!"

    async def test_student_list(self, unfazed: Unfazed):
        async with Requestfactory(unfazed) as client:
            resp = await client.get("/api/enroll/student-list")
            assert resp.status_code == 200

            data = resp.json()
            assert data["code"] == 0
            assert len(data["data"]) == 10

            # 带分页
            resp = await client.get(
                "/api/enroll/student-list", params={"page": 2, "size": 5}
            )
            data = resp.json()
            assert len(data["data"]) == 5

            # 带搜索
            resp = await client.get(
                "/api/enroll/student-list", params={"search": "Alice"}
            )
            data = resp.json()
            assert len(data["data"]) == 1

    async def test_course_list(self, unfazed: Unfazed):
        async with Requestfactory(unfazed) as client:
            resp = await client.get("/api/enroll/course-list")
            assert resp.status_code == 200

            data = resp.json()
            assert data["code"] == 0
            assert len(data["data"]) == 3

    async def test_bind(self, unfazed: Unfazed):
        student = await m.Student.get(name="Charlie")
        course = await m.Course.get(name="Chemistry")

        async with Requestfactory(unfazed) as client:
            resp = await client.post(
                "/api/enroll/bind",
                json={"student_id": student.id, "course_id": course.id},
            )
            assert resp.status_code == 200

            data = resp.json()
            assert data["code"] == 0

            # 重复绑定
            resp = await client.post(
                "/api/enroll/bind",
                json={"student_id": student.id, "course_id": course.id},
            )
            assert resp.status_code == 200
            # 异常被捕获并作为错误响应返回

    async def test_unbind(self, unfazed: Unfazed):
        student = await m.Student.get(name="David")
        course = await m.Course.get(name="Math")

        async with Requestfactory(unfazed) as client:
            # 先选课
            await client.post(
                "/api/enroll/bind",
                json={"student_id": student.id, "course_id": course.id},
            )

            # 再退课
            resp = await client.post(
                "/api/enroll/unbind",
                json={"student_id": student.id, "course_id": course.id},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["code"] == 0
```

## 运行测试

### 基本命令

```bash
# 运行所有测试
pytest

# 运行指定测试文件
pytest enroll/test_all.py

# 运行指定测试类
pytest enroll/test_all.py::TestEnrollServices

# 运行指定测试方法
pytest enroll/test_all.py::TestEnrollServices::test_bind

# 详细输出
pytest -v

# 带覆盖率报告
pytest --cov=enroll --cov-report=term-missing
```

### 使用 Makefile

```bash
make test          # 运行所有测试
```

## 测试覆盖率

使用 `--cov` 运行测试后，你会看到类似输出：

```
---------- coverage ----------
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
enroll/__init__.py          0      0   100%
enroll/endpoints.py        32      0   100%
enroll/exceptions.py        8      0   100%
enroll/models.py           24      0   100%
enroll/serializers.py      16      0   100%
enroll/services.py         72      2    97%   45, 78
enroll/routes.py            8      0   100%
-----------------------------------------------------
TOTAL                     160      2    99%
```

生成 HTML 报告：

```bash
pytest --cov=enroll --cov-report=html
open htmlcov/index.html
```

## 测试最佳实践

### 使用描述性测试名称

```python
async def test_bind_raises_when_course_is_full():
    ...

async def test_unbind_raises_when_not_enrolled():
    ...
```

### 使用参数化测试

```python
@pytest.mark.parametrize("page,size,expected_count", [
    (1, 5, 5),
    (2, 5, 5),
    (3, 5, 1),
    (1, 20, 11),
])
async def test_student_pagination(page, size, expected_count):
    result = await EnrollService.list_student(page, size)
    assert len(result["data"]) == expected_count
```

### 使用 Fixture 进行通用准备

```python
@pytest.fixture
async def enrolled_student():
    student = await m.Student.create(
        name="Enrolled", email="enrolled@test.com", age=20, student_id="EN001"
    )
    course = await m.Course.create(
        name="Test Course", code="TC001", description="Test",
        credits=3, max_students=10,
    )
    await student.courses.add(course)
    return student, course


async def test_unbind_with_fixture(enrolled_student):
    student, course = enrolled_student
    result = await EnrollService.unbind(student.id, course.id)
    assert result["code"] == 0
```

## 总结

在本系列教程中，我们使用 Unfazed 构建了完整的学生选课系统，涵盖：

1. **[第一部分](part1.md)**：项目创建与环境配置
2. **[第二部分](part2.md)**：应用创建与 Hello World
3. **[第三部分](part3.md)**：数据模型（Tortoise ORM）与 serializer
4. **[第四部分](part4.md)**：带类型化参数注解和 OpenAPI 的 API endpoint
5. **[第五部分](part5.md)**：Services 层业务逻辑
6. **[第六部分](part6.md)**：使用 `Requestfactory` 和 pytest 进行测试

### 延伸阅读

更多功能细节见功能文档：

| 主题                | 文档                                          |
| -------------------- | --------------------------------------------- |
| App System           | [App](../features/app.md)                     |
| Routing              | [Routing](../features/route.md)               |
| Endpoints            | [Endpoint](../features/endpoint.md)            |
| Request / Response   | [Request](../features/request.md), [Response](../features/response.md) |
| Serializer           | [Serializer](../features/serializer.md)       |
| Tortoise ORM         | [Tortoise ORM](../features/tortoise-orm.md)   |
| OpenAPI              | [OpenAPI](../features/openapi.md)             |
| Exceptions           | [Exceptions](../features/exception.md)        |
| Test Client          | [Test Client](../features/testclient.md)      |
| Settings             | [Settings](../features/settings.md)            |
| Middleware           | [Middleware](../features/middleware.md)       |
| Commands             | [Command](../features/command.md)              |
| Cache                | [Cache](../features/cache.md)                 |
| Lifespan             | [Lifespan](../features/lifespan.md)           |
| Logging              | [Logging](../features/logging.md)             |
| Session              | [Session](../features/contrib/session.md)     |
| Authentication       | [Auth](../features/contrib/auth.md)           |
| Admin Panel          | [Admin](../features/contrib/admin.md)         |
