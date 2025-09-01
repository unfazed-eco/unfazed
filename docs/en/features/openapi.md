Unfazed OpenAPI Documentation System
=====

Unfazed has a built-in powerful OpenAPI documentation generation system based on OpenAPI 3.1.1 standard, automatically generating complete API documentation from your endpoint functions and type annotations. The system provides both Swagger UI and ReDoc interfaces, supporting interactive API testing and beautiful documentation display.

## System Overview

### Core Features

- **Auto-generation**: Automatically generates OpenAPI specifications based on type annotations and Pydantic models
- **Dual Interface Support**: Provides both Swagger UI and ReDoc documentation interfaces
- **Interactive Testing**: Supports online API testing and parameter validation
- **Type Safety**: Complete support for Python type system and Pydantic validation
- **Highly Customizable**: Supports custom CDN, themes, and configuration options

### Core Components

- **OpenApi**: Core OpenAPI specification generator
- **OpenApiService**: Documentation service provider, manages HTML templates and static resources
- **Built-in View Functions**: Automatically provides `/openapi/docs`, `/openapi/redoc`, `/openapi/openapi.json` routes
- **Configuration System**: Flexible configuration management, supports development and production environments

### Supported Parameter Types

- **Path Parameters**: Path parameter extraction and validation
- **Query Parameters**: Query string parameter handling
- **Header Parameters**: HTTP header parameter validation
- **Cookie Parameters**: Cookie value extraction
- **Request Body**: JSON, Form, file upload support
- **Response Models**: Response model definition and documentation generation

## Quick Start

### 1. Basic Configuration

```python
# settings.py
UNFAZED_SETTINGS = {
    "OPENAPI": {
        "info": {
            "title": "My API",
            "version": "1.0.0",
            "description": "An API system built with Unfazed",
            "termsOfService": "https://example.com/terms",
            "contact": {
                "name": "API Support Team",
                "url": "https://example.com/contact", 
                "email": "support@example.com"
            },
            "license": {
                "name": "MIT License",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "servers": [
            {"url": "https://api.example.com", "description": "Production Environment"},
            {"url": "https://staging-api.example.com", "description": "Staging Environment"},
            {"url": "http://127.0.0.1:9527", "description": "Local Development"}
        ],
    }
}
```

### 2. Define Data Models

```python
# models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import StrEnum
from datetime import datetime

class UserRole(StrEnum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserQuery(BaseModel):
    """User query parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=10, ge=1, le=100, description="Page size")
    role: Optional[UserRole] = Field(default=None, description="User role filter")
    keyword: Optional[str] = Field(default=None, description="Search keyword")

class UserCreate(BaseModel):
    """Create user request"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    profile: Optional[dict] = Field(default=None, description="User profile")

class UserResponse(BaseModel):
    """User response model"""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email")
    role: UserRole = Field(..., description="Role")
    is_active: bool = Field(..., description="Is active")
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")

class UserListResponse(BaseModel):
    """User list response"""
    users: List[UserResponse] = Field(..., description="User list")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    code: int = Field(..., description="Error code")
    details: Optional[dict] = Field(default=None, description="Error details")
```

### 3. Write API View Functions

```python
# endpoints.py
import typing as t
from unfazed.http import HttpRequest, JsonResponse
from unfazed.route import params
from unfazed.route.params import ResponseSpec
from .models import UserQuery, UserCreate, UserResponse, UserListResponse, ErrorResponse

async def get_users(
    request: HttpRequest,
    query: t.Annotated[UserQuery, params.Query()],
    authorization: t.Annotated[str, params.Header(description="Bearer token")]
) -> t.Annotated[JsonResponse, ResponseSpec(
    model=UserListResponse,
    description="Successfully retrieved user list",
    examples={
        "success": {
            "summary": "Success example",
            "value": {
                "users": [
                    {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "role": "user",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 10
            }
        }
    }
)]:
    """
    Get user list
    
    Supports pagination query and role filtering, requires valid authentication token.
    """
    # Simulate business logic
    users = [
        UserResponse(
            id=1,
            username="john_doe",
            email="john@example.com", 
            role="user",
            is_active=True,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
    ]
    
    response = UserListResponse(
        users=users,
        total=len(users),
        page=query.page,
        size=query.size
    )
    
    return JsonResponse(response.model_dump())

async def create_user(
    request: HttpRequest,
    user_data: t.Annotated[UserCreate, params.Json()],
    authorization: t.Annotated[str, params.Header(description="Bearer token")]
) -> t.Annotated[JsonResponse, ResponseSpec(
    model=UserResponse,
    description="Successfully created user",
    code="201"
)]:
    """
    Create new user
    
    Creates a new user account, requires administrator privileges.
    """
    # Simulate user creation
    new_user = UserResponse(
        id=999,
        username=user_data.username,
        email=user_data.email,
        role=user_data.role,
        is_active=True,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z"
    )
    
    return JsonResponse(new_user.model_dump(), status_code=201)

async def get_user_by_id(
    request: HttpRequest,
    user_id: t.Annotated[int, params.Path(description="User ID")],
    authorization: t.Annotated[str, params.Header(description="Bearer token")]
) -> t.Annotated[JsonResponse, ResponseSpec(model=UserResponse)]:
    """Get user details by ID"""
    
    # Simulate user lookup
    if user_id == 404:
        return JsonResponse(
            ErrorResponse(error="User not found", code=404).model_dump(),
            status_code=404
        )
    
    user = UserResponse(
        id=user_id,
        username=f"user_{user_id}",
        email=f"user{user_id}@example.com",
        role="user",
        is_active=True,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z"
    )
    
    return JsonResponse(user.model_dump())
```

### 4. Configure Routes

```python
# routes.py
from unfazed.route import path
from .endpoints import get_users, create_user, get_user_by_id

patterns = [
    path(
        "/api/users",
        endpoint=get_users,
        methods=["GET"],
        tags=["User Management"],
        summary="Get user list",
        description="Get user list in the system, supports pagination and filtering"
    ),
    path(
        "/api/users",
        endpoint=create_user,
        methods=["POST"],
        tags=["User Management"],
        summary="Create user",
        description="Create new user account"
    ),
    path(
        "/api/users/{user_id}",
        endpoint=get_user_by_id,
        methods=["GET"],
        tags=["User Management"],
        summary="Get user details",
        description="Get detailed information of user by user ID"
    ),
]
```

### 5. Start Service and Access Documentation

```bash
# Start development server
uvicorn asgi:application --host 0.0.0.0 --port 9527 --reload
```

**Access Documentation Interfaces:**

- **Swagger UI**: `http://127.0.0.1:9527/openapi/docs`
- **ReDoc**: `http://127.0.0.1:9527/openapi/redoc`
- **OpenAPI JSON**: `http://127.0.0.1:9527/openapi/openapi.json`

## Advanced Features

### Response Model Definition

```python
from unfazed.route.params import ResponseSpec

# Single response model
async def simple_endpoint() -> t.Annotated[JsonResponse, ResponseSpec(
    model=UserResponse,
    description="User information"
)]:
    pass

# Multiple status code responses
async def complex_endpoint() -> JsonResponse:
    pass

# Define response models in routes
patterns = [
    path(
        "/api/complex",
        endpoint=complex_endpoint,
        response_models=[
            ResponseSpec(
                model=UserResponse,
                code="200",
                description="Operation successful",
                content_type="application/json"
            ),
            ResponseSpec(
                model=ErrorResponse,
                code="400",
                description="Request parameter error",
                content_type="application/json"
            ),
            ResponseSpec(
                model=ErrorResponse,
                code="401",
                description="Unauthorized access",
                content_type="application/json"
            )
        ]
    )
]
```

### File Upload

```python
from unfazed.file import UploadFile

class FileUploadForm(BaseModel):
    """File upload form"""
    title: str = Field(..., description="File title")
    description: Optional[str] = Field(default=None, description="File description")

async def upload_file(
    request: HttpRequest,
    form_data: t.Annotated[FileUploadForm, params.Form()],
    file: t.Annotated[UploadFile, params.File(description="File to upload")]
) -> t.Annotated[JsonResponse, ResponseSpec(
    model=dict,
    description="File upload successful"
)]:
    """
    File upload endpoint
    
    Supports various format file uploads, maximum 10MB.
    """
    return JsonResponse({
        "filename": file.filename,
        "size": file.size,
        "content_type": file.content_type,
        "title": form_data.title,
        "description": form_data.description
    })

# Route configuration
patterns = [
    path(
        "/api/upload",
        endpoint=upload_file,
        methods=["POST"],
        tags=["File Management"],
        summary="Upload file"
    )
]
```

## Complete Configuration Details

### OpenAPI Configuration Options

```python
UNFAZED_SETTINGS = {
    "OPENAPI": {
        # OpenAPI specification version
        "openapi": "3.1.1",
        
        # API basic information
        "info": {
            "title": "My API",
            "version": "1.0.0", 
            "description": "API description",
            "termsOfService": "https://example.com/terms",
            "contact": {
                "name": "Support Team",
                "url": "https://example.com/contact",
                "email": "support@example.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        
        # Server configuration
        "servers": [
            {"url": "https://api.example.com", "description": "Production Environment"},
            {"url": "http://localhost:9527", "description": "Development Environment"}
        ],
        
        # External documentation links
        "externalDocs": {
            "description": "Complete documentation",
            "url": "https://docs.example.com"
        },
        
        # Documentation interface configuration
        "json_route": "/openapi/openapi.json",  # OpenAPI JSON route
        
        # Swagger UI configuration
        "swagger_ui": {
            "css": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
            "js": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            "favicon": "https://www.openapis.org/wp-content/uploads/sites/3/2016/11/favicon.png"
        },
        
        # ReDoc configuration
        "redoc": {
            "js": "https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"
        },
        
        # Access control
        "allow_public": True  # Recommended to set False in production
    }
}
```

### Custom CDN Configuration

```python
# Use domestic CDN acceleration
UNFAZED_SETTINGS = {
    "OPENAPI": {
        "swagger_ui": {
            "css": "https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
            "js": "https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            "favicon": "/static/favicon.ico"  # Use local icon
        },
        "redoc": {
            "js": "https://unpkg.com/redoc@latest/bundles/redoc.standalone.js"
        }
    }
}
```

### Route-level Configuration

```python
patterns = [
    # Include in documentation
    path(
        "/api/public",
        endpoint=public_endpoint,
        include_in_schema=True,  # Default value
        tags=["Public APIs"],
        summary="Public endpoint",
        description="Public endpoint that doesn't require authentication"
    ),
    
    # Exclude from documentation
    path(
        "/internal/health",
        endpoint=health_check,
        include_in_schema=False,  # Not shown in documentation
        tags=["Internal APIs"]
    ),
    
    # Custom response models
    path(
        "/api/custom",
        endpoint=custom_endpoint,
        response_models=[
            ResponseSpec(model=SuccessResponse, code="200"),
            ResponseSpec(model=ErrorResponse, code="400")
        ],
        tags=["Custom APIs"],
        deprecated=False,  # Whether deprecated
        externalDocs={
            "description": "Detailed documentation",
            "url": "https://docs.example.com/custom"
        }
    )
]
```

## Production Environment Deployment

### Security Configuration

```python
# production_settings.py
UNFAZED_SETTINGS = {
    "OPENAPI": {
        "allow_public": False,  # Disable public access
        "info": {
            "title": "Production API",
            "version": "1.0.0"
        },
        "servers": [
            {"url": "https://api.yourdomain.com", "description": "Production Environment"}
        ]
    }
}
```

### Conditional Documentation Enablement

```python
import os

# Control documentation availability based on environment variables
ENABLE_DOCS = os.getenv("ENABLE_API_DOCS", "false").lower() == "true"

if ENABLE_DOCS:
    UNFAZED_SETTINGS["OPENAPI"] = {
        "allow_public": True,
        "info": {"title": "API Docs", "version": "1.0.0"}
    }
else:
    # Don't enable OpenAPI in production
    UNFAZED_SETTINGS["OPENAPI"] = None
```

Through Unfazed's OpenAPI system, you can easily build professional, complete, and interactive API documentation. This system not only improves development efficiency but also provides an excellent development experience for API users.
