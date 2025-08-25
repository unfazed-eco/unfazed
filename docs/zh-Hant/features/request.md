Unfazed HttpRequest
=====

Unfazed 的 `HttpRequest` 类继承自 Starlette 的 Request 类，在原有功能基础上增强了 JSON 解析、会话管理、用户认证等功能。它是视图函数的第一个参数，包含了 HTTP 请求的所有信息。

## 类概述

### 核心特性

- **增强的 JSON 解析**: 使用 orjson 提供高性能的 JSON 解析
- **会话管理集成**: 自动集成会话系统，支持多种会话后端
- **用户认证支持**: 内置用户认证系统集成
- **应用实例访问**: 提供对 Unfazed 应用实例的直接访问
- **缓存优化**: JSON 解析结果缓存，避免重复解析

### 类签名

```python
class HttpRequest(Request):
    def __init__(self, scope: Scope, receive: Receive = None) -> None:
        ...
```

## 基本用法

### 简单示例

```python
# endpoints.py
import typing as t
from unfazed.http import HttpRequest, HttpResponse, JsonResponse

async def hello_world(request: HttpRequest) -> HttpResponse:
    """简单的 Hello World 端点"""
    return HttpResponse("Hello, World!")

async def echo_request_info(request: HttpRequest) -> JsonResponse:
    """回显请求信息"""
    return JsonResponse({
        "method": request.method,
        "path": request.path,
        "scheme": request.scheme,
        "client_host": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent")
    })
```

## 请求属性详解

### HTTP 方法 (Method)

获取 HTTP 请求方法：

```python
async def handle_method(request: HttpRequest) -> JsonResponse:
    method = request.method  # GET, POST, PUT, DELETE, etc.
    
    if method == "GET":
        return JsonResponse({"action": "读取数据"})
    elif method == "POST":
        return JsonResponse({"action": "创建数据"})
    elif method == "PUT":
        return JsonResponse({"action": "更新数据"})
    elif method == "DELETE":
        return JsonResponse({"action": "删除数据"})
    else:
        return JsonResponse({"error": "不支持的方法"}, status_code=405)
```

### URL 信息

`HttpRequest` 提供了便捷的 URL 属性访问：

```python
async def analyze_url(request: HttpRequest) -> JsonResponse:
    """分析请求URL的各个组成部分"""
    url_info = {
        # 便捷属性
        "scheme": request.scheme,        # http 或 https
        "path": request.path,           # URL 路径
        
        # 详细URL信息
        "full_url": str(request.url),
        "netloc": request.url.netloc,   # 域名和端口
        "hostname": request.url.hostname,
        "port": request.url.port,
        "query": request.url.query,     # 查询字符串
        "fragment": request.url.fragment,
        "is_secure": request.url.is_secure,  # 是否 HTTPS
        
        # 用户认证信息（如果URL中包含）
        "username": request.url.username,
        "password": request.url.password,
    }
    
    return JsonResponse(url_info)

# 示例请求：https://user:pass@api.example.com:8080/users?page=1#top
# 返回结果：
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

### 应用实例访问

访问 Unfazed 应用实例和相关配置：

```python
async def get_app_info(request: HttpRequest) -> JsonResponse:
    """获取应用信息"""
    # 两种方式访问应用实例
    app = request.unfazed  # 推荐方式
    app_alt = request.app  # 兼容方式
    
    return JsonResponse({
        "project_name": app.settings.PROJECT_NAME,
        "debug_mode": app.settings.DEBUG,
        "installed_apps": app.settings.INSTALLED_APPS or [],
        "middleware_count": len(app.user_middleware),
    })
```

### 客户端信息

获取客户端连接信息：

```python
async def client_info(request: HttpRequest) -> JsonResponse:
    """获取客户端信息"""
    if request.client:
        return JsonResponse({
            "client_host": request.client.host,
            "client_port": request.client.port,
            "connection_info": f"{request.client.host}:{request.client.port}"
        })
    else:
        return JsonResponse({"error": "无法获取客户端信息"})

async def get_real_ip(request: HttpRequest) -> JsonResponse:
    """获取客户端真实IP（考虑代理）"""
    # 优先从代理头获取真实IP
    real_ip = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip() or
        request.headers.get("x-real-ip") or
        (request.client.host if request.client else "unknown")
    )
    
    return JsonResponse({"real_ip": real_ip})
```

### 应用状态访问

通过生命周期管理系统共享的状态：

```python
async def access_shared_state(request: HttpRequest) -> JsonResponse:
    """访问生命周期共享状态"""
    try:
        # 访问由生命周期组件设置的状态
        db_connection = request.state.db_connection
        cache_client = request.state.redis
        
        return JsonResponse({
            "database_available": db_connection is not None,
            "cache_available": cache_client is not None,
            "shared_config": getattr(request.state, "config", {})
        })
    except AttributeError as e:
        return JsonResponse({"error": f"状态未找到: {str(e)}"})
```

> 参考 [lifespan 文档](./lifespan.md) 了解更多状态管理信息。

## 请求数据访问

### 请求头 (Headers)

虽然推荐使用参数化方式处理请求头，但也可以直接访问：

```python
# 推荐的参数化方式
from pydantic import BaseModel, Field
from unfazed.route import params as p

class AuthHeaders(BaseModel):
    authorization: str = Field(..., description="认证令牌")
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

# 直接访问方式
async def direct_headers(request: HttpRequest) -> JsonResponse:
    """直接访问请求头"""
    return JsonResponse({
        "authorization": request.headers.get("authorization"),
        "user_agent": request.headers.get("user-agent", "unknown"),
        "content_length": request.headers.get("content-length", "0"),
        "all_headers": dict(request.headers)
    })
```

> 参考 [endpoint 文档](./endpoint.md) 了解参数化处理方式。

### 查询参数 (Query Parameters)

处理 URL 查询字符串参数：

```python
# 推荐的参数化方式
class SearchQuery(BaseModel):
    keyword: str = Field(..., description="搜索关键词")
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页数量")
    sort: str = Field(default="created_at", description="排序字段")

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

# 直接访问方式
async def direct_query(request: HttpRequest) -> JsonResponse:
    """直接访问查询参数"""
    return JsonResponse({
        "keyword": request.query_params.get("keyword"),
        "page": int(request.query_params.get("page", "1")),
        "size": int(request.query_params.get("size", "10")),
        "all_params": dict(request.query_params)
    })
```

### 路径参数 (Path Parameters)

处理 URL 路径中的动态参数：

```python
# 推荐的参数化方式
class UserPathParams(BaseModel):
    user_id: int = Field(..., description="用户ID")
    action: str = Field(..., description="操作类型")

async def user_action(
    request: HttpRequest,
    path_params: t.Annotated[UserPathParams, p.Path()]
) -> JsonResponse:
    return JsonResponse({
        "user_id": path_params.user_id,
        "action": path_params.action,
        "message": f"对用户 {path_params.user_id} 执行 {path_params.action} 操作"
    })

# 直接访问方式
async def direct_path(request: HttpRequest) -> JsonResponse:
    """直接访问路径参数"""
    return JsonResponse({
        "user_id": request.path_params.get("user_id"),
        "action": request.path_params.get("action"),
        "all_path_params": dict(request.path_params)
    })
```

### Cookies

处理 HTTP Cookies：

```python
# 推荐的参数化方式
class UserCookies(BaseModel):
    session_id: str = Field(..., description="会话ID")
    theme: str = Field(default="light", description="主题设置")
    language: str = Field(default="zh-CN", description="语言设置")

async def with_cookies(
    request: HttpRequest,
    cookies: t.Annotated[UserCookies, p.Cookie()]
) -> JsonResponse:
    return JsonResponse({
        "session_id": cookies.session_id,
        "theme": cookies.theme,
        "language": cookies.language
    })

# 直接访问方式
async def direct_cookies(request: HttpRequest) -> JsonResponse:
    """直接访问 Cookies"""
    return JsonResponse({
        "session_id": request.cookies.get("session_id"),
        "theme": request.cookies.get("theme", "light"),
        "all_cookies": dict(request.cookies)
    })
```

### 请求体 (Request Body)

处理各种格式的请求体数据：

#### JSON 数据

```python
# 推荐的参数化方式
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
        "message": "用户创建成功",
        "user": user_data.model_dump(),
        "validation_passed": True
    })

# 直接访问方式
async def direct_json(request: HttpRequest) -> JsonResponse:
    """直接解析 JSON 请求体"""
    try:
        data = await request.json()  # 使用缓存的高性能解析
        return JsonResponse({
            "received_data": data,
            "data_type": type(data).__name__
        })
    except Exception as e:
        return JsonResponse({"error": f"JSON 解析失败: {str(e)}"}, status_code=400)
```

#### 表单数据

```python
# 推荐的参数化方式
class ContactForm(BaseModel):
    name: str = Field(..., description="姓名")
    email: str = Field(..., description="邮箱")
    message: str = Field(..., description="留言内容")
    subscribe: bool = Field(default=False, description="是否订阅")

async def contact_form(
    request: HttpRequest,
    form_data: t.Annotated[ContactForm, p.Form()]
) -> JsonResponse:
    return JsonResponse({
        "message": "表单提交成功",
        "form_data": form_data.model_dump()
    })

# 直接访问方式
async def direct_form(request: HttpRequest) -> JsonResponse:
    """直接处理表单数据"""
    form_data = await request.form()
    return JsonResponse({
        "name": form_data.get("name"),
        "email": form_data.get("email"),
        "message": form_data.get("message"),
        "all_form_data": dict(form_data)
    })
```

### 文件上传

处理文件上传请求：

```python
from unfazed.file import UploadFile

# 推荐的参数化方式
async def upload_file(
    request: HttpRequest,
    file: t.Annotated[UploadFile, p.File(description="上传的文件")]
) -> JsonResponse:
    """处理单文件上传"""
    return JsonResponse({
        "filename": file.filename,
        "content_type": file.content_type,
        "size": file.size,
        "message": "文件上传成功"
    })

# 多文件上传
async def upload_multiple_files(
    request: HttpRequest,
    avatar: t.Annotated[UploadFile, p.File(description="头像文件")],
    document: t.Annotated[UploadFile, p.File(description="文档文件")]
) -> JsonResponse:
    """处理多文件上传"""
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

# 直接访问方式
async def direct_file_upload(request: HttpRequest) -> JsonResponse:
    """直接处理文件上传"""
    form_data = await request.form()
    
    uploaded_files = []
    for field_name, file_data in form_data.items():
        if hasattr(file_data, 'filename'):  # 是文件对象
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

## 会话和认证

### 会话管理

访问和操作用户会话：

```python
async def session_demo(request: HttpRequest) -> JsonResponse:
    """会话管理示例"""
    try:
        # 读取会话数据
        user_id = request.session.get("user_id")
        username = request.session.get("username")
        
        # 设置会话数据
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
            "hint": "请确保已安装 SessionMiddleware"
        }, status_code=500)
```

### 用户认证

访问认证用户信息：

```python
async def user_profile(request: HttpRequest) -> JsonResponse:
    """获取用户资料"""
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
                "message": "用户未登录"
            }, status_code=401)
            
    except ValueError as e:
        return JsonResponse({
            "error": str(e),
            "hint": "请确保已安装 AuthenticationMiddleware"
        }, status_code=500)

async def require_auth(request: HttpRequest) -> JsonResponse:
    """需要认证的端点"""
    try:
        if not request.user:
            return JsonResponse({"error": "需要登录"}, status_code=401)
        
        return JsonResponse({
            "message": f"欢迎，{request.user.username}！",
            "user_permissions": getattr(request.user, 'permissions', [])
        })
    except ValueError:
        return JsonResponse({"error": "认证系统未配置"}, status_code=500)
```

## 实用工具方法

### 内容类型检测

```python
async def content_type_handler(request: HttpRequest) -> JsonResponse:
    """根据内容类型处理请求"""
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

### 请求验证

```python
async def validate_request(request: HttpRequest) -> JsonResponse:
    """请求验证示例"""
    errors = []
    
    # 验证 HTTP 方法
    if request.method not in ["GET", "POST", "PUT", "DELETE"]:
        errors.append("不支持的 HTTP 方法")
    
    # 验证内容类型
    if request.method in ["POST", "PUT"]:
        content_type = request.headers.get("content-type", "")
        if not content_type:
            errors.append("缺少 Content-Type 头")
    
    # 验证认证头
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        errors.append("缺少或无效的认证头")
    
    if errors:
        return JsonResponse({"errors": errors}, status_code=400)
    
    return JsonResponse({"message": "请求验证通过"})
```

通过 Unfazed 的 `HttpRequest` 类，您可以方便地访问和处理各种类型的 HTTP 请求数据。建议在实际项目中优先使用参数化的方式处理请求数据，这样可以获得更好的类型安全和自动验证功能。