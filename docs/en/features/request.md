Unfazed HttpRequest
=====

Unfazed's `HttpRequest` class inherits from Starlette's Request class, enhancing the original functionality with JSON parsing, session management, user authentication, and more. It is the first parameter of view functions and contains all information about HTTP requests.

## Class Overview

### Core Features

- **Enhanced JSON Parsing**: Uses orjson to provide high-performance JSON parsing
- **Session Management Integration**: Automatically integrates session system, supports multiple session backends
- **User Authentication Support**: Built-in user authentication system integration
- **Application Instance Access**: Provides direct access to Unfazed application instance
- **Cache Optimization**: JSON parsing results are cached to avoid repeated parsing

### Class Signature

```python
class HttpRequest(Request):
    def __init__(self, scope: Scope, receive: Receive = None) -> None:
        ...
```

## Basic Usage

### Simple Example

```python
# endpoints.py
import typing as t
from unfazed.http import HttpRequest, HttpResponse, JsonResponse

async def hello_world(request: HttpRequest) -> HttpResponse:
    """Simple Hello World endpoint"""
    return HttpResponse("Hello, World!")

async def echo_request_info(request: HttpRequest) -> JsonResponse:
    """Echo request information"""
    return JsonResponse({
        "method": request.method,
        "path": request.path,
        "scheme": request.scheme,
        "client_host": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent")
    })
```

## Request Attributes Details

### HTTP Method

Get HTTP request method:

```python
async def handle_method(request: HttpRequest) -> JsonResponse:
    method = request.method  # GET, POST, PUT, DELETE, etc.
    
    if method == "GET":
        return JsonResponse({"action": "Read data"})
    elif method == "POST":
        return JsonResponse({"action": "Create data"})
    elif method == "PUT":
        return JsonResponse({"action": "Update data"})
    elif method == "DELETE":
        return JsonResponse({"action": "Delete data"})
    else:
        return JsonResponse({"error": "Unsupported method"}, status_code=405)
```

### URL Information

`HttpRequest` provides convenient URL attribute access:

```python
async def analyze_url(request: HttpRequest) -> JsonResponse:
    """Analyze various components of request URL"""
    url_info = {
        # Convenient attributes
        "scheme": request.scheme,        # http or https
        "path": request.path,           # URL path
        
        # Detailed URL information
        "full_url": str(request.url),
        "netloc": request.url.netloc,   # Domain and port
        "hostname": request.url.hostname,
        "port": request.url.port,
        "query": request.url.query,     # Query string
        "fragment": request.url.fragment,
        "is_secure": request.url.is_secure,  # Whether HTTPS
        
        # User authentication information (if included in URL)
        "username": request.url.username,
        "password": request.url.password,
    }
    
    return JsonResponse(url_info)

# Example request: https://user:pass@api.example.com:8080/users?page=1#top
# Return result:
# {
#     "scheme": "https",
#     "path": "/users",
#     "netloc": "api.example.com:8080",
#     "hostname": "api.example.com",
#     "port": 8080,
#     "query": "page=1",
#     "fragment": "top",
#     "is_secure": true,
#     "username": "user",
#     "password": "pass"
# }
```

### Application Instance Access

Access Unfazed application instance and related configuration:

```python
async def get_app_info(request: HttpRequest) -> JsonResponse:
    """Get application information"""
    # Two ways to access application instance
    app = request.unfazed  # Recommended way
    app_alt = request.app  # Compatible way
    
    return JsonResponse({
        "project_name": app.settings.PROJECT_NAME,
        "debug_mode": app.settings.DEBUG,
        "installed_apps": app.settings.INSTALLED_APPS or [],
        "middleware_count": len(app.user_middleware),
    })
```

### Client Information

Get client connection information:

```python
async def client_info(request: HttpRequest) -> JsonResponse:
    """Get client information"""
    if request.client:
        return JsonResponse({
            "client_host": request.client.host,
            "client_port": request.client.port,
            "connection_info": f"{request.client.host}:{request.client.port}"
        })
    else:
        return JsonResponse({"error": "Unable to get client information"})

async def get_real_ip(request: HttpRequest) -> JsonResponse:
    """Get client real IP (considering proxy)"""
    # Prioritize getting real IP from proxy headers
    real_ip = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip() or
        request.headers.get("x-real-ip") or
        (request.client.host if request.client else "unknown")
    )
    
    return JsonResponse({"real_ip": real_ip})
```

### Application State Access

Shared state through lifecycle management system:

```python
async def access_shared_state(request: HttpRequest) -> JsonResponse:
    """Access lifecycle shared state"""
    try:
        # Access state set by lifecycle components
        db_connection = request.state.db_connection
        cache_client = request.state.redis
        
        return JsonResponse({
            "database_available": db_connection is not None,
            "cache_available": cache_client is not None,
            "shared_config": getattr(request.state, "config", {})
        })
    except AttributeError as e:
        return JsonResponse({"error": f"State not found: {str(e)}"})
```

> Refer to [lifespan documentation](./lifespan.md) for more state management information.

## Request Data Access

### Request Headers

Although parameterized approach is recommended for handling request headers, direct access is also possible:

```python
# Recommended parameterized approach
from pydantic import BaseModel, Field
from unfazed.route import params as p

class AuthHeaders(BaseModel):
    authorization: str = Field(..., description="Authentication token")
    user_agent: str = Field(default="unknown", alias="user-agent")
    content_type: str = Field(default="application/json", alias="content-type")

async def with_headers(
    request: HttpRequest,
    headers: t.Annotated[AuthHeaders, p.Header()]
) -> JsonResponse:
    return JsonResponse({
        "auth_token": headers.authorization,
        "user_agent": headers.user_agent,
        "content_type": headers.content_type
    })

# Direct access approach
async def direct_headers(request: HttpRequest) -> JsonResponse:
    """Direct access to request headers"""
    return JsonResponse({
        "authorization": request.headers.get("authorization"),
        "user_agent": request.headers.get("user-agent", "unknown"),
        "content_length": request.headers.get("content-length", "0"),
        "all_headers": dict(request.headers)
    })
```

> Refer to [endpoint documentation](./endpoint.md) for parameterized processing approaches.

### Query Parameters

Handle URL query string parameters:

```python
# Recommended parameterized approach
class SearchQuery(BaseModel):
    keyword: str = Field(..., description="Search keyword")
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=10, ge=1, le=100, description="Page size")
    sort: str = Field(default="created_at", description="Sort field")

async def search_with_params(
    request: HttpRequest,
    query: t.Annotated[SearchQuery, p.Query()]
) -> JsonResponse:
    return JsonResponse({
        "keyword": query.keyword,
        "page": query.page,
        "size": query.size,
        "sort": query.sort,
        "offset": (query.page - 1) * query.size
    })

# Direct access approach
async def direct_query(request: HttpRequest) -> JsonResponse:
    """Direct access to query parameters"""
    return JsonResponse({
        "keyword": request.query_params.get("keyword"),
        "page": int(request.query_params.get("page", "1")),
        "size": int(request.query_params.get("size", "10")),
        "all_params": dict(request.query_params)
    })
```

### Path Parameters

Handle dynamic parameters in URL paths:

```python
# Recommended parameterized approach
class UserPathParams(BaseModel):
    user_id: int = Field(..., description="User ID")
    action: str = Field(..., description="Action type")

async def user_action(
    request: HttpRequest,
    path_params: t.Annotated[UserPathParams, p.Path()]
) -> JsonResponse:
    return JsonResponse({
        "user_id": path_params.user_id,
        "action": path_params.action,
        "message": f"Execute {path_params.action} operation on user {path_params.user_id}"
    })

# Direct access approach
async def direct_path(request: HttpRequest) -> JsonResponse:
    """Direct access to path parameters"""
    return JsonResponse({
        "user_id": request.path_params.get("user_id"),
        "action": request.path_params.get("action"),
        "all_path_params": dict(request.path_params)
    })
```

### Cookies

Handle HTTP Cookies:

```python
# Recommended parameterized approach
class UserCookies(BaseModel):
    session_id: str = Field(..., description="Session ID")
    theme: str = Field(default="light", description="Theme setting")
    language: str = Field(default="en-US", description="Language setting")

async def with_cookies(
    request: HttpRequest,
    cookies: t.Annotated[UserCookies, p.Cookie()]
) -> JsonResponse:
    return JsonResponse({
        "session_id": cookies.session_id,
        "theme": cookies.theme,
        "language": cookies.language
    })

# Direct access approach
async def direct_cookies(request: HttpRequest) -> JsonResponse:
    """Direct access to Cookies"""
    return JsonResponse({
        "session_id": request.cookies.get("session_id"),
        "theme": request.cookies.get("theme", "light"),
        "all_cookies": dict(request.cookies)
    })
```

### Request Body

Handle various formats of request body data:

#### JSON Data

```python
# Recommended parameterized approach
class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=1, le=150)
    profile: dict = Field(default_factory=dict)

async def create_user(
    request: HttpRequest,
    user_data: t.Annotated[UserCreateRequest, p.Json()]
) -> JsonResponse:
    return JsonResponse({
        "message": "User created successfully",
        "user": user_data.model_dump(),
        "validation_passed": True
    })

# Direct access approach
async def direct_json(request: HttpRequest) -> JsonResponse:
    """Direct JSON request body parsing"""
    try:
        data = await request.json()  # Use cached high-performance parsing
        return JsonResponse({
            "received_data": data,
            "data_type": type(data).__name__
        })
    except Exception as e:
        return JsonResponse({"error": f"JSON parsing failed: {str(e)}"}, status_code=400)
```

#### Form Data

```python
# Recommended parameterized approach
class ContactForm(BaseModel):
    name: str = Field(..., description="Name")
    email: str = Field(..., description="Email")
    message: str = Field(..., description="Message content")
    subscribe: bool = Field(default=False, description="Subscribe or not")

async def contact_form(
    request: HttpRequest,
    form_data: t.Annotated[ContactForm, p.Form()]
) -> JsonResponse:
    return JsonResponse({
        "message": "Form submitted successfully",
        "form_data": form_data.model_dump()
    })

# Direct access approach
async def direct_form(request: HttpRequest) -> JsonResponse:
    """Direct form data processing"""
    form_data = await request.form()
    return JsonResponse({
        "name": form_data.get("name"),
        "email": form_data.get("email"),
        "message": form_data.get("message"),
        "all_form_data": dict(form_data)
    })
```

### File Upload

Handle file upload requests:

```python
from unfazed.file import UploadFile

# Recommended parameterized approach
async def upload_file(
    request: HttpRequest,
    file: t.Annotated[UploadFile, p.File(description="Uploaded file")]
) -> JsonResponse:
    """Handle single file upload"""
    return JsonResponse({
        "filename": file.filename,
        "content_type": file.content_type,
        "size": file.size,
        "message": "File uploaded successfully"
    })

# Multiple file upload
async def upload_multiple_files(
    request: HttpRequest,
    avatar: t.Annotated[UploadFile, p.File(description="Avatar file")],
    document: t.Annotated[UploadFile, p.File(description="Document file")]
) -> JsonResponse:
    """Handle multiple file upload"""
    return JsonResponse({
        "avatar": {
            "filename": avatar.filename,
            "size": avatar.size,
            "type": avatar.content_type
        },
        "document": {
            "filename": document.filename,
            "size": document.size,
            "type": document.content_type
        }
    })

# Direct access approach
async def direct_file_upload(request: HttpRequest) -> JsonResponse:
    """Direct file upload processing"""
    form_data = await request.form()
    
    uploaded_files = []
    for field_name, file_data in form_data.items():
        if hasattr(file_data, 'filename'):  # Is file object
            uploaded_files.append({
                "field_name": field_name,
                "filename": file_data.filename,
                "content_type": file_data.content_type,
                "size": len(await file_data.read())
            })
    
    return JsonResponse({
        "uploaded_files": uploaded_files,
        "total_files": len(uploaded_files)
    })
```

## Session and Authentication

### Session Management

Access and manipulate user sessions:

```python
async def session_demo(request: HttpRequest) -> JsonResponse:
    """Session management example"""
    try:
        # Read session data
        user_id = request.session.get("user_id")
        username = request.session.get("username")
        
        # Set session data
        request.session["last_visit"] = "2024-01-01T00:00:00"
        request.session["page_views"] = request.session.get("page_views", 0) + 1
        
        return JsonResponse({
            "user_id": user_id,
            "username": username,
            "page_views": request.session["page_views"],
            "session_key": request.session.session_key
        })
    except ValueError as e:
        return JsonResponse({
            "error": str(e),
            "hint": "Please ensure SessionMiddleware is installed"
        }, status_code=500)
```

### User Authentication

Access authenticated user information:

```python
async def user_profile(request: HttpRequest) -> JsonResponse:
    """Get user profile"""
    try:
        user = request.user
        
        if user:
            return JsonResponse({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "is_authenticated": True
            })
        else:
            return JsonResponse({
                "is_authenticated": False,
                "message": "User not logged in"
            }, status_code=401)
            
    except ValueError as e:
        return JsonResponse({
            "error": str(e),
            "hint": "Please ensure AuthenticationMiddleware is installed"
        }, status_code=500)

async def require_auth(request: HttpRequest) -> JsonResponse:
    """Endpoint requiring authentication"""
    try:
        if not request.user:
            return JsonResponse({"error": "Login required"}, status_code=401)
        
        return JsonResponse({
            "message": f"Welcome, {request.user.username}!",
            "user_permissions": getattr(request.user, 'permissions', [])
        })
    except ValueError:
        return JsonResponse({"error": "Authentication system not configured"}, status_code=500)
```

## Utility Methods

### Content Type Detection

```python
async def content_type_handler(request: HttpRequest) -> JsonResponse:
    """Handle requests based on content type"""
    content_type = request.headers.get("content-type", "")
    
    if "application/json" in content_type:
        data = await request.json()
        return JsonResponse({"type": "json", "data": data})
    elif "application/x-www-form-urlencoded" in content_type:
        data = await request.form()
        return JsonResponse({"type": "form", "data": dict(data)})
    elif "multipart/form-data" in content_type:
        data = await request.form()
        return JsonResponse({"type": "multipart", "fields": list(data.keys())})
    else:
        body = await request.body()
        return JsonResponse({
            "type": "raw",
            "content_type": content_type,
            "body_length": len(body)
        })
```

### Request Validation

```python
async def validate_request(request: HttpRequest) -> JsonResponse:
    """Request validation example"""
    errors = []
    
    # Validate HTTP method
    if request.method not in ["GET", "POST", "PUT", "DELETE"]:
        errors.append("Unsupported HTTP method")
    
    # Validate content type
    if request.method in ["POST", "PUT"]:
        content_type = request.headers.get("content-type", "")
        if not content_type:
            errors.append("Missing Content-Type header")
    
    # Validate authentication header
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        errors.append("Missing or invalid authentication header")
    
    if errors:
        return JsonResponse({"errors": errors}, status_code=400)
    
    return JsonResponse({"message": "Request validation passed"})
```

Through Unfazed's `HttpRequest` class, you can conveniently access and handle various types of HTTP request data. It is recommended to prioritize parameterized approaches for handling request data in actual projects, as this provides better type safety and automatic validation functionality.
