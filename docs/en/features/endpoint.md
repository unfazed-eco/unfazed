Unfazed Endpoint System
=====

Endpoint is a core component in the Unfazed framework, serving as a bridge between route dispatch and business logic processing. It provides powerful parameter parsing, type validation, and API documentation generation capabilities.

## System Architecture

The Unfazed Endpoint system includes the following core components:

### EndpointHandler
Responsible for handling request parameter parsing and validation, supporting:
- Automatic parameter type conversion
- Request validation and error handling
- Synchronous and asynchronous endpoint execution
- Parameter injection and dependency resolution

### EndPointDefinition
Responsible for view function metadata definition and model construction:
- Parse function signatures and type annotations
- Build request parameter models (Path, Query, Header, Cookie, Body)
- Generate OpenAPI document specifications
- Support HttpResponse model definitions

### Parameter Type System
Supports multiple parameter sources and types:
- **Path**: Path parameters (e.g., `/users/{user_id}`)
- **Query**: Query parameters (e.g., `?page=1&size=10`)
- **Header**: Request header parameters
- **Cookie**: Cookie parameters
- **Json**: JSON request body
- **Form**: Form data
- **File**: File uploads

## Quick Start

### Basic View Functions

Create a simple view function:

```python
# endpoints.py
import typing as t
from unfazed.http import HttpRequest, HttpResponse, JsonResponse
from pydantic import BaseModel


async def hello_world(request: HttpRequest) -> HttpResponse:
    return HttpResponse(content="Hello, World!")


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


async def get_user(request: HttpRequest) -> JsonResponse[UserResponse]:
    user_data = UserResponse(id=1, name="John", email="john@example.com")
    return JsonResponse(user_data)
```

### Route Registration

Connect view functions to the routing system:

```python
# routes.py
from unfazed.route import path
from .endpoints import hello_world, get_user

patterns = [
    path("/", endpoint=hello_world),
    path("/user", endpoint=get_user, methods=["GET"]),
]
```

### View Function Features

Unfazed's view function system has the following features:

1. **Type Safety**: Parameter validation based on Python type annotations
2. **Automatic Documentation**: Automatically generate OpenAPI/Swagger documentation
3. **Dependency Injection**: Automatically parse and inject request parameters
4. **Async Support**: Native support for async/await
5. **Error Handling**: Unified error handling and validation mechanisms (depends on middleware handling)


## Request Parameter System

Unfazed provides a powerful request parameter parsing system that supports multiple parameter sources and automatic type validation. The system supports the following parameter types:

| Parameter Type | Description                                       | Example                             |
| -------------- | ------------------------------------------------- | ----------------------------------- |
| **Path**       | Path parameters, extracted from URL path          | `/users/{user_id}`                  |
| **Query**      | Query parameters, extracted from URL query string | `?page=1&size=10`                   |
| **Header**     | Request header parameters                         | `Authorization: Bearer token`       |
| **Cookie**     | Cookie parameters                                 | `session_id=abc123`                 |
| **Json**       | JSON request body                                 | `{"name": "John"}`                  |
| **Form**       | Form data                                         | `application/x-www-form-urlencoded` |
| **File**       | File uploads                                      | `multipart/form-data`               |

### Parameter Definition Methods

Parameters can be defined in two ways:

#### 1. Using typing.Annotated annotations (recommended)

```python
import typing as t
from unfazed.route import params as p

async def endpoint(
    request: HttpRequest,
    user_id: t.Annotated[int, p.Path()],              # Path parameter
    page: t.Annotated[int, p.Query(default=1)],       # Query parameter with default
    auth: t.Annotated[str, p.Header()],               # Header parameter
) -> JsonResponse:
    ...
```

#### 2. Automatic inference (simplified syntax)

In actual business development, try to avoid using automatic inference. Clear parameter definition methods can improve code readability and maintainability.

```python
async def endpoint(
    request: HttpRequest,
    user_id: int,        # Automatically recognized as Path parameter if defined in route
    page: int,           # Basic types automatically recognized as Query parameters
    user: UserModel,     # BaseModel types automatically recognized as Json parameters
) -> JsonResponse:
    ...
```

#### 3. Automatic merging

Parameters of the same type can be automatically merged, for example:

```python

class Profile(BaseModel):
    sex: str
    height: int
    weight: int


async def endpoint(
    request: HttpRequest,
    name: t.Annotated[str, p.Query()],
    age: t.Annotated[int, p.Query()],
    profile: t.Annotated[Profile, p.Query()],
) -> JsonResponse:
    return JsonResponse({"message": f"Got user {name} successfully", "age": age, "sex": profile.sex, "height": profile.height, "weight": profile.weight})


```

### Parameter Validation and Error Handling

The system automatically validates parameter types and required fields:

```python
from pydantic import Field, BaseModel

class UserCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50, description="Username")
    age: int = Field(ge=0, le=150, description="Age")
    email: str = Field(regex=r'^[^@]+@[^@]+\.[^@]+$', description="Email")

async def create_user(
    request: HttpRequest,
    user_data: t.Annotated[UserCreateRequest, p.Json()]
) -> JsonResponse:
    # Parameters will be automatically validated, return error if validation fails
    return JsonResponse({"message": f"Created user {user_data.name} successfully"})
```

Below are detailed introductions to various parameter types.


### Path Parameters

Path parameters extract from URL paths, supporting basic types and complex models.

#### Basic Usage

```python
import typing as t
from pydantic import BaseModel, Field
from unfazed.http import HttpRequest, JsonResponse
from unfazed.route import params as p


# Basic type path parameters
async def get_user(
    request: HttpRequest,
    user_id: t.Annotated[int, p.Path(description="User ID")],
    category: t.Annotated[str, p.Path(description="User category")]
) -> JsonResponse:
    return JsonResponse({
        "user_id": user_id,
        "category": category
    })


# Route definition
patterns = [
    path("/users/{user_id}/category/{category}", endpoint=get_user),
]

# Request example: GET /users/123/category/vip
# Result: {"user_id": 123, "category": "vip"}
```

#### Using BaseModel to organize path parameters

```python
class UserPathParams(BaseModel):
    user_id: int = Field(description="User ID", gt=0)
    org_id: int = Field(description="Organization ID", gt=0)


class ProjectPathParams(BaseModel):
    project_id: str = Field(description="Project ID", min_length=1)
    version: str = Field(default="latest", description="Version number")


async def get_user_project(
    request: HttpRequest,
    user_params: t.Annotated[UserPathParams, p.Path()],
    project_params: t.Annotated[ProjectPathParams, p.Path()],
    action: t.Annotated[str, p.Path(default="view")]  # Individual path parameter
) -> JsonResponse:
    return JsonResponse({
        "user_id": user_params.user_id,
        "org_id": user_params.org_id,
        "project_id": project_params.project_id,
        "version": project_params.version,
        "action": action
    })


# Route definition
patterns = [
    path("/orgs/{org_id}/users/{user_id}/projects/{project_id}/{version}/{action}", 
         endpoint=get_user_project),
]

# Request example: GET /orgs/1/users/123/projects/myapp/v1.0/edit
```

#### Automatic path parameter inference

```python
async def simple_path_endpoint(
    request: HttpRequest,
    user_id: int,      # Automatically recognized as path parameter (because {user_id} is defined in route)
    post_id: int,      # Automatically recognized as path parameter (because {post_id} is defined in route)
) -> JsonResponse:
    return JsonResponse({
        "user_id": user_id,
        "post_id": post_id
    })

# Route definition
patterns = [
    path("/users/{user_id}/posts/{post_id}", endpoint=simple_path_endpoint),
]
```

#### Path Parameter Features

- **Type Conversion**: Automatically convert to specified Python types
- **Validation**: Support all Pydantic validation rules
- **Documentation Generation**: Automatically generate OpenAPI parameter documentation
- **Error Handling**: Return errors when type conversion fails (depends on middleware handling)


### Query Parameters

Query parameters extract from URL query strings, commonly used for pagination, filtering, and search scenarios.

#### Basic Usage

```python
# Basic type query parameters
async def search_users(
    request: HttpRequest,
    keyword: t.Annotated[str, p.Query(description="Search keyword")],
    page: t.Annotated[int, p.Query(default=1, description="Page number", ge=1)],
    size: t.Annotated[int, p.Query(default=10, description="Page size", ge=1, le=100)],
    active: t.Annotated[bool, p.Query(default=True, description="Is active")]
) -> JsonResponse:
    return JsonResponse({
        "keyword": keyword,
        "page": page,
        "size": size,
        "active": active,
        "results": []  # Mock search results
    })

# Request example: GET /search?keyword=John&page=2&size=20&active=false
```

#### Using BaseModel to organize query parameters

```python
class SearchParams(BaseModel):
    keyword: str = Field(description="Search keyword", min_length=1)
    category: str = Field(default="all", description="Category")


class PaginationParams(BaseModel):
    page: int = Field(default=1, description="Page number", ge=1)
    size: int = Field(default=10, description="Page size", ge=1, le=100)
    sort_by: str = Field(default="created_at", description="Sort field")
    order: str = Field(default="desc", regex="^(asc|desc)$", description="Sort direction")


async def advanced_search(
    request: HttpRequest,
    search: t.Annotated[SearchParams, p.Query()],
    pagination: t.Annotated[PaginationParams, p.Query()],
    include_inactive: t.Annotated[bool, p.Query(default=False)]  # Individual query parameter
) -> JsonResponse:
    return JsonResponse({
        "search_params": {
            "keyword": search.keyword,
            "category": search.category
        },
        "pagination": {
            "page": pagination.page,
            "size": pagination.size,
            "sort_by": pagination.sort_by,
            "order": pagination.order
        },
        "include_inactive": include_inactive
    })

# Request example: GET /advanced-search?keyword=python&category=tech&page=2&size=5&sort_by=title&order=asc&include_inactive=true
```

#### Automatic query parameter inference

```python
async def simple_query_endpoint(
    request: HttpRequest,
    name: str,          # Basic types automatically recognized as query parameters
    age: int,           # Basic types automatically recognized as query parameters
    email: str,         # Basic types automatically recognized as query parameters
) -> JsonResponse:
    return JsonResponse({
        "name": name,
        "age": age,
        "email": email
    })

# Request example: GET /simple?name=John&age=25&email=john@example.com
```

#### Query Parameter Features

- **Optional Parameters**: Support default values, use defaults when not provided
- **Type Conversion**: Automatically convert strings to specified types (int, bool, float, etc.)
- **List Support**: Support multi-value parameters (e.g., `?tags=python&tags=web`)
- **Validation**: Support all Pydantic validation rules

#### Advanced Query Parameter Examples

```python
from typing import List, Optional
from enum import Enum

class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class FilterParams(BaseModel):
    status: Optional[StatusEnum] = Field(default=None, description="Status filter")
    tags: List[str] = Field(default=[], description="Tag list")
    min_price: Optional[float] = Field(default=None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(default=None, ge=0, description="Maximum price")
    created_after: Optional[str] = Field(default=None, description="Creation time filter")

async def filter_products(
    request: HttpRequest,
    filters: t.Annotated[FilterParams, p.Query()]
) -> JsonResponse:
    return JsonResponse({
        "filters": filters.model_dump(exclude_none=True),
        "message": "Query successful"
    })

# Request example: GET /products?status=active&tags=electronics&tags=mobile&min_price=100&max_price=1000
```


### Header Parameters

Header parameters extract from HTTP request headers, commonly used for authentication, content negotiation, and client information passing.

#### Basic Usage

```python
# Common request header parameters
async def authenticated_endpoint(
    request: HttpRequest,
    authorization: t.Annotated[str, p.Header(description="Authentication token")],
    user_agent: t.Annotated[str, p.Header(alias="User-Agent", description="User agent")],
    content_type: t.Annotated[str, p.Header(
        alias="Content-Type", 
        default="application/json",
        description="Content type"
    )],
    x_request_id: t.Annotated[str, p.Header(
        alias="X-Request-ID",
        default=None,
        description="Request tracking ID"
    )]
) -> JsonResponse:
    return JsonResponse({
        "authorization": authorization,
        "user_agent": user_agent,
        "content_type": content_type,
        "request_id": x_request_id
    })

# Request example:
# GET /api/data
# Authorization: Bearer your-token-here
# User-Agent: Mozilla/5.0...
# Content-Type: application/json
# X-Request-ID: 12345-67890
```

#### Using BaseModel to organize request headers

```python
class AuthHeaders(BaseModel):
    authorization: str = Field(description="Authentication token", min_length=1)
    x_api_key: str = Field(alias="X-API-Key", description="API key")


class ClientHeaders(BaseModel):
    user_agent: str = Field(alias="User-Agent", description="User agent")
    accept_language: str = Field(
        alias="Accept-Language", 
        default="zh-CN",
        description="Accept language"
    )
    x_forwarded_for: str = Field(
        alias="X-Forwarded-For",
        default=None,
        description="Client IP"
    )


async def api_with_headers(
    request: HttpRequest,
    auth: t.Annotated[AuthHeaders, p.Header()],
    client_info: t.Annotated[ClientHeaders, p.Header()],
    custom_header: t.Annotated[str, p.Header(alias="X-Custom-Value", default="default")]
) -> JsonResponse:
    return JsonResponse({
        "auth": {
            "authorization": auth.authorization,
            "api_key": auth.x_api_key
        },
        "client": {
            "user_agent": client_info.user_agent,
            "language": client_info.accept_language,
            "forwarded_for": client_info.x_forwarded_for
        },
        "custom": custom_header
    })
```

#### Header Parameter Features

- **Alias Support**: Use `alias` to handle HTTP Header naming conventions (e.g., `Content-Type`)
- **Case Insensitive**: HTTP header names are case insensitive
- **Optional Parameters**: Support default values
- **Validation**: Support Pydantic validation rules


### Cookie Parameters

Cookie parameters extract from HTTP Cookies, commonly used for session management, user preference settings, etc.

#### Basic Usage

```python
# Basic Cookie parameters
async def user_dashboard(
    request: HttpRequest,
    session_id: t.Annotated[str, p.Cookie(description="Session ID")],
    user_preferences: t.Annotated[str, p.Cookie(
        default="default", 
        description="User preference settings"
    )],
    theme: t.Annotated[str, p.Cookie(default="light", description="Theme setting")],
    language: t.Annotated[str, p.Cookie(default="zh-CN", description="Language setting")]
) -> JsonResponse:
    return JsonResponse({
        "session_id": session_id,
        "preferences": user_preferences,
        "theme": theme,
        "language": language
    })

# Cookie setting example:
# Cookie: session_id=abc123; user_preferences=compact; theme=dark; language=en-US
```

#### Using BaseModel to organize Cookies

```python
class SessionCookies(BaseModel):
    session_id: str = Field(description="Session identifier")
    csrf_token: str = Field(description="CSRF token", min_length=10)


class UserCookies(BaseModel):
    user_id: int = Field(description="User ID", gt=0)
    remember_me: bool = Field(default=False, description="Remember login")
    last_visit: str = Field(default=None, description="Last visit time")


async def authenticated_page(
    request: HttpRequest,
    session: t.Annotated[SessionCookies, p.Cookie()],
    user: t.Annotated[UserCookies, p.Cookie()],
    analytics_id: t.Annotated[str, p.Cookie(default=None, description="Analytics tracking ID")]
) -> JsonResponse:
    return JsonResponse({
        "session": {
            "id": session.session_id,
            "csrf_token": session.csrf_token
        },
        "user": {
            "id": user.user_id,
            "remember_me": user.remember_me,
            "last_visit": user.last_visit
        },
        "analytics_id": analytics_id
    })
```

#### Cookie Parameter Features

- **Automatic Parsing**: Automatically parse Cookie strings
- **Type Conversion**: Support automatic conversion of basic types
- **Optional Parameters**: Support default values
- **Security Considerations**: Recommend validating sensitive Cookies


### Json Parameters

Json parameters extract JSON data from HTTP request bodies, the most commonly used data transmission method for APIs.

#### Basic Usage

```python
# Simple JSON request body
class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50, description="Username")
    email: str = Field(regex=r'^[^@]+@[^@]+\.[^@]+$', description="Email address")
    age: int = Field(ge=0, le=150, description="Age")
    is_active: bool = Field(default=True, description="Is active")

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int
    is_active: bool
    created_at: str

async def create_user(
    request: HttpRequest,
    user_data: t.Annotated[CreateUserRequest, p.Json()]
) -> JsonResponse[UserResponse]:
    # Simulate creating user
    new_user = UserResponse(
        id=12345,
        name=user_data.name,
        email=user_data.email,
        age=user_data.age,
        is_active=user_data.is_active,
        created_at="2024-01-15T10:30:00Z"
    )
    return JsonResponse(new_user)

# Request example:
# POST /users
# Content-Type: application/json
# {
#   "name": "John",
#   "email": "john@example.com", 
#   "age": 25,
#   "is_active": true
# }
```

#### Automatic JSON parameter inference

```python
class ProductData(BaseModel):
    title: str = Field(description="Product title")
    price: float = Field(gt=0, description="Price")
    description: str = Field(default="", description="Product description")

async def create_product(
    request: HttpRequest,
    product: ProductData  # BaseModel types automatically recognized as Json parameters
) -> JsonResponse:
    return JsonResponse({
        "message": "Product created successfully",
        "product": product.model_dump()
    })
```

#### Complex JSON structures

```python
from typing import List, Dict, Optional, Union
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskTag(BaseModel):
    name: str
    color: str = Field(regex=r'^#[0-9A-Fa-f]{6}$', description="Color code")

class TaskAttachment(BaseModel):
    filename: str
    url: str
    size: int = Field(ge=0, description="File size (bytes)")

class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    priority: Priority = Field(default=Priority.MEDIUM, description="Priority")
    tags: List[TaskTag] = Field(default=[], description="Tag list")
    attachments: List[TaskAttachment] = Field(default=[], description="Attachment list")
    metadata: Dict[str, Union[str, int, bool]] = Field(default={}, description="Metadata")
    due_date: Optional[datetime] = Field(default=None, description="Due date")

async def create_task(
    request: HttpRequest,
    task_data: t.Annotated[CreateTaskRequest, p.Json()]
) -> JsonResponse:
    return JsonResponse({
        "message": "Task created successfully",
        "task_id": "TASK-001",
        "title": task_data.title,
        "priority": task_data.priority,
        "tags_count": len(task_data.tags),
        "attachments_count": len(task_data.attachments)
    })

# Request example:
# POST /tasks
# {
#   "title": "Complete project documentation",
#   "description": "Write technical documentation for the project",
#   "priority": "high",
#   "tags": [
#     {"name": "Documentation", "color": "#ff0000"},
#     {"name": "Important", "color": "#00ff00"}
#   ],
#   "metadata": {
#     "project_id": "PROJ-001",
#     "estimate_hours": 8
#   },
#   "due_date": "2024-01-20T18:00:00Z"
# }
```

#### Combining multiple JSON parameters

```python
class AuthInfo(BaseModel):
    api_key: str = Field(description="API key")
    signature: str = Field(description="Request signature")

class RequestData(BaseModel):
    action: str = Field(description="Operation type")
    data: Dict[str, t.Any] = Field(description="Operation data")

async def secure_operation(
    request: HttpRequest,
    auth: t.Annotated[AuthInfo, p.Json()],
    request_data: t.Annotated[RequestData, p.Json()],
    timestamp: t.Annotated[int, p.Json(description="Timestamp")]
) -> JsonResponse:
    # Verify authentication information and execute operation
    return JsonResponse({
        "status": "success",
        "action": request_data.action,
        "timestamp": timestamp
    })

# Request example:
# POST /secure-api
# {
#   "api_key": "your-api-key",
#   "signature": "request-signature",
#   "action": "update_profile",
#   "data": {"name": "New Name"},
#   "timestamp": 1705320600
# }
```

#### JSON Parameter Features

- **Automatic Validation**: Data validation based on Pydantic models
- **Type Conversion**: Automatic type conversion and formatting
- **Nested Support**: Support for complex nested data structures
- **Error Messages**: Provide detailed validation error information
- **Documentation Generation**: Automatically generate JSON Schema documentation


### Form Parameters

Form parameters extract from HTTP form data, supporting `application/x-www-form-urlencoded` format.

#### Basic Usage

```python
# Simple form data
class LoginForm(BaseModel):
    username: str = Field(min_length=1, description="Username")
    password: str = Field(min_length=6, description="Password")
    remember_me: bool = Field(default=False, description="Remember login")

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: str = None

async def login(
    request: HttpRequest,
    form_data: t.Annotated[LoginForm, p.Form()]
) -> JsonResponse[LoginResponse]:
    # Verify login information (example)
    if form_data.username == "admin" and form_data.password == "password":
        return JsonResponse(LoginResponse(
            success=True,
            message="Login successful",
            token="your-auth-token"
        ))
    else:
        return JsonResponse(LoginResponse(
            success=False,
            message="Incorrect username or password"
        ), status_code=401)

# Request example:
# POST /login
# Content-Type: application/x-www-form-urlencoded
# username=admin&password=password&remember_me=true
```

#### Complex Form Processing

```python
class UserProfileForm(BaseModel):
    full_name: str = Field(min_length=1, max_length=100, description="Full name")
    email: str = Field(regex=r'^[^@]+@[^@]+\.[^@]+$', description="Email")
    phone: str = Field(regex=r'^\+?1?\d{9,15}$', description="Phone number")
    bio: str = Field(default="", max_length=500, description="Bio")
    age: int = Field(ge=0, le=150, description="Age")
    newsletter: bool = Field(default=False, description="Subscribe to newsletter")

class AddressForm(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City")
    state: str = Field(description="State/Province")
    zip_code: str = Field(description="ZIP code")
    country: str = Field(default="CN", description="Country code")

async def update_profile(
    request: HttpRequest,
    profile: t.Annotated[UserProfileForm, p.Form()],
    address: t.Annotated[AddressForm, p.Form()],
    timezone: t.Annotated[str, p.Form(default="Asia/Shanghai", description="Timezone")]
) -> JsonResponse:
    return JsonResponse({
        "message": "Profile updated successfully",
        "profile": {
            "name": profile.full_name,
            "email": profile.email,
            "phone": profile.phone
        },
        "address": {
            "city": address.city,
            "country": address.country
        },
        "timezone": timezone
    })

# Request example:
# POST /profile
# Content-Type: application/x-www-form-urlencoded
# full_name=John&email=john@example.com&phone=13800138000&bio=Software Engineer&age=30&newsletter=true&street=Tech Avenue 1&city=Shenzhen&state=Guangdong&zip_code=518000&country=CN&timezone=Asia/Shanghai
```

### File Parameters

File parameters handle file uploads, supporting `multipart/form-data` format.

#### Basic File Upload

```python
from unfazed.file import UploadFile

class FileUploadResponse(BaseModel):
    filename: str
    size: int
    content_type: str
    message: str

async def upload_avatar(
    request: HttpRequest,
    avatar: t.Annotated[UploadFile, p.File(description="User avatar")]
) -> JsonResponse[FileUploadResponse]:
    # Validate file type
    if not avatar.content_type.startswith('image/'):
        return JsonResponse(
            {"error": "Only image files are supported"},
            status_code=400
        )
    
    # Validate file size (e.g., max 5MB)
    content = await avatar.read()
    if len(content) > 5 * 1024 * 1024:
        return JsonResponse(
            {"error": "File size cannot exceed 5MB"},
            status_code=400
        )
    
    # File saving logic (example)
    # save_file(avatar.filename, content)
    
    return JsonResponse(FileUploadResponse(
        filename=avatar.filename,
        size=len(content),
        content_type=avatar.content_type,
        message="Avatar uploaded successfully"
    ))

# Request example:
# POST /upload-avatar
# Content-Type: multipart/form-data
# avatar: [binary file data]
```

#### Multiple File Upload

```python
from typing import List

class MultiFileUploadResponse(BaseModel):
    uploaded_files: List[dict]
    total_count: int
    total_size: int

async def upload_documents(
    request: HttpRequest,
    documents: t.Annotated[List[UploadFile], p.File(description="Document list")],
    category: t.Annotated[str, p.Form(description="Document category")]
) -> JsonResponse[MultiFileUploadResponse]:
    uploaded_files = []
    total_size = 0
    
    for doc in documents:
        # Validate file type
        allowed_types = ['application/pdf', 'application/msword', 'text/plain']
        if doc.content_type not in allowed_types:
            continue
            
        content = await doc.read()
        file_size = len(content)
        total_size += file_size
        
        # File saving logic
        # save_document(doc.filename, content, category)
        
        uploaded_files.append({
            "filename": doc.filename,
            "size": file_size,
            "content_type": doc.content_type
        })
    
    return JsonResponse(MultiFileUploadResponse(
        uploaded_files=uploaded_files,
        total_count=len(uploaded_files),
        total_size=total_size
    ))

# Request example:
# POST /upload-documents
# Content-Type: multipart/form-data
# documents: [file1.pdf, file2.docx, file3.txt]
# category: reports
```

#### File and Form Data Combination

```python
class DocumentForm(BaseModel):
    title: str = Field(description="Document title")
    description: str = Field(default="", description="Document description")
    is_public: bool = Field(default=False, description="Is public")
    tags: str = Field(default="", description="Tags (comma separated)")

async def create_document(
    request: HttpRequest,
    document_file: t.Annotated[UploadFile, p.File(description="Document file")],
    form_data: t.Annotated[DocumentForm, p.Form()],
    author_id: t.Annotated[int, p.Form(description="Author ID")]
) -> JsonResponse:
    # Process file
    content = await document_file.read()
    
    # Parse tags
    tags = [tag.strip() for tag in form_data.tags.split(',') if tag.strip()]
    
    return JsonResponse({
        "message": "Document created successfully",
        "document": {
            "title": form_data.title,
            "filename": document_file.filename,
            "size": len(content),
            "author_id": author_id,
            "tags": tags,
            "is_public": form_data.is_public
        }
    })

# Request example:
# POST /documents
# Content-Type: multipart/form-data
# document_file: [binary file]
# title: Project Report
# description: Q1 2024 project summary
# is_public: true
# tags: report,quarterly,project
# author_id: 123
```

#### File Parameter Features

- **Type Support**: Inherits from Starlette's UploadFile, supports all file operations
- **Async Operations**: Support for async file reading and processing
- **Content Type**: Automatically detect file MIME types
- **Size Limits**: Can set file size limits
- **Multiple Files**: Support for receiving multiple files in a single endpoint
- **Combined Usage**: Can be used together with form data

#### UploadFile Methods

```python
async def handle_file(file: UploadFile):
    # File properties
    filename = file.filename          # Original filename
    content_type = file.content_type  # MIME type
    
    # File operations
    content = await file.read()       # Read all content
    await file.seek(0)               # Reset file pointer
    chunk = await file.read(1024)    # Read specified bytes
    await file.close()               # Close file
```

## Advanced Usage

### Response Model Definition

Unfazed supports defining response models for generating API documentation and type hints:

```python
from unfazed.route import params as p

class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: t.Dict[str, t.Any]

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: int

async def api_endpoint(
    request: HttpRequest,
    user_id: t.Annotated[int, p.Path()]
) -> t.Annotated[
    JsonResponse,
    p.ResponseSpec(model=SuccessResponse, code="200", description="Success response"),
    p.ResponseSpec(model=ErrorResponse, code="404", description="User not found"),
    p.ResponseSpec(model=ErrorResponse, code="500", description="Server error")
]:
    try:
        # Business logic
        user_data = {"id": user_id, "name": "John"}
        return JsonResponse(SuccessResponse(
            message="User info retrieved successfully",
            data=user_data
        ))
    except UserNotFound:
        return JsonResponse(ErrorResponse(
            error="User not found",
            error_code=404
        ), status_code=404)
```

### Parameter Dependencies and Validation

#### Custom Validators

```python
from pydantic import validator

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str
    password: str = Field(min_length=8)
    confirm_password: str
    
    @validator('email')
    def validate_email(cls, v):
        if not '@' in v:
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

async def register_user(
    request: HttpRequest,
    user_data: t.Annotated[CreateUserRequest, p.Json()]
) -> JsonResponse:
    # User data has been validated
    return JsonResponse({"message": "User registered successfully"})
```

#### Conditional Parameters

```python
from typing import Union

class BaseSearchParams(BaseModel):
    query: str = Field(min_length=1, description="Search keyword")
    limit: int = Field(default=10, ge=1, le=100)

class UserSearchParams(BaseSearchParams):
    search_type: t.Literal["user"] = "user"
    include_inactive: bool = Field(default=False)

class ProductSearchParams(BaseSearchParams):
    search_type: t.Literal["product"] = "product"
    category: str = Field(default="all")
    min_price: float = Field(default=0, ge=0)

SearchParams = Union[UserSearchParams, ProductSearchParams]

async def universal_search(
    request: HttpRequest,
    search_params: t.Annotated[SearchParams, p.Json()]
) -> JsonResponse:
    if isinstance(search_params, UserSearchParams):
        # User search logic
        return JsonResponse({"type": "user_search", "results": []})
    else:
        # Product search logic
        return JsonResponse({"type": "product_search", "results": []})
```
