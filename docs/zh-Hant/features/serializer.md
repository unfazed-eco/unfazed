Unfazed Serializer 序列化器
=====

Unfazed Serializer 是一个基于 Tortoise ORM 模型的强大序列化器系统，自动将数据库模型转换为 Pydantic 模型，并提供完整的 CRUD 操作。该系统完美集成了 Tortoise ORM 的特性，支持关系字段、字段验证、分页查询等高级功能。

## 系统概述

### 核心特性

- **自动模型转换**: 基于 Tortoise ORM 模型自动生成 Pydantic 序列化器
- **完整的 CRUD 操作**: 内置创建、读取、更新、删除的完整方法
- **关系字段支持**: 支持外键、多对多、一对一等各种关系字段
- **字段定制**: 支持字段覆盖、新增字段和字段过滤
- **分页查询**: 内置高效的分页查询机制
- **类型安全**: 完整的类型注解和 Pydantic 验证

### 核心组件

- **Serializer**: 序列化器基类，提供所有核心功能
- **MetaClass**: 元类，负责自动生成 Pydantic 模型
- **create_model_from_tortoise**: 核心转换函数，将 Tortoise 模型转换为 Pydantic 模型
- **关系字段处理器**: 处理各种关系字段的专用函数

### 设计理念

1. **约定优于配置**: 大部分功能开箱即用，无需复杂配置
2. **类型安全**: 全面的类型检查和验证
3. **高性能**: 优化的查询和序列化性能
4. **灵活性**: 支持字段定制和行为扩展

## 快速开始

### 基本使用

```python
# models.py
from tortoise import Model, fields

class Student(Model):
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=255, description="学生姓名")
    age = fields.IntField(description="年龄")
    email = fields.CharField(max_length=255, null=True, description="邮箱")
    is_active = fields.BooleanField(default=True, description="是否激活")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "students"

# serializers.py
from unfazed.serializer import Serializer
from .models import Student

class StudentSerializer(Serializer):
    class Meta:
        model = Student
```

### CRUD 操作

```python
from pydantic import BaseModel
from typing import Dict, Any

# 1. 创建学生
class StudentCreateData(BaseModel):
    name: str
    age: int
    email: str = None

async def create_student():
    create_data = StudentCreateData(name="张三", age=20, email="zhangsan@example.com")
    student = await StudentSerializer.create_from_ctx(create_data)
    print(f"创建学生: {student.name}, ID: {student.id}")
    return student

# 2. 查询学生
class StudentRetrieveData(BaseModel):
    id: int

async def get_student(student_id: int):
    retrieve_data = StudentRetrieveData(id=student_id)
    student = await StudentSerializer.retrieve_from_ctx(retrieve_data)
    print(f"查询学生: {student.name}, 年龄: {student.age}")
    return student

# 3. 更新学生
class StudentUpdateData(BaseModel):
    id: int
    name: str = None
    age: int = None
    email: str = None

async def update_student(student_id: int):
    update_data = StudentUpdateData(id=student_id, age=21)
    student = await StudentSerializer.update_from_ctx(update_data)
    print(f"更新学生: {student.name}, 新年龄: {student.age}")
    return student

# 4. 删除学生
class StudentDeleteData(BaseModel):
    id: int

async def delete_student(student_id: int):
    delete_data = StudentDeleteData(id=student_id)
    await StudentSerializer.destroy_from_ctx(delete_data)
    print(f"删除学生 ID: {student_id}")

# 5. 分页查询
async def list_students():
    # 查询条件
    conditions: Dict[str, Any] = {"is_active": True}
    
    # 分页参数
    page = 1
    size = 10
    
    # 查询选项
    result = await StudentSerializer.list_from_ctx(
        cond=conditions,
        page=page,
        size=size,
        order_by=["-created_at"],  # 按创建时间倒序
        fetch_relations=True
    )
    
    print(f"总数: {result.count}")
    print(f"当前页学生数: {len(result.data)}")
    for student in result.data:
        print(f"- {student.name} (ID: {student.id})")
    
    return result
```

## 字段定制

### 字段覆盖

可以覆盖模型中的字段类型或属性：

```python
from pydantic import Field
from datetime import datetime

class StudentSerializer(Serializer):
    # 覆盖字段类型
    age: str = Field(..., description="年龄（字符串格式）")
    
    # 添加新字段
    display_name: str = Field(default="", description="显示名称")
    
    # 覆盖字段默认值
    is_active: bool = Field(default=False, description="是否激活")

    class Meta:
        model = Student

# 使用示例
student_data = {
    "name": "李四",
    "age": "22",  # 现在是字符串类型
    "display_name": "学生李四",
    "email": "lisi@example.com"
}

student = StudentSerializer(**student_data)
print(f"年龄类型: {type(student.age)}")  # <class 'str'>
```

### 字段过滤

使用 `include` 和 `exclude` 控制序列化字段：

```python
# 只包含特定字段
class StudentBasicSerializer(Serializer):
    class Meta:
        model = Student
        include = ["id", "name", "age"]

# 排除特定字段
class StudentPublicSerializer(Serializer):
    class Meta:
        model = Student
        exclude = ["created_at", "updated_at"]

# 使用示例
student = await StudentBasicSerializer.retrieve_from_ctx(
    StudentRetrieveData(id=1)
)
# 只包含 id, name, age 字段
print(student.model_dump())  # {"id": 1, "name": "张三", "age": 20}
```

## 关系字段处理

### 定义关系模型

```python
# models.py
class Course(Model):
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=255, description="课程名称")
    code = fields.CharField(max_length=50, description="课程代码")
    credits = fields.IntField(description="学分")

class StudentCourse(Model):
    id = fields.BigIntField(primary_key=True)
    student = fields.ForeignKeyField("models.Student", related_name="enrollments")
    course = fields.ForeignKeyField("models.Course", related_name="enrollments")
    score = fields.FloatField(null=True, description="成绩")
    enrolled_at = fields.DatetimeField(auto_now_add=True)

class StudentProfile(Model):
    id = fields.BigIntField(primary_key=True)
    student = fields.OneToOneField("models.Student", related_name="profile")
    phone = fields.CharField(max_length=20, null=True)
    address = fields.TextField(null=True)
    emergency_contact = fields.CharField(max_length=255, null=True)

# 更新 Student 模型
class Student(Model):
    # ... 原有字段 ...
    
    # 关系字段会被自动检测
    # profile: StudentProfile (一对一)
    # enrollments: List[StudentCourse] (一对多)
```

### 关系字段序列化器

```python
class CourseSerializer(Serializer):
    class Meta:
        model = Course

class StudentProfileSerializer(Serializer):
    class Meta:
        model = StudentProfile
        exclude = ["student"]  # 避免循环引用

class StudentCourseSerializer(Serializer):
    class Meta:
        model = StudentCourse

# 启用关系字段的学生序列化器
class StudentWithRelationsSerializer(Serializer):
    class Meta:
        model = Student
        enable_relations = True

# 手动定义关系字段（推荐方式）
class StudentDetailSerializer(Serializer):
    # 手动定义关系字段，避免循环引用
    profile: StudentProfileSerializer = None
    enrollments: List[StudentCourseSerializer] = []

    class Meta:
        model = Student
        exclude = ["created_at", "updated_at"]
```

### 关系查询

```python
async def get_student_with_relations():
    # 查询学生及其关联数据
    result = await StudentDetailSerializer.list_from_ctx(
        cond={"is_active": True},
        page=1,
        size=10,
        fetch_relations=True  # 自动预取关系字段
    )
    
    for student in result.data:
        print(f"学生: {student.name}")
        if student.profile:
            print(f"  联系电话: {student.profile.phone}")
        
        print(f"  选课情况:")
        for enrollment in student.enrollments:
            print(f"    - 课程: {enrollment.course.name}, 成绩: {enrollment.score}")

# 查找关系
async def find_student_course_relation():
    relation = StudentSerializer.find_relation(CourseSerializer)
    if relation:
        print(f"关系类型: {relation.relation}")
        print(f"源字段: {relation.source_field}")
        print(f"目标字段: {relation.target_field}")
```

## 高级查询

### 复杂查询条件

```python
from datetime import datetime, timedelta

async def advanced_queries():
    # 1. 复杂过滤条件
    conditions = {
        "age__gte": 18,  # 年龄大于等于18
        "age__lt": 25,   # 年龄小于25
        "name__icontains": "张",  # 姓名包含"张"
        "is_active": True,
        "created_at__gte": datetime.now() - timedelta(days=30)  # 最近30天创建
    }
    
    result = await StudentSerializer.list_from_ctx(
        cond=conditions,
        page=1,
        size=20,
        order_by=["-age", "name"]  # 按年龄降序，姓名升序
    )
    
    # 2. 使用 QuerySet 进行更复杂的查询
    from tortoise.queryset import QuerySet
    
    queryset = Student.filter(
        age__gte=18,
        is_active=True
    ).select_related("profile").prefetch_related("enrollments")
    
    result = await StudentSerializer.list_from_queryset(
        queryset=queryset,
        page=1,
        size=10
    )
    
    return result

# 自定义查询方法
class StudentSerializer(Serializer):
    class Meta:
        model = Student
    
    @classmethod
    async def get_active_students_by_age_range(
        cls, 
        min_age: int, 
        max_age: int, 
        page: int = 1, 
        size: int = 10
    ):
        conditions = {
            "age__gte": min_age,
            "age__lte": max_age,
            "is_active": True
        }
        
        return await cls.list_from_ctx(
            cond=conditions,
            page=page,
            size=size,
            order_by=["age"]
        )
```

### 批量操作

```python
async def batch_operations():
    # 1. 批量创建
    students_data = [
        {"name": "学生1", "age": 20, "email": "student1@example.com"},
        {"name": "学生2", "age": 21, "email": "student2@example.com"},
        {"name": "学生3", "age": 22, "email": "student3@example.com"},
    ]
    
    created_students = []
    for data in students_data:
        create_data = StudentCreateData(**data)
        student = await StudentSerializer.create_from_ctx(create_data)
        created_students.append(student)
    
    # 2. 批量更新
    for student in created_students:
        update_data = StudentUpdateData(
            id=student.id,
            age=student.age + 1
        )
        await StudentSerializer.update_from_ctx(update_data)
    
    # 3. 批量删除
    for student in created_students:
        delete_data = StudentDeleteData(id=student.id)
        await StudentSerializer.destroy_from_ctx(delete_data)
```

## Meta 配置详解

### 配置选项

```python
class StudentSerializer(Serializer):
    class Meta:
        model = Student                    # 必需: 关联的 Tortoise 模型
        include = ["id", "name", "age"]   # 可选: 包含的字段列表
        exclude = ["created_at"]          # 可选: 排除的字段列表 (与include互斥)
        enable_relations = True           # 可选: 是否启用关系字段自动处理

# 字段包含示例
class StudentMinimalSerializer(Serializer):
    class Meta:
        model = Student
        include = ["id", "name"]  # 只序列化 id 和 name

# 字段排除示例  
class StudentWithoutTimestampsSerializer(Serializer):
    class Meta:
        model = Student
        exclude = ["created_at", "updated_at"]  # 排除时间戳字段

# 关系字段启用示例
class StudentFullSerializer(Serializer):
    class Meta:
        model = Student
        enable_relations = True  # 自动处理关系字段
```

### 注意事项

**关系字段初始化**：
- `enable_relations = True` 时，序列化器会自动处理关系字段
- 如果 `Tortoise._inited` 未初始化，关系字段会被跳过以避免错误
- 建议在 `app.ready()` 方法中避免访问序列化器，或手动定义关系字段

```python
# 推荐的关系字段处理方式
class StudentSafeSerializer(Serializer):
    # 手动定义关系字段，避免初始化问题
    profile: StudentProfileSerializer = None
    courses: List[CourseSerializer] = []

    class Meta:
        model = Student
        # 不启用自动关系字段处理
        enable_relations = False
```

## 最佳实践

### 1. 序列化器组织

```python
# 按功能组织序列化器
class StudentListSerializer(Serializer):
    """用于列表显示的轻量级序列化器"""
    class Meta:
        model = Student
        include = ["id", "name", "age", "is_active"]

class StudentDetailSerializer(Serializer):
    """用于详情显示的完整序列化器"""
    profile: StudentProfileSerializer = None
    
    class Meta:
        model = Student
        exclude = ["created_at", "updated_at"]

class StudentCreateSerializer(Serializer):
    """用于创建的序列化器"""
    class Meta:
        model = Student
        exclude = ["id", "created_at", "updated_at"]

class StudentUpdateSerializer(Serializer):
    """用于更新的序列化器"""
    class Meta:
        model = Student
        exclude = ["id", "created_at"]  # 允许更新 updated_at
```

通过 Unfazed Serializer，您可以快速构建出功能强大、类型安全的数据序列化和 CRUD 操作系统。该系统完美结合了 Tortoise ORM 的数据库功能和 Pydantic 的验证能力，为构建高质量的 Web API 提供了坚实的基础。

