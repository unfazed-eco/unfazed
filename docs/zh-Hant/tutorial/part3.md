# 第三部分：数据模型与序列化器

在前两节中，我们成功创建了项目和应用，并实现了 Hello World API。现在我们将进入核心部分：使用 Tortoise ORM 设计数据模型，并创建对应的序列化器来处理数据验证和转换。

我们将为学生选课系统设计数据结构，这个系统包含学生、课程以及它们之间的多对多关系。

## 数据模型设计

### 业务需求分析

我们的学生选课系统需要支持以下功能：
- 📚 **课程管理**：创建、更新课程信息
- 👨‍🎓 **学生管理**：管理学生基本信息
- 🔗 **选课关系**：学生可以选择多门课程，课程可以被多个学生选择
- 📊 **数据追踪**：记录创建和更新时间

### 设计数据模型

编辑 `enroll/models.py` 文件：

```python
# src/backend/enroll/models.py

from tortoise import fields
from tortoise.models import Model

class Student(Model):
    """学生模型"""
    
    class Meta:
        table = "students"
        table_description = "学生信息表"
    
    # 基本字段
    id = fields.IntField(pk=True, description="学生ID")
    name = fields.CharField(max_length=100, description="学生姓名")
    email = fields.CharField(max_length=255, unique=True, description="邮箱地址")
    age = fields.IntField(description="年龄")
    student_id = fields.CharField(max_length=20, unique=True, description="学号")
    
    # 时间戳字段
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    
    # 关系字段
    courses = fields.ManyToManyField(
        "models.Course", 
        related_name="students", 
        through="student_course",
        description="选修的课程"
    )
    
    def __str__(self):
        return f"{self.student_id} - {self.name}"


class Course(Model):
    """课程模型"""
    
    class Meta:
        table = "courses"
        table_description = "课程信息表"
    
    # 基本字段
    id = fields.IntField(pk=True, description="课程ID")
    name = fields.CharField(max_length=200, description="课程名称")
    code = fields.CharField(max_length=20, unique=True, description="课程代码")
    description = fields.TextField(description="课程描述")
    credits = fields.IntField(default=3, description="学分")
    max_students = fields.IntField(default=50, description="最大学生数")
    
    # 课程状态
    is_active = fields.BooleanField(default=True, description="是否激活")
    
    # 时间戳字段
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    
    # 反向关系声明（用于类型提示）
    students: fields.ManyToManyRelation[Student]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    async def enrolled_count(self) -> int:
        """获取已选课学生数量"""
        return await self.students.all().count()
    
    @property
    async def is_full(self) -> bool:
        """检查课程是否已满"""
        count = await self.enrolled_count
        return count >= self.max_students
```

### 数据模型特性解析

**关键字段说明**：

| 字段类型                           | 示例                  | 说明                     |
| ---------------------------------- | --------------------- | ------------------------ |
| `IntField(pk=True)`                | `id`                  | 主键字段，自动递增       |
| `CharField(max_length=100)`        | `name`                | 字符串字段，指定最大长度 |
| `CharField(unique=True)`           | `email`, `student_id` | 唯一约束字段             |
| `TextField()`                      | `description`         | 长文本字段               |
| `BooleanField(default=True)`       | `is_active`           | 布尔字段，带默认值       |
| `DatetimeField(auto_now_add=True)` | `created_at`          | 创建时自动设置           |
| `DatetimeField(auto_now=True)`     | `updated_at`          | 更新时自动修改           |
| `ManyToManyField()`                | `courses`             | 多对多关系字段           |

**关系设计**：
- **多对多关系**：`Student.courses` ↔ `Course.students`
- **中间表**：`student_course`（自动创建）
- **反向查询**：支持双向数据查询

## 数据库配置

### 配置数据库连接

编辑 `entry/settings/__init__.py`：

```python
# src/backend/entry/settings/__init__.py

import os
from pathlib import Path

# 项目根目录
PROJECT_DIR = Path(__file__).resolve().parent.parent

UNFAZED_SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "Tutorial Project",
    
    # 应用配置
    "INSTALLED_APPS": [
        "enroll",
    ],
    
    # 数据库配置
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "tortoise.backends.sqlite",
                "CREDENTIALS": {
                    "FILE_PATH": os.path.join(PROJECT_DIR, "db.sqlite3"),
                },
            }
        },
    }
}
```

**配置说明**：
- **ENGINE**: 数据库引擎（SQLite/MySQL/PostgreSQL）
- **CREDENTIALS**: 数据库连接凭据
- **APPS**: ORM 应用配置，指定模型位置和连接

### 初始化数据库

使用 Unfazed 集成的 Aerich 工具进行数据库迁移：

```bash
# 在 backend 目录下执行

# 1. 初始化数据库配置
unfazed-cli init-db

# 2. 生成并执行迁移
unfazed-cli migrate
```

**命令说明**：
- `init-db`: 初始化 Aerich 配置，创建迁移文件夹
- `migrate`: 根据模型生成迁移文件并执行

## 序列化器设计

序列化器是 Unfazed 的核心功能之一，它提供了数据验证、转换和 CRUD 操作的能力。

### 创建基础序列化器

编辑 `enroll/serializers.py` 文件：

```python
# src/backend/enroll/serializers.py

from unfazed.serializer import Serializer
from . import models as m

class StudentSerializer(Serializer):
    """学生序列化器"""
    
    class Meta:
        model = m.Student
        # 指定需要序列化的字段
        include = [
            "id", "name", "email", "age", "student_id", 
            "created_at", "updated_at"
        ]
        # 启用关系字段序列化
        enable_relations = True

class CourseSerializer(Serializer):
    """课程序列化器"""
    
    class Meta:
        model = m.Course
        include = [
            "id", "name", "code", "description", "credits", 
            "max_students", "is_active", "created_at", "updated_at"
        ]
        enable_relations = True

class StudentWithCoursesSerializer(Serializer):
    """包含课程信息的学生序列化器"""
    
    class Meta:
        model = m.Student
        include = [
            "id", "name", "email", "age", "student_id", 
            "created_at", "updated_at", "courses"
        ]
        enable_relations = True

class CourseWithStudentsSerializer(Serializer):
    """包含学生信息的课程序列化器"""
    
    class Meta:
        model = m.Course
        include = [
            "id", "name", "code", "description", "credits", 
            "max_students", "is_active", "created_at", "updated_at", "students"
        ]
        enable_relations = True
```

### 序列化器核心功能

Unfazed 序列化器提供了丰富的功能：

**1. 自动数据验证**
```python
# 自动根据模型字段进行数据验证
from pydantic import BaseModel

class StudentCreateRequest(BaseModel):
    name: str
    age: int
    email: str
    student_id: str

data = StudentCreateRequest(name="张三", age=20, email="zhangsan@example.com", student_id="2024001")
student = await StudentSerializer.create_from_ctx(data)
```

**2. CRUD 操作方法**
```python
from pydantic import BaseModel

# 创建
class StudentCreateRequest(BaseModel):
    name: str
    age: int
    email: str 
    student_id: str

create_data = StudentCreateRequest(name="张三", age=20, email="zhangsan@example.com", student_id="2024001")
student = await StudentSerializer.create_from_ctx(create_data)

# 查询列表（支持分页）
result = await StudentSerializer.list_from_ctx({}, page=1, size=10)

# 查询单个
class StudentRetrieveRequest(BaseModel):
    id: int

retrieve_data = StudentRetrieveRequest(id=1)
student = await StudentSerializer.retrieve_from_ctx(retrieve_data)

# 更新
class StudentUpdateRequest(BaseModel):
    id: int
    age: int

update_data = StudentUpdateRequest(id=1, age=21)
updated_student = await StudentSerializer.update_from_ctx(update_data)

# 删除
class StudentDeleteRequest(BaseModel):
    id: int

delete_data = StudentDeleteRequest(id=1)
await StudentSerializer.destroy_from_ctx(delete_data)
```

**3. 关系数据处理**
```python
# 获取学生及其选修的课程
class StudentRetrieveRequest(BaseModel):
    id: int

retrieve_data = StudentRetrieveRequest(id=1)
student_with_courses = await StudentWithCoursesSerializer.retrieve_from_ctx(
    retrieve_data, fetch_relations=True
)
```

### 高级序列化器功能

**序列化器配置选项**：

```python
class AdvancedStudentSerializer(Serializer):
    """高级学生序列化器配置示例"""
    
    class Meta:
        model = m.Student
        # 包含特定字段
        include = ["id", "name", "email", "age", "student_id", "created_at", "updated_at"]
        # 启用关系字段自动加载
        enable_relations = True

class StudentListSerializer(Serializer):
    """用于列表显示的精简序列化器"""
    
    class Meta:
        model = m.Student
        # 只包含必要字段，提升列表查询性能
        include = ["id", "name", "student_id", "age"]
        # 禁用关系字段以提升性能
        enable_relations = False

class StudentDetailSerializer(Serializer):
    """用于详情显示的完整序列化器"""
    
    class Meta:
        model = m.Student
        # 包含所有字段和关系
        include = ["id", "name", "email", "age", "student_id", "created_at", "updated_at", "courses"]
        enable_relations = True
```

## 测试数据模型

让我们创建一些测试代码来验证我们的数据模型：

```python
# 可以在 Python shell 中测试
# unfazed-cli shell

from pydantic import BaseModel
from enroll.models import Student, Course
from enroll.serializers import StudentSerializer, CourseSerializer

# 定义数据模型
class CourseCreateRequest(BaseModel):
    name: str
    code: str
    description: str
    credits: int
    max_students: int

class StudentCreateRequest(BaseModel):
    name: str
    email: str
    age: int
    student_id: str

# 创建课程
course_data = CourseCreateRequest(
    name="Python 编程基础",
    code="CS101", 
    description="学习 Python 编程语言的基础知识",
    credits=3,
    max_students=30
)
course_result = await CourseSerializer.create_from_ctx(course_data)

# 创建学生
student_data = StudentCreateRequest(
    name="张三",
    email="zhangsan@example.com", 
    age=20,
    student_id="2024001"
)
student_result = await StudentSerializer.create_from_ctx(student_data)

# 获取模型实例进行关系操作
student_instance = await Student.get(id=student_result.id)
course_instance = await Course.get(id=course_result.id)

# 学生选课（通过模型实例）
await student_instance.courses.add(course_instance)

# 查询验证
enrolled_courses = await student_instance.courses.all()
course_students = await course_instance.students.all()

print(f"学生 {student_result.name} 选修了 {len(enrolled_courses)} 门课程")
print(f"课程 {course_result.name} 有 {len(course_students)} 个学生")
```

## 下一步

恭喜！你已经成功设计了数据模型和序列化器。在下一个教程中，我们将：

- 设计 API 接口（学生列表、课程列表、选课接口）
- 使用 Pydantic 定义请求/响应模型
- 学习 Unfazed 的参数注解系统
- 生成自动 API 文档

让我们继续前往 **第四部分：API 接口设计与 Schema 定义**！

---
