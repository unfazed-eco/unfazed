# Part 4: API Interface Design and Schema Definition

In the previous section, we successfully designed data models and serializers. Now we will create complete API interfaces, learn how to use Unfazed's parameter annotation system, define request/response models, and generate automated API documentation.

We will create three core interfaces for the student course enrollment system, showcasing Unfazed's modern API development approach.

## API Interface Design

### Interface Planning

Based on the business logic of student course enrollment, we need to design the following interfaces:

| Interface Path         | HTTP Method | Function Description   | Parameter Type                |
| ---------------------- | ----------- | ---------------------- | ----------------------------- |
| `/enroll/student-list` | GET         | Get student list       | Query parameters (pagination) |
| `/enroll/course-list`  | GET         | Get course list        | Query parameters (pagination) |
| `/enroll/bind`         | POST        | Student course binding | JSON request body             |

### API Design Principles

Different teams have different design specifications. Taking the team where the unfazed author works as an example, we don't use RESTful style and follow these practices:

- ✅ **HTTP Method**: Only use GET/POST methods
- ✅ **URL**: /api/v1{version}/enroll{app-label}/student-list{resource-action}
- ✅ **Status Code**: HTTP status codes are all 200, return code field in response body, code 0 means success, other values mean failure
- ✅ **Response Body**: Unified response body structure, including message, data, code fields


## Schema Definition

Schema is the data contract of the API, defining the data structure of requests and responses.

### Creating Basic Schema

Edit the `enroll/schema.py` file:

```python
# src/backend/enroll/schema.py

import typing as t
from pydantic import BaseModel, Field
from .serializers import StudentSerializer, CourseSerializer

class BaseResponse[T](BaseModel):
    """Unified response base class"""
    code: int = Field(0, description="Response code")
    message: str = Field("", description="Response message")
    data: T = Field(description="Response data")

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(description="Current page number")
    size: int = Field(description="Items per page")
    total: int = Field(description="Total records")
    total_pages: int = Field(description="Total pages")

class StudentListResponse(BaseResponse[t.List[StudentSerializer]]):
    """Student list response"""
    pass


class CourseListResponse(BaseResponse[t.List[CourseSerializer]]):
    """Course list response"""
    pass


class BindRequest(BaseModel):
    """Course binding request"""
    student_id: int = Field(description="Student ID", gt=0)
    course_id: int = Field(description="Course ID", gt=0)

class BindResponse(BaseResponse[t.Dict]):
    """Course binding response"""
    pass

class StudentDetailResponse(BaseResponse[StudentSerializer]):
    """Student detail response"""
    pass

class CourseDetailResponse(BaseResponse[CourseSerializer]):
    """Course detail response"""
    pass
```

## Endpoint Implementation

### Understanding Unfazed Parameter Annotations

Unfazed uses Python's `Annotated` type annotations to declare API parameters:

```python
import typing as t
from unfazed.route import params as p

# Query parameters (URL query string)
page: t.Annotated[int, p.Query(default=1)] 

# Path parameters (URL path variables)
user_id: t.Annotated[int, p.Path()]

# JSON request body
data: t.Annotated[UserCreateRequest, p.Json()]

# Form data
form: t.Annotated[UserForm, p.Form()]

# File upload
file: t.Annotated[UploadFile, p.File()]

# Response specification
-> t.Annotated[JsonResponse, p.ResponseSpec(model=UserResponse)]
```

### Implementing View Functions

Edit the `enroll/endpoints.py` file:

```python
# src/backend/enroll/endpoints.py

import typing as t
import time
from unfazed.http import HttpRequest, JsonResponse, PlainTextResponse
from unfazed.route import params as p
from . import schema as s

# Keep the previous hello function
async def hello(request: HttpRequest) -> PlainTextResponse:
    """Hello World interface"""
    return PlainTextResponse("Hello, World!")

async def list_student(
    request: HttpRequest,
    page: t.Annotated[int, p.Query(default=1, description="Page number", ge=1)],
    size: t.Annotated[int, p.Query(default=10, description="Items per page", ge=1, le=100)],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.StudentListResponse)]:
    """
    Get student list
    
    - **page**: Page number, starting from 1
    - **size**: Items per page, range 1-100
    """
    # Return empty data for now, will implement specific logic in next section
    return JsonResponse({
        "message": "Get student list successfully",
        "data": [],
        "code": 0,
    })

async def list_course(
    request: HttpRequest,
    page: t.Annotated[int, p.Query(default=1, description="Page number", ge=1)],
    size: t.Annotated[int, p.Query(default=10, description="Items per page", ge=1, le=100)],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.CourseListResponse)]:
    """
    Get course list
    
    - **page**: Page number, starting from 1  
    - **size**: Items per page, range 1-100
    """
    return JsonResponse({
        "message": "Get course list successfully",
        "data": [],
        "code": 0,
    })

async def bind(
    request: HttpRequest,
    ctx: t.Annotated[s.BindRequest, p.Json()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.BindResponse)]:
    """
    Student course binding
    
    - **student_id**: Student ID
    - **course_id**: Course ID
    """
    return JsonResponse({
        "message": f"Student {ctx.student_id} successfully enrolled in course {ctx.course_id}",
        "data": {
            "student_id": ctx.student_id,
            "course_id": ctx.course_id
        },
        "code": 0,
    })

async def get_student(
    request: HttpRequest,
    student_id: t.Annotated[int, p.Path(description="Student ID")],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.StudentDetailResponse)]:
    """
    Get student details
    
    - **student_id**: Student ID
    """
    # Return mock data for now
    return JsonResponse({
        "code": 0,
        "message": "Get student details successfully",
        "data": {
            "id": student_id,
            "name": "Example Student",
            "email": "student@example.com",
            "age": 20,
            "student_id": "2024001"
        }
    })
```

### Parameter Validation Features

Unfazed provides powerful parameter validation capabilities:

**1. Type Validation**:
```python
page: t.Annotated[int, p.Query()]  # Automatically convert to integer
```

**2. Range Constraints**:
```python
size: t.Annotated[int, p.Query(ge=1, le=100)]  # Value range 1-100
```

**3. Default Values**:
```python
page: t.Annotated[int, p.Query(default=1)]  # Default value is 1
```

**4. Required Parameters**:
```python
user_id: t.Annotated[int, p.Path()]  # Path parameters are required
```

## Route Configuration

### Update Route Definition

Edit the `enroll/routes.py` file:

```python
# src/backend/enroll/routes.py

import typing as t
from unfazed.route import Route, path
from .endpoints import hello, list_student, list_course, bind, get_student

patterns: t.List[Route] = [
    # Hello World interface
    path("/hello", endpoint=hello, methods=["GET"], name="hello"),
    
    # Student related interfaces
    path("/student-list", endpoint=list_student, methods=["GET"], name="list_students"),

    # Course related interfaces  
    path("/course-list", endpoint=list_course, methods=["GET"], name="list_courses"),
    
    # Course binding interface
    path("/bind", endpoint=bind, methods=["POST"], name="bind_course"),
]
```

## Automatic API Documentation

### OpenAPI Documentation Generation

Unfazed automatically generates OpenAPI 3.0 documentation based on your code, no additional configuration needed!

After starting the project, visit the following addresses:

**Swagger UI (Interactive Documentation)**:
```
http://127.0.0.1:9527/openapi/docs
```

**ReDoc (Beautiful Documentation)**:
```
http://127.0.0.1:9527/openapi/redoc
```

### Documentation Features

Unfazed generates API documentation including:

1. **Complete Interface Information**:
   - HTTP methods and paths
   - Request/response parameters
   - Data types and validation rules

2. **Interactive Testing**:
   - Test APIs directly in Swagger UI
   - View actual request/response data

3. **Code Examples**:
   - Auto-generate call examples in multiple languages
   - curl, Python, JavaScript, etc.

4. **Data Models**:
   - Complete Schema definitions
   - Field descriptions and constraint information

### Enhancing Documentation Quality

**Adding Interface Tags**:
```python
# Group interfaces
path("/students", endpoint=list_student, tags=["Student Management"])
path("/courses", endpoint=list_course, tags=["Course Management"])
```

**Improving Interface Descriptions**:
```python
async def list_student(request: HttpRequest, ...):
    """
    Get student list
    
    Get a paginated list of all students in the system, supports querying by page number and items per page.
    
    **Usage Instructions**:
    - Page numbers start from 1
    - Maximum 100 records per page
    - Return results include complete pagination metadata
    
    **Return Data Includes**:
    - Student basic information (name, email, age, etc.)
    - Pagination information (current page, total, total pages, etc.)
    """
    pass
```

## Testing API Interfaces

### Using curl for Testing

```bash
# Test student list interface
curl "http://127.0.0.1:9527/enroll/students?page=1&size=5"

# Test student detail interface
curl "http://127.0.0.1:9527/enroll/students/1"

# Test course list interface
curl "http://127.0.0.1:9527/enroll/courses"

# Test course binding interface
curl -X POST "http://127.0.0.1:9527/enroll/bind" \
     -H "Content-Type: application/json" \
     -d '{"student_id": 1, "course_id": 1}'
```

### Using Python requests for Testing

```python
import requests
import json

base_url = "http://127.0.0.1:9527/enroll"

# Test student list
response = requests.get(f"{base_url}/students", params={"page": 1, "size": 10})
print("Student list:", response.json())

# Test course binding
bind_data = {"student_id": 1, "course_id": 1}
response = requests.post(
    f"{base_url}/bind", 
    json=bind_data,
    headers={"Content-Type": "application/json"}
)
print("Binding result:", response.json())
```

### Custom Error Responses

```python
from unfazed.exception import ValidationError

async def bind(request: HttpRequest, ctx: s.BindRequest) -> JsonResponse:
    """Course binding (with validation)"""
    
    # Custom business validation
    if ctx.student_id == ctx.course_id:
        raise ValidationError("Student ID and Course ID cannot be the same")
    
    # Normal processing logic
    return JsonResponse({
        "success": True,
        "message": "Binding successful",
        "data": {"student_id": ctx.student_id, "course_id": ctx.course_id}
    })
```

## Next Steps

Excellent! You have successfully designed complete API interfaces and data models. In the next tutorial, we will:

- Implement business logic services (Services)
- Connect to database for actual CRUD operations
- Learn advanced usage of serializers
- Handle complex business scenarios

Let's continue to **Part 5: Business Logic Implementation**!

---
