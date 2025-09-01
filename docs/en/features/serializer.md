Unfazed Serializer
=====

Unfazed Serializer is a powerful serializer system based on Tortoise ORM models that automatically converts database models to Pydantic models and provides complete CRUD operations. This system perfectly integrates Tortoise ORM features, supporting relationship fields, field validation, pagination queries, and other advanced functionality.

## System Overview

### Core Features

- **Automatic Model Conversion**: Automatically generates Pydantic serializers based on Tortoise ORM models
- **Complete CRUD Operations**: Built-in create, read, update, delete methods
- **Relationship Field Support**: Supports foreign keys, many-to-many, one-to-one, and other relationship fields
- **Field Customization**: Supports field override, new fields, and field filtering
- **Pagination Queries**: Built-in efficient pagination query mechanism
- **Type Safety**: Complete type annotations and Pydantic validation

### Core Components

- **Serializer**: Base serializer class providing all core functionality
- **MetaClass**: Metaclass responsible for automatically generating Pydantic models
- **create_model_from_tortoise**: Core conversion function that converts Tortoise models to Pydantic models
- **Relationship Field Handlers**: Specialized functions for handling various relationship fields

### Design Philosophy

1. **Convention over Configuration**: Most functionality works out of the box without complex configuration
2. **Type Safety**: Comprehensive type checking and validation
3. **High Performance**: Optimized query and serialization performance
4. **Flexibility**: Supports field customization and behavior extension

## Quick Start

### Basic Usage

```python
# models.py
from tortoise import Model, fields

class Student(Model):
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=255, description="Student name")
    age = fields.IntField(description="Age")
    email = fields.CharField(max_length=255, null=True, description="Email")
    is_active = fields.BooleanField(default=True, description="Is active")
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

### CRUD Operations

```python
from pydantic import BaseModel
from typing import Dict, Any

# 1. Create student
class StudentCreateData(BaseModel):
    name: str
    age: int
    email: str = None

async def create_student():
    create_data = StudentCreateData(name="John", age=20, email="john@example.com")
    student = await StudentSerializer.create_from_ctx(create_data)
    print(f"Created student: {student.name}, ID: {student.id}")
    return student

# 2. Query student
class StudentRetrieveData(BaseModel):
    id: int

async def get_student(student_id: int):
    retrieve_data = StudentRetrieveData(id=student_id)
    student = await StudentSerializer.retrieve_from_ctx(retrieve_data)
    print(f"Retrieved student: {student.name}, Age: {student.age}")
    return student

# 3. Update student
class StudentUpdateData(BaseModel):
    id: int
    name: str = None
    age: int = None
    email: str = None

async def update_student(student_id: int):
    update_data = StudentUpdateData(id=student_id, age=21)
    student = await StudentSerializer.update_from_ctx(update_data)
    print(f"Updated student: {student.name}, New age: {student.age}")
    return student

# 4. Delete student
class StudentDeleteData(BaseModel):
    id: int

async def delete_student(student_id: int):
    delete_data = StudentDeleteData(id=student_id)
    await StudentSerializer.destroy_from_ctx(delete_data)
    print(f"Deleted student ID: {student_id}")

# 5. Pagination query
async def list_students():
    # Query conditions
    conditions: Dict[str, Any] = {"is_active": True}
    
    # Pagination parameters
    page = 1
    size = 10
    
    # Query options
    result = await StudentSerializer.list_from_ctx(
        cond=conditions,
        page=page,
        size=size,
        order_by=["-created_at"],  # Order by creation time descending
        fetch_relations=True
    )
    
    print(f"Total: {result.count}")
    print(f"Current page students: {len(result.data)}")
    for student in result.data:
        print(f"- {student.name} (ID: {student.id})")
    
    return result
```

## Field Customization

### Field Override

Can override field types or properties in models:

```python
from pydantic import Field
from datetime import datetime

class StudentSerializer(Serializer):
    # Override field type
    age: str = Field(..., description="Age (string format)")
    
    # Add new field
    display_name: str = Field(default="", description="Display name")
    
    # Override field default value
    is_active: bool = Field(default=False, description="Is active")

    class Meta:
        model = Student

# Usage example
student_data = {
    "name": "Jane",
    "age": "22",  # Now string type
    "display_name": "Student Jane",
    "email": "jane@example.com"
}

student = StudentSerializer(**student_data)
print(f"Age type: {type(student.age)}")  # <class 'str'>
```

### Field Filtering

Use `include` and `exclude` to control serialized fields:

```python
# Include only specific fields
class StudentBasicSerializer(Serializer):
    class Meta:
        model = Student
        include = ["id", "name", "age"]

# Exclude specific fields
class StudentPublicSerializer(Serializer):
    class Meta:
        model = Student
        exclude = ["created_at", "updated_at"]

# Usage example
student = await StudentBasicSerializer.retrieve_from_ctx(
    StudentRetrieveData(id=1)
)
# Only includes id, name, age fields
print(student.model_dump())  # {"id": 1, "name": "John", "age": 20}
```

## Relationship Field Handling

### Define Relationship Models

```python
# models.py
class Course(Model):
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=255, description="Course name")
    code = fields.CharField(max_length=50, description="Course code")
    credits = fields.IntField(description="Credits")

class StudentCourse(Model):
    id = fields.BigIntField(primary_key=True)
    student = fields.ForeignKeyField("models.Student", related_name="enrollments")
    course = fields.ForeignKeyField("models.Course", related_name="enrollments")
    score = fields.FloatField(null=True, description="Score")
    enrolled_at = fields.DatetimeField(auto_now_add=True)

class StudentProfile(Model):
    id = fields.BigIntField(primary_key=True)
    student = fields.OneToOneField("models.Student", related_name="profile")
    phone = fields.CharField(max_length=20, null=True)
    address = fields.TextField(null=True)
    emergency_contact = fields.CharField(max_length=255, null=True)

# Update Student model
class Student(Model):
    # ... existing fields ...
    
    # Relationship fields are automatically detected
    # profile: StudentProfile (one-to-one)
    # enrollments: List[StudentCourse] (one-to-many)
```

### Relationship Field Serializers

```python
class CourseSerializer(Serializer):
    class Meta:
        model = Course

class StudentProfileSerializer(Serializer):
    class Meta:
        model = StudentProfile
        exclude = ["student"]  # Avoid circular references

class StudentCourseSerializer(Serializer):
    class Meta:
        model = StudentCourse

# Student serializer with relationship fields enabled
class StudentWithRelationsSerializer(Serializer):
    class Meta:
        model = Student
        enable_relations = True

# Manually define relationship fields (recommended approach)
class StudentDetailSerializer(Serializer):
    # Manually define relationship fields to avoid circular references
    profile: StudentProfileSerializer = None
    enrollments: List[StudentCourseSerializer] = []

    class Meta:
        model = Student
        exclude = ["created_at", "updated_at"]
```

### Relationship Queries

```python
async def get_student_with_relations():
    # Query students and their related data
    result = await StudentDetailSerializer.list_from_ctx(
        cond={"is_active": True},
        page=1,
        size=10,
        fetch_relations=True  # Automatically prefetch relationship fields
    )
    
    for student in result.data:
        print(f"Student: {student.name}")
        if student.profile:
            print(f"  Contact phone: {student.profile.phone}")
        
        print(f"  Course enrollments:")
        for enrollment in student.enrollments:
            print(f"    - Course: {enrollment.course.name}, Score: {enrollment.score}")

# Find relationships
async def find_student_course_relation():
    relation = StudentSerializer.find_relation(CourseSerializer)
    if relation:
        print(f"Relation type: {relation.relation}")
        print(f"Source field: {relation.source_field}")
        print(f"Target field: {relation.target_field}")
```

## Advanced Queries

### Complex Query Conditions

```python
from datetime import datetime, timedelta

async def advanced_queries():
    # 1. Complex filtering conditions
    conditions = {
        "age__gte": 18,  # Age greater than or equal to 18
        "age__lt": 25,   # Age less than 25
        "name__icontains": "John",  # Name contains "John"
        "is_active": True,
        "created_at__gte": datetime.now() - timedelta(days=30)  # Created in last 30 days
    }
    
    result = await StudentSerializer.list_from_ctx(
        cond=conditions,
        page=1,
        size=20,
        order_by=["-age", "name"]  # Order by age descending, name ascending
    )
    
    # 2. Use QuerySet for more complex queries
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

# Custom query methods
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

### Batch Operations

```python
async def batch_operations():
    # 1. Batch create
    students_data = [
        {"name": "Student1", "age": 20, "email": "student1@example.com"},
        {"name": "Student2", "age": 21, "email": "student2@example.com"},
        {"name": "Student3", "age": 22, "email": "student3@example.com"},
    ]
    
    created_students = []
    for data in students_data:
        create_data = StudentCreateData(**data)
        student = await StudentSerializer.create_from_ctx(create_data)
        created_students.append(student)
    
    # 2. Batch update
    for student in created_students:
        update_data = StudentUpdateData(
            id=student.id,
            age=student.age + 1
        )
        await StudentSerializer.update_from_ctx(update_data)
    
    # 3. Batch delete
    for student in created_students:
        delete_data = StudentDeleteData(id=student.id)
        await StudentSerializer.destroy_from_ctx(delete_data)
```

## Meta Configuration Details

### Configuration Options

```python
class StudentSerializer(Serializer):
    class Meta:
        model = Student                    # Required: Associated Tortoise model
        include = ["id", "name", "age"]   # Optional: List of included fields
        exclude = ["created_at"]          # Optional: List of excluded fields (mutually exclusive with include)
        enable_relations = True           # Optional: Whether to enable automatic relationship field handling

# Field inclusion example
class StudentMinimalSerializer(Serializer):
    class Meta:
        model = Student
        include = ["id", "name"]  # Only serialize id and name

# Field exclusion example  
class StudentWithoutTimestampsSerializer(Serializer):
    class Meta:
        model = Student
        exclude = ["created_at", "updated_at"]  # Exclude timestamp fields

# Relationship field enablement example
class StudentFullSerializer(Serializer):
    class Meta:
        model = Student
        enable_relations = True  # Automatically handle relationship fields
```

### Important Notes

**Relationship Field Initialization**:
- When `enable_relations = True`, serializer automatically handles relationship fields
- If `Tortoise._inited` is not initialized, relationship fields are skipped to avoid errors
- Recommend avoiding accessing serializers in `app.ready()` method, or manually define relationship fields

```python
# Recommended relationship field handling approach
class StudentSafeSerializer(Serializer):
    # Manually define relationship fields to avoid initialization issues
    profile: StudentProfileSerializer = None
    courses: List[CourseSerializer] = []

    class Meta:
        model = Student
        # Don't enable automatic relationship field handling
        enable_relations = False
```

## Best Practices

### 1. Serializer Organization

```python
# Organize serializers by functionality
class StudentListSerializer(Serializer):
    """Lightweight serializer for list display"""
    class Meta:
        model = Student
        include = ["id", "name", "age", "is_active"]

class StudentDetailSerializer(Serializer):
    """Complete serializer for detail display"""
    profile: StudentProfileSerializer = None
    
    class Meta:
        model = Student
        exclude = ["created_at", "updated_at"]

class StudentCreateSerializer(Serializer):
    """Serializer for creation"""
    class Meta:
        model = Student
        exclude = ["id", "created_at", "updated_at"]

class StudentUpdateSerializer(Serializer):
    """Serializer for updates"""
    class Meta:
        model = Student
        exclude = ["id", "created_at"]  # Allow updating updated_at
```

Through Unfazed Serializer, you can quickly build powerful, type-safe data serialization and CRUD operation systems. This system perfectly combines Tortoise ORM's database functionality with Pydantic's validation capabilities, providing a solid foundation for building high-quality Web APIs.
