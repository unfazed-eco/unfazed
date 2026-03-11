# 第三部分：数据模型与 Serializer

在前几部分中，我们创建了项目和应用，并实现了 Hello World API。现在我们将使用 Tortoise ORM 设计数据模型，并创建提供自动 CRUD 操作的 serializer。

我们将设计学生选课系统的数据结构：学生、课程以及它们之间的多对多关系。

## 数据模型设计

### 业务需求

选课系统需要支持：

- **课程管理**：创建和管理课程信息
- **学生管理**：管理学生记录
- **选课关系**：学生可选修多门课程；课程可有多个学生
- **时间戳**：记录创建和更新时间

### 定义模型

编辑 `enroll/models.py`：

```python
# enroll/models.py

from tortoise import fields
from tortoise.models import Model


class Student(Model):
    class Meta:
        table = "students"

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    email = fields.CharField(max_length=255, unique=True)
    age = fields.IntField()
    student_id = fields.CharField(max_length=20, unique=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    courses = fields.ManyToManyField(
        "models.Course",
        related_name="students",
        through="student_course",
    )

    def __str__(self):
        return f"{self.student_id} - {self.name}"


class Course(Model):
    class Meta:
        table = "courses"

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200)
    code = fields.CharField(max_length=20, unique=True)
    description = fields.TextField()
    credits = fields.IntField(default=3)
    max_students = fields.IntField(default=50)
    is_active = fields.BooleanField(default=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    students: fields.ManyToManyRelation["Student"]

    def __str__(self):
        return f"{self.code} - {self.name}"
```

Unfazed 会自动发现已安装应用中的 `models.py` 并注册到 Tortoise ORM。完整参考见 [Tortoise ORM](../features/tortoise-orm.md)。

### 主要字段类型

| 字段类型                         | 示例               | 说明                       |
| -------------------------------- | ------------------ | -------------------------- |
| `IntField(pk=True)`              | `id`               | 主键，自增                 |
| `CharField(max_length=100)`      | `name`             | 带最大长度的字符串字段     |
| `CharField(unique=True)`         | `email`, `student_id` | 唯一约束字段               |
| `TextField()`                    | `description`      | 长文本字段                 |
| `BooleanField(default=True)`     | `is_active`        | 带默认值的布尔字段         |
| `DatetimeField(auto_now_add=True)` | `created_at`      | 创建时自动设置             |
| `DatetimeField(auto_now=True)`   | `updated_at`       | 更新时自动设置             |
| `ManyToManyField()`              | `courses`          | 多对多关系                 |

### 关系设计

- `Student.courses` 与 `Course.students` 构成多对多关系
- 中间表 `student_course` 由 Tortoise ORM 自动创建
- 支持双向查询（如 `student.courses.all()`、`course.students.all()`）

## 数据库配置

### 配置数据库连接

编辑 `entry/settings/__init__.py`，添加 `DATABASE` 配置：

```python
# entry/settings/__init__.py

import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

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
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "tortoise.backends.sqlite",
                "CREDENTIALS": {
                    "FILE_PATH": os.path.join(PROJECT_DIR, "db.sqlite3"),
                },
            }
        },
    },
}
```

所有支持的引擎和凭证配置见 [Tortoise ORM — Database Configuration](../features/tortoise-orm.md#database-configuration)。

### 初始化并迁移数据库

Unfazed 使用 [Aerich](https://github.com/tortoise/aerich) 进行数据库迁移。在 backend 目录下执行：

```bash
# 1. 初始化迁移目录（仅首次）
unfazed-cli init-db

# 2. 根据模型变更生成迁移
unfazed-cli migrate --name initial

# 3. 应用迁移
unfazed-cli upgrade
```

完整命令参考见 [Tortoise ORM — Migration Commands](../features/tortoise-orm.md#migration-commands)。

## Serializer 设计

Serializer 连接数据库模型与 API 层。它们从 Tortoise 模型自动生成 Pydantic 字段，并提供内置的异步 CRUD 操作。完整参考见 [Serializer](../features/serializer.md)。

### 创建 Serializer

编辑 `enroll/serializers.py`：

```python
# enroll/serializers.py

from unfazed.serializer import Serializer

from . import models as m


class StudentSerializer(Serializer):
    class Meta:
        model = m.Student
        include = [
            "id", "name", "email", "age", "student_id",
            "created_at", "updated_at",
        ]


class CourseSerializer(Serializer):
    class Meta:
        model = m.Course
        include = [
            "id", "name", "code", "description", "credits",
            "max_students", "is_active", "created_at", "updated_at",
        ]


class StudentWithCoursesSerializer(Serializer):
    class Meta:
        model = m.Student
        include = [
            "id", "name", "email", "age", "student_id",
            "created_at", "updated_at", "courses",
        ]
        enable_relations = True


class CourseWithStudentsSerializer(Serializer):
    class Meta:
        model = m.Course
        include = [
            "id", "name", "code", "description", "credits",
            "max_students", "is_active", "created_at", "updated_at", "students",
        ]
        enable_relations = True
```

### Meta 选项

| 选项             | 类型         | 默认值 | 说明                                          |
| ---------------- | ------------ | ------ | --------------------------------------------- |
| `model`          | `Type[Model]`| 必需   | 要序列化的 Tortoise ORM 模型。                |
| `include`        | `List[str]`  | `[]`   | 要包含的字段。设置后，其他字段会被排除。       |
| `exclude`        | `List[str]`  | `[]`   | 要排除的字段。不能与 `include` 同时使用。      |
| `enable_relations` | `bool`       | `False` | 为 FK、M2M、O2O 关系生成字段。               |

### 使用 CRUD 操作

所有 CRUD 方法都是类方法，接受 Pydantic `BaseModel` 作为上下文：

```python
from pydantic import BaseModel
from enroll.serializers import StudentSerializer, CourseSerializer


# --- Create ---

class CreateStudent(BaseModel):
    name: str
    email: str
    age: int
    student_id: str

student = await StudentSerializer.create_from_ctx(
    CreateStudent(name="Alice", email="alice@example.com", age=20, student_id="2024001")
)
# student is a StudentSerializer instance


# --- Retrieve ---

class StudentId(BaseModel):
    id: int

student = await StudentSerializer.retrieve_from_ctx(StudentId(id=1))


# --- Update ---

class UpdateStudent(BaseModel):
    id: int
    age: int

updated = await StudentSerializer.update_from_ctx(
    UpdateStudent(id=1, age=21)
)


# --- Delete ---

await StudentSerializer.destroy_from_ctx(StudentId(id=1))


# --- List with pagination ---

result = await StudentSerializer.list_from_ctx(
    cond={},
    page=1,
    size=10,
)
# result.count — 匹配记录总数
# result.data  — StudentSerializer 实例列表
```

### 关联数据

检索时包含关联对象，可使用 `enable_relations = True` 的 serializer：

```python
class StudentId(BaseModel):
    id: int

student_with_courses = await StudentWithCoursesSerializer.retrieve_from_ctx(
    StudentId(id=1)
)
# student_with_courses.courses 包含已选课程数据
```

## 测试模型

可使用 Unfazed shell 交互式验证模型：

```bash
unfazed-cli shell
```

```python
from pydantic import BaseModel
from enroll.models import Student, Course
from enroll.serializers import StudentSerializer, CourseSerializer


class CreateCourse(BaseModel):
    name: str
    code: str
    description: str
    credits: int
    max_students: int

class CreateStudent(BaseModel):
    name: str
    email: str
    age: int
    student_id: str


# Create a course
course = await CourseSerializer.create_from_ctx(
    CreateCourse(
        name="Python Programming",
        code="CS101",
        description="Learn the basics of Python",
        credits=3,
        max_students=30,
    )
)

# Create a student
student = await StudentSerializer.create_from_ctx(
    CreateStudent(
        name="Alice",
        email="alice@example.com",
        age=20,
        student_id="2024001",
    )
)

# Enroll the student in the course (via model instances)
student_instance = await Student.get(id=student.id)
course_instance = await Course.get(id=course.id)
await student_instance.courses.add(course_instance)

# Verify the relationship
enrolled_courses = await student_instance.courses.all()
course_students = await course_instance.students.all()

print(f"Student {student.name} enrolled in {len(enrolled_courses)} courses")
print(f"Course {course.name} has {len(course_students)} students")
```

## 下一步

你已经设计了数据模型和带内置 CRUD 操作的 serializer。下一部分我们将：

- 使用类型化参数注解设计 API endpoint
- 定义用于 OpenAPI 文档的请求/响应 schema
- 学习 Unfazed 的参数系统（`Path`、`Query`、`Json` 等）

继续阅读 **[第四部分：API 接口设计与 Schema 定义](part4.md)**。
