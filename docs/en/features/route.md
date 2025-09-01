Unfazed Routing System
========

Unfazed's routing system is built on Starlette with design philosophy inspired by Django routing and extensive enhancements. The routing system provides powerful parameter parsing, middleware integration, OpenAPI support, and more, making it a core component for building Web applications.

## System Overview

### Core Features

- **Django-style Design**: Familiar routing configuration patterns, easy to learn and use
- **Powerful Parameter Parsing**: Automatically parses path, query, header, cookie, and request body parameters
- **Middleware Integration**: Supports global and route-level middleware
- **Native OpenAPI Support**: Built-in OpenAPI documentation generation and Swagger UI
- **Type Safety**: Complete type annotation and validation support
- **Flexible Organization**: Supports application-level route organization and modular development

### Routing System Architecture

```python
Routing System Components:
├── path() - Route definition function
├── include() - Route module inclusion function
├── Route - Core route class (extends Starlette)
├── EndpointHandler - View function handler
├── EndPointDefinition - View function definition and parameter parsing
├── static() - Static file routes
└── mount() - ASGI application mounting
```

### Design Characteristics

1. **Flat Route Structure**: All routes are eventually expanded into a flat structure for easy management and debugging
2. **Application Isolation**: Each application's routes are managed independently, supporting namespaces
3. **Enhanced Parameterization**: Powerful parameter parsing and validation system
4. **Middleware Support**: Route-level middleware for precise control of request processing flow

## Route Configuration

### Global Route Configuration

Route entry is configured through `ROOT_URLCONF`, defaulting to `entry.routes`:

```python
# settings.py
UNFAZED_SETTINGS = {
    "ROOT_URLCONF": "entry.routes",  # Specify route entry file
    "DEBUG": True,
    "INSTALLED_APPS": [
        "myapp1",
        "myapp2",
    ]
}
```

### Project Structure

```
project/
├── backend/
│   ├── entry/
│   │   ├── __init__.py
│   │   ├── routes.py          # Global route entry
│   │   └── settings.py
│   ├── myapp1/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── routes.py          # Application routes
│   │   ├── endpoints.py       # View functions
│   │   └── models.py
│   └── myapp2/
│       ├── __init__.py
│       ├── routes.py
│       └── endpoints.py
└── main.py
```

## Route Definition

### Basic Route Definition

```python
# myapp/endpoints.py
import typing as t
from unfazed.http import HttpRequest, JsonResponse

async def hello_world(request: HttpRequest) -> JsonResponse:
    """Simple Hello World"""
    return JsonResponse({"message": "Hello, World!"})

async def get_user(request: HttpRequest) -> JsonResponse:
    """Get user information"""
    user_id = request.path_params.get("user_id")
    return JsonResponse({"user_id": user_id, "name": f"User {user_id}"})
```

```python
# myapp/routes.py
from unfazed.route import path
from . import endpoints as e

patterns = [
    # Basic route
    path("/hello", endpoint=e.hello_world),
    
    # Route with path parameters
    path("/users/{user_id}", endpoint=e.get_user),
    
    # Specify HTTP methods
    path("/users", endpoint=e.create_user, methods=["POST"]),
    
    # With OpenAPI documentation information
    path(
        "/users/{user_id}",
        endpoint=e.update_user,
        methods=["PUT"],
        summary="Update user information",
        description="Update user's basic information by user ID",
        tags=["User Management"],
    ),
]
```

### Global Route Organization

```python
# entry/routes.py
from unfazed.route import path, include

patterns = [
    # Include application routes
    path("/api/v1/users", routes=include("myapp1.routes")),
    path("/api/v1/orders", routes=include("myapp2.routes")),
    
    # Directly defined global routes
    path("/health", endpoint=health_check),
    path("/metrics", endpoint=get_metrics),
    
    # Static file routes
    static("/static", directory="static"),
    
    # Mount external ASGI applications
    mount("/admin", app=admin_app),
]
```

### Route Naming and Organization

```python
# Named routes for easy reverse resolution
patterns = [
    path(
        "/users/{user_id}",
        endpoint=e.get_user,
        name="user_detail",
        app_label="users"
    ),
    path(
        "/users/{user_id}/posts",
        endpoint=e.get_user_posts,
        name="user_posts",
        app_label="users"
    ),
]
```

## path Function Details

### Complete Signature

```python
def path(
    path: str,
    *,
    # Endpoint configuration
    endpoint: Callable | None = None,
    routes: List[Route] | None = None,
    
    # HTTP configuration
    methods: List[HttpMethod] | None = None,
    
    # Route metadata
    name: str | None = None,
    app_label: str | None = None,
    
    # Middleware configuration
    middlewares: List[CanBeImported] | None = None,
    
    # OpenAPI configuration
    include_in_schema: bool = True,
    tags: List[str] | None = None,
    summary: str | None = None,
    description: str | None = None,
    externalDocs: Dict | None = None,
    deprecated: bool = False,
    operation_id: str | None = None,
    response_models: List[ResponseSpec] | None = None,
) -> Route | List[Route]:
```

### Parameter Details

| Parameter           | Type          | Description                                       | Example                                      |
| ------------------- | ------------- | ------------------------------------------------- | -------------------------------------------- |
| `path`              | `str`         | Route path, supports path parameters              | `"/users/{user_id:int}"`                     |
| `endpoint`          | `Callable`    | View function (mutually exclusive with routes)    | `get_user`                                   |
| `routes`            | `List[Route]` | Sub-route list (mutually exclusive with endpoint) | `include("app.routes")`                      |
| `methods`           | `List[str]`   | Supported HTTP methods, default ["GET"]           | `["GET", "POST"]`                            |
| `name`              | `str`         | Route name for reverse resolution                 | `"user_detail"`                              |
| `app_label`         | `str`         | Application label, automatically set              | `"users"`                                    |
| `middlewares`       | `List[str]`   | Route-level middleware                            | `["app.middleware.AuthMiddleware"]`          |
| `include_in_schema` | `bool`        | Whether to include in OpenAPI documentation       | `True`                                       |
| `tags`              | `List[str]`   | OpenAPI tags                                      | `["User Management"]`                        |
| `summary`           | `str`         | OpenAPI summary                                   | `"Get user details"`                         |
| `description`       | `str`         | OpenAPI description                               | `"Get detailed user information by user ID"` |
| `deprecated`        | `bool`        | Whether deprecated                                | `False`                                      |

### Path Parameter Support

```python
patterns = [
    # Basic path parameters
    path("/users/{user_id}", endpoint=get_user),
    
    # Type converters
    path("/users/{user_id:int}", endpoint=get_user),
    path("/posts/{slug:str}", endpoint=get_post),
    path("/files/{file_path:path}", endpoint=download_file),
    
    # Multiple path parameters
    path("/users/{user_id:int}/posts/{post_id:int}", endpoint=get_user_post),
    
    # Optional parameters (implemented through query parameters)
    path("/search", endpoint=search),  # ?q=keyword&page=1
]
```

## Advanced Routing Features

### Route Middleware

```python
# middleware/auth.py
from unfazed.middleware import BaseMiddleware
from unfazed.http import JsonResponse

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        request = HttpRequest(scope, receive)
        
        # Check authentication
        auth_header = request.headers.get("authorization")
        if not auth_header:
            response = JsonResponse({"error": "Unauthorized access"}, status_code=401)
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)

# routes.py
patterns = [
    # Routes requiring authentication
    path(
        "/admin/users",
        endpoint=admin_users,
        middlewares=["myapp.middleware.AuthMiddleware"]
    ),
    
    # Multiple middleware (executed in order)
    path(
        "/api/sensitive",
        endpoint=sensitive_api,
        middlewares=[
            "myapp.middleware.AuthMiddleware",
            "myapp.middleware.RateLimitMiddleware",
            "myapp.middleware.LoggingMiddleware"
        ]
    ),
]
```

### OpenAPI Integration

```python
from unfazed.route.params import ResponseSpec
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class ErrorResponse(BaseModel):
    error: str
    code: int

patterns = [
    path(
        "/users/{user_id:int}",
        endpoint=get_user,
        methods=["GET"],
        summary="Get user details",
        description="Get detailed user information by user ID, including username, email, etc.",
        tags=["User Management"],
        response_models=[
            ResponseSpec(
                model=UserResponse,
                code="200",
                description="Successfully retrieved user information"
            ),
            ResponseSpec(
                model=ErrorResponse,
                code="404",
                description="User not found"
            ),
        ],
        externalDocs={
            "description": "User API detailed documentation",
            "url": "https://docs.example.com/users"
        }
    ),
]
```

## Parameter Parsing System

Unfazed routing system's core feature is powerful parameter parsing functionality. For detailed content, please refer to [endpoint documentation](./endpoint.md).

### Basic Parameter Types

```python
import typing as t
from pydantic import BaseModel, Field
from unfazed.route import params as p

# Path parameters
class UserPathParams(BaseModel):
    user_id: int = Field(..., description="User ID")

# Query parameters
class UserQuery(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=10, ge=1, le=100, description="Page size")

# Request body
class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="Email address")

async def create_user(
    request: HttpRequest,
    path_params: t.Annotated[UserPathParams, p.Path()],
    query: t.Annotated[UserQuery, p.Query()],
    user_data: t.Annotated[UserCreateRequest, p.Json()]
) -> JsonResponse:
    return JsonResponse({
        "user_id": path_params.user_id,
        "page": query.page,
        "username": user_data.username
    })
```

## Static Files and Mounting

### Static File Serving

```python
from unfazed.route import static

patterns = [
    # Static file serving
    static("/static", directory="static", name="static"),
    static("/media", directory="uploads", name="media"),
    
    # Support HTML files (SPA applications)
    static("/", directory="dist", html=True, name="frontend"),
]
```

### Mount External Applications

```python
from unfazed.route import mount
from starlette.applications import Starlette

# Create external ASGI application
admin_app = Starlette()

patterns = [
    # Mount to specific path
    mount("/admin", app=admin_app, name="admin"),
    
    # Mount sub-routes
    mount("/api/v2", routes=api_v2_routes, name="api_v2"),
]
```

## Custom Converters

### Built-in Converters

Unfazed supports the following built-in path parameter converters:

- `str`: String (default)
- `int`: Integer
- `float`: Float
- `uuid`: UUID
- `path`: Path (includes slashes)
- `slug`: URL slug

### Custom Converters

```python
# converters.py
from starlette.convertors import Convertor
from unfazed.route import register_url_convertor

class LanguageConvertor(Convertor):
    """Language code converter"""
    regex = r"[a-z]{2}(-[A-Z]{2})?"  # zh, en, zh-CN, en-US

    def convert(self, value: str) -> str:
        return value.lower()

    def to_string(self, value: str) -> str:
        return value

class YearConvertor(Convertor):
    """Year converter"""
    regex = r"[0-9]{4}"

    def convert(self, value: str) -> int:
        return int(value)

    def to_string(self, value: int) -> str:
        return str(value)

# app.py
from unfazed.app import BaseAppConfig

class AppConfig(BaseAppConfig):
    async def ready(self) -> None:
        # Register custom converters
        register_url_convertor("lang", LanguageConvertor())
        register_url_convertor("year", YearConvertor())
```

### Using Custom Converters

```python
# routes.py
patterns = [
    # Use language converter
    path("/{lang:lang}/posts", endpoint=get_posts_by_language),
    
    # Use year converter
    path("/archive/{year:year}", endpoint=get_posts_by_year),
    
    # Combined usage
    path("/{lang:lang}/archive/{year:year}/{month:int}", endpoint=get_monthly_posts),
]

# endpoints.py
async def get_posts_by_language(request: HttpRequest) -> JsonResponse:
    lang = request.path_params["lang"]  # Already converted to lowercase
    return JsonResponse({"language": lang, "posts": []})

async def get_posts_by_year(request: HttpRequest) -> JsonResponse:
    year = request.path_params["year"]  # Already converted to int
    return JsonResponse({"year": year, "posts": []})
```


Through Unfazed's routing system, you can build well-structured, powerful, and maintainable Web applications. The routing system provides a complete solution from simple static routes to complex parameterized routes, while seamlessly integrating with OpenAPI, middleware, parameter parsing, and other systems.
