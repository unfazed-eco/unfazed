# Part 3: Data Models and Serializers

In the previous two sections, we successfully created a project and application, and implemented the Hello World API. Now we will enter the core part: using Tortoise ORM to design data models and creating corresponding serializers to handle data validation and transformation.

We will design the data structure for a student course enrollment system, which includes students, courses, and the many-to-many relationships between them.

## Data Model Design

### Business Requirements Analysis

Our student course enrollment system needs to support the following functions:
- 📚 **Course Management**: Create, update course information
- 👨‍🎓 **Student Management**: Manage student basic information
- 🔗 **Enrollment Relationships**: Students can choose multiple courses, courses can be chosen by multiple students
- 📊 **Data Tracking**: Record creation and update times

### Designing Data Models

Edit the `enroll/models.py` file:

```python
# src/backend/enroll/models.py

from tortoise import fields
from tortoise.models import Model

class Student(Model):
    """Student model"""
    
    class Meta:
        table = "students"
        table_description = "Student information table"
    
    # Basic fields
    id = fields.IntField(pk=True, description="Student ID")
    name = fields.CharField(max_length=100, description="Student name")
    email = fields.CharField(max_length=255, unique=True, description="Email address")
    age = fields.IntField(description="Age")
    student_id = fields.CharField(max_length=20, unique=True, description="Student number")
    
    # Timestamp fields
    created_at = fields.DatetimeField(auto_now_add=True, description="Creation time")
    updated_at = fields.DatetimeField(auto_now=True, description="Update time")
    
    # Relationship fields
    courses = fields.ManyToManyField(
        "models.Course", 
        related_name="students", 
        through="student_course",
        description="Enrolled courses"
    )
    
    def __str__(self):
        return f"{self.student_id} - {self.name}"


class Course(Model):
    """Course model"""
    
    class Meta:
        table = "courses"
        table_description = "Course information table"
    
    # Basic fields
    id = fields.IntField(pk=True, description="Course ID")
    name = fields.CharField(max_length=200, description="Course name")
    code = fields.CharField(max_length=20, unique=True, description="Course code")
    description = fields.TextField(description="Course description")
    credits = fields.IntField(default=3, description="Credits")
    max_students = fields.IntField(default=50, description="Maximum students")
    
    # Course status
    is_active = fields.BooleanField(default=True, description="Is active")
    
    # Timestamp fields
    created_at = fields.DatetimeField(auto_now_add=True, description="Creation time")
    updated_at = fields.DatetimeField(auto_now=True, description="Update time")
    
    # Reverse relationship declaration (for type hints)
    students: fields.ManyToManyRelation[Student]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    async def enrolled_count(self) -> int:
        """Get number of enrolled students"""
        return await self.students.all().count()
    
    @property
    async def is_full(self) -> bool:
        """Check if course is full"""
        count = await self.enrolled_count
        return count >= self.max_students
```

### Data Model Feature Analysis

**Key Field Descriptions**:

| Field Type                         | Example               | Description                       |
| ---------------------------------- | --------------------- | --------------------------------- |
| `IntField(pk=True)`                | `id`                  | Primary key field, auto-increment |
| `CharField(max_length=100)`        | `name`                | String field, specify max length  |
| `CharField(unique=True)`           | `email`, `student_id` | Unique constraint field           |
| `TextField()`                      | `description`         | Long text field                   |
| `BooleanField(default=True)`       | `is_active`           | Boolean field with default value  |
| `DatetimeField(auto_now_add=True)` | `created_at`          | Automatically set on creation     |
| `DatetimeField(auto_now=True)`     | `updated_at`          | Automatically modified on update  |
| `ManyToManyField()`                | `courses`             | Many-to-many relationship field   |

**Relationship Design**:
- **Many-to-many relationship**: `Student.courses` ↔ `Course.students`
- **Junction table**: `student_course` (automatically created)
- **Reverse queries**: Support bidirectional data queries

## Database Configuration

### Configure Database Connection

Edit `entry/settings/__init__.py`:

```python
# src/backend/entry/settings/__init__.py

import os
from pathlib import Path

# Project root directory
PROJECT_DIR = Path(__file__).resolve().parent.parent

UNFAZED_SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "Tutorial Project",
    
    # Application configuration
    "INSTALLED_APPS": [
        "enroll",
    ],
    
    # Database configuration
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

**Configuration Description**:
- **ENGINE**: Database engine (SQLite/MySQL/PostgreSQL)
- **CREDENTIALS**: Database connection credentials
- **APPS**: ORM application configuration, specify model locations and connections

### Initialize Database

Use Unfazed's integrated Aerich tool for database migration:

```bash
# Execute in backend directory

# 1. Initialize database configuration
unfazed-cli init-db

# 2. Generate and execute migrations
unfazed-cli migrate
```

**Command Description**:
- `init-db`: Initialize Aerich configuration, create migration folders
- `migrate`: Generate migration files based on models and execute them

## Serializer Design

Serializers are one of Unfazed's core features, providing data validation, transformation, and CRUD operation capabilities.

### Creating Basic Serializers

Edit the `enroll/serializers.py` file:

```python
# src/backend/enroll/serializers.py

from unfazed.serializer import Serializer
from . import models as m

class StudentSerializer(Serializer):
    """Student serializer"""
    
    class Meta:
        model = m.Student
        # Specify fields to be serialized
        include = [
            "id", "name", "email", "age", "student_id", 
            "created_at", "updated_at"
        ]
        # Enable relationship field serialization
        enable_relations = True

class CourseSerializer(Serializer):
    """Course serializer"""
    
    class Meta:
        model = m.Course
        include = [
            "id", "name", "code", "description", "credits", 
            "max_students", "is_active", "created_at", "updated_at"
        ]
        enable_relations = True

class StudentWithCoursesSerializer(Serializer):
    """Student serializer with course information"""
    
    class Meta:
        model = m.Student
        include = [
            "id", "name", "email", "age", "student_id", 
            "created_at", "updated_at", "courses"
        ]
        enable_relations = True

class CourseWithStudentsSerializer(Serializer):
    """Course serializer with student information"""
    
    class Meta:
        model = m.Course
        include = [
            "id", "name", "code", "description", "credits", 
            "max_students", "is_active", "created_at", "updated_at", "students"
        ]
        enable_relations = True
```

### Serializer Core Functions

Unfazed serializers provide rich functionality:

**1. Automatic Data Validation**
```python
# Automatic data validation based on model fields
from pydantic import BaseModel

class StudentCreateRequest(BaseModel):
    name: str
    age: int
    email: str
    student_id: str

data = StudentCreateRequest(name="John", age=20, email="john@example.com", student_id="2024001")
student = await StudentSerializer.create_from_ctx(data)
```

**2. CRUD Operation Methods**
```python
from pydantic import BaseModel

# Create
class StudentCreateRequest(BaseModel):
    name: str
    age: int
    email: str 
    student_id: str

create_data = StudentCreateRequest(name="John", age=20, email="john@example.com", student_id="2024001")
student = await StudentSerializer.create_from_ctx(create_data)

# Query list (with pagination support)
result = await StudentSerializer.list_from_ctx({}, page=1, size=10)

# Query single item
class StudentRetrieveRequest(BaseModel):
    id: int

retrieve_data = StudentRetrieveRequest(id=1)
student = await StudentSerializer.retrieve_from_ctx(retrieve_data)

# Update
class StudentUpdateRequest(BaseModel):
    id: int
    age: int

update_data = StudentUpdateRequest(id=1, age=21)
updated_student = await StudentSerializer.update_from_ctx(update_data)

# Delete
class StudentDeleteRequest(BaseModel):
    id: int

delete_data = StudentDeleteRequest(id=1)
await StudentSerializer.destroy_from_ctx(delete_data)
```

**3. Relationship Data Processing**
```python
# Get student and their enrolled courses
class StudentRetrieveRequest(BaseModel):
    id: int

retrieve_data = StudentRetrieveRequest(id=1)
student_with_courses = await StudentWithCoursesSerializer.retrieve_from_ctx(
    retrieve_data, fetch_relations=True
)
```

### Advanced Serializer Features

**Serializer Configuration Options**:

```python
class AdvancedStudentSerializer(Serializer):
    """Advanced student serializer configuration example"""
    
    class Meta:
        model = m.Student
        # Include specific fields
        include = ["id", "name", "email", "age", "student_id", "created_at", "updated_at"]
        # Enable automatic relationship field loading
        enable_relations = True

class StudentListSerializer(Serializer):
    """Simplified serializer for list display"""
    
    class Meta:
        model = m.Student
        # Only include necessary fields, improve list query performance
        include = ["id", "name", "student_id", "age"]
        # Disable relationship fields to improve performance
        enable_relations = False

class StudentDetailSerializer(Serializer):
    """Complete serializer for detail display"""
    
    class Meta:
        model = m.Student
        # Include all fields and relationships
        include = ["id", "name", "email", "age", "student_id", "created_at", "updated_at", "courses"]
        enable_relations = True
```

## Testing Data Models

Let's create some test code to verify our data models:

```python
# Can be tested in Python shell
# unfazed-cli shell

from pydantic import BaseModel
from enroll.models import Student, Course
from enroll.serializers import StudentSerializer, CourseSerializer

# Define data models
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

# Create course
course_data = CourseCreateRequest(
    name="Python Programming Basics",
    code="CS101", 
    description="Learn the basics of Python programming language",
    credits=3,
    max_students=30
)
course_result = await CourseSerializer.create_from_ctx(course_data)

# Create student
student_data = StudentCreateRequest(
    name="John",
    email="john@example.com", 
    age=20,
    student_id="2024001"
)
student_result = await StudentSerializer.create_from_ctx(student_data)

# Get model instances for relationship operations
student_instance = await Student.get(id=student_result.id)
course_instance = await Course.get(id=course_result.id)

# Student enrolls in course (through model instances)
await student_instance.courses.add(course_instance)

# Query verification
enrolled_courses = await student_instance.courses.all()
course_students = await course_instance.students.all()

print(f"Student {student_result.name} enrolled in {len(enrolled_courses)} courses")
print(f"Course {course_result.name} has {len(course_students)} students")
```

## Next Steps

Congratulations! You have successfully designed data models and serializers. In the next tutorial, we will:

- Design API interfaces (student list, course list, enrollment interface)
- Use Pydantic to define request/response models
- Learn Unfazed's parameter annotation system
- Generate automatic API documentation

Let's continue to **Part 4: API Interface Design and Schema Definition**!

---
