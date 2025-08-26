Unfazed OpenAPI 文档系统
=====

Unfazed 内置了强大的 OpenAPI 文档生成系统，基于 OpenAPI 3.1.1 标准，自动从您的端点函数和类型注解生成完整的 API 文档。系统提供 Swagger UI 和 ReDoc 两种文档界面，支持交互式 API 测试和美观的文档展示。

## 系统概述

### 核心特性

- **自动生成**: 基于类型注解和 Pydantic 模型自动生成 OpenAPI 规范
- **双界面支持**: 提供 Swagger UI 和 ReDoc 两种文档界面
- **交互测试**: 支持在线 API 测试和参数验证
- **类型安全**: 完整支持 Python 类型系统和 Pydantic 验证
- **高度定制**: 支持自定义 CDN、主题和配置选项

### 核心组件

- **OpenApi**: 核心 OpenAPI 规范生成器
- **OpenApiService**: 文档服务提供者，管理 HTML 模板和静态资源
- **内置视图函数**: 自动提供 `/openapi/docs`、`/openapi/redoc`、`/openapi/openapi.json` 路由
- **配置系统**: 灵活的配置管理，支持开发和生产环境

### 支持的参数类型

- **Path 参数**: 路径参数提取和验证
- **Query 参数**: 查询字符串参数处理
- **Header 参数**: HTTP 头部参数验证
- **Cookie 参数**: Cookie 值提取
- **Request Body**: JSON、Form、文件上传支持
- **Response Models**: 响应模型定义和文档生成

## 快速开始

### 1. 基础配置

```python
# settings.py
UNFAZED_SETTINGS = {
    "OPENAPI": {
        "info": {
            "title": "My API",
            "version": "1.0.0",
            "description": "一个使用 Unfazed 构建的 API 系统",
            "termsOfService": "https://example.com/terms",
            "contact": {
                "name": "API 支持团队",
                "url": "https://example.com/contact", 
                "email": "support@example.com"
            },
            "license": {
                "name": "MIT License",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "servers": [
            {"url": "https://api.example.com", "description": "生产环境"},
            {"url": "https://staging-api.example.com", "description": "测试环境"},
            {"url": "http://127.0.0.1:9527", "description": "本地开发"}
        ],
    }
}
```

### 2. 定义数据模型

```python
# models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import StrEnum
from datetime import datetime

class UserRole(StrEnum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserQuery(BaseModel):
    """用户查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=10, ge=1, le=100, description="每页数量")
    role: Optional[UserRole] = Field(default=None, description="用户角色过滤")
    keyword: Optional[str] = Field(default=None, description="搜索关键词")

class UserCreate(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, description="密码")
    role: UserRole = Field(default=UserRole.USER, description="用户角色")
    profile: Optional[dict] = Field(default=None, description="用户资料")

class UserResponse(BaseModel):
    """用户响应模型"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    role: UserRole = Field(..., description="角色")
    is_active: bool = Field(..., description="是否活跃")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

class UserListResponse(BaseModel):
    """用户列表响应"""
    users: List[UserResponse] = Field(..., description="用户列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误信息")
    code: int = Field(..., description="错误代码")
    details: Optional[dict] = Field(default=None, description="错误详情")
```

### 3. 编写 API 视图函数

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
    description="成功获取用户列表",
    examples={
        "success": {
            "summary": "成功示例",
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
    获取用户列表
    
    支持分页查询和角色过滤，需要提供有效的认证令牌。
    """
    # 模拟业务逻辑
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
    description="成功创建用户",
    code="201"
)]:
    """
    创建新用户
    
    创建一个新的用户账户，需要管理员权限。
    """
    # 模拟创建用户
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
    user_id: t.Annotated[int, params.Path(description="用户ID")],
    authorization: t.Annotated[str, params.Header(description="Bearer token")]
) -> t.Annotated[JsonResponse, ResponseSpec(model=UserResponse)]:
    """根据ID获取用户详情"""
    
    # 模拟查找用户
    if user_id == 404:
        return JsonResponse(
            ErrorResponse(error="用户不存在", code=404).model_dump(),
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

### 4. 配置路由

```python
# routes.py
from unfazed.route import path
from .endpoints import get_users, create_user, get_user_by_id

patterns = [
    path(
        "/api/users",
        endpoint=get_users,
        methods=["GET"],
        tags=["用户管理"],
        summary="获取用户列表",
        description="获取系统中的用户列表，支持分页和过滤"
    ),
    path(
        "/api/users",
        endpoint=create_user,
        methods=["POST"],
        tags=["用户管理"],
        summary="创建用户",
        description="创建新的用户账户"
    ),
    path(
        "/api/users/{user_id}",
        endpoint=get_user_by_id,
        methods=["GET"],
        tags=["用户管理"],
        summary="获取用户详情",
        description="根据用户ID获取用户的详细信息"
    ),
]
```

### 5. 启动服务并访问文档

```bash
# 启动开发服务器
uvicorn asgi:application --host 0.0.0.0 --port 9527 --reload
```

**访问文档界面：**

- **Swagger UI**: `http://127.0.0.1:9527/openapi/docs`
- **ReDoc**: `http://127.0.0.1:9527/openapi/redoc`
- **OpenAPI JSON**: `http://127.0.0.1:9527/openapi/openapi.json`

## 高级功能

### 响应模型定义

```python
from unfazed.route.params import ResponseSpec

# 单一响应模型
async def simple_endpoint() -> t.Annotated[JsonResponse, ResponseSpec(
    model=UserResponse,
    description="用户信息"
)]:
    pass

# 多状态码响应
async def complex_endpoint() -> JsonResponse:
    pass

# 在路由中定义响应模型
patterns = [
    path(
        "/api/complex",
        endpoint=complex_endpoint,
        response_models=[
            ResponseSpec(
                model=UserResponse,
                code="200",
                description="操作成功",
                content_type="application/json"
            ),
            ResponseSpec(
                model=ErrorResponse,
                code="400",
                description="请求参数错误",
                content_type="application/json"
            ),
            ResponseSpec(
                model=ErrorResponse,
                code="401",
                description="未授权访问",
                content_type="application/json"
            )
        ]
    )
]
```

### 文件上传

```python
from unfazed.file import UploadFile

class FileUploadForm(BaseModel):
    """文件上传表单"""
    title: str = Field(..., description="文件标题")
    description: Optional[str] = Field(default=None, description="文件描述")

async def upload_file(
    request: HttpRequest,
    form_data: t.Annotated[FileUploadForm, params.Form()],
    file: t.Annotated[UploadFile, params.File(description="要上传的文件")]
) -> t.Annotated[JsonResponse, ResponseSpec(
    model=dict,
    description="文件上传成功"
)]:
    """
    文件上传接口
    
    支持各种格式的文件上传，最大支持 10MB。
    """
    return JsonResponse({
        "filename": file.filename,
        "size": file.size,
        "content_type": file.content_type,
        "title": form_data.title,
        "description": form_data.description
    })

# 路由配置
patterns = [
    path(
        "/api/upload",
        endpoint=upload_file,
        methods=["POST"],
        tags=["文件管理"],
        summary="上传文件"
    )
]
```

## 完整配置详解

### OpenAPI 配置选项

```python
UNFAZED_SETTINGS = {
    "OPENAPI": {
        # OpenAPI 规范版本
        "openapi": "3.1.1",
        
        # API 基本信息
        "info": {
            "title": "My API",
            "version": "1.0.0", 
            "description": "API 描述",
            "termsOfService": "https://example.com/terms",
            "contact": {
                "name": "支持团队",
                "url": "https://example.com/contact",
                "email": "support@example.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        
        # 服务器配置
        "servers": [
            {"url": "https://api.example.com", "description": "生产环境"},
            {"url": "http://localhost:9527", "description": "开发环境"}
        ],
        
        # 外部文档链接
        "externalDocs": {
            "description": "完整文档",
            "url": "https://docs.example.com"
        },
        
        # 文档界面配置
        "json_route": "/openapi/openapi.json",  # OpenAPI JSON 路由
        
        # Swagger UI 配置
        "swagger_ui": {
            "css": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
            "js": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            "favicon": "https://www.openapis.org/wp-content/uploads/sites/3/2016/11/favicon.png"
        },
        
        # ReDoc 配置
        "redoc": {
            "js": "https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"
        },
        
        # 访问控制
        "allow_public": True  # 生产环境建议设为 False
    }
}
```

### 自定义 CDN 配置

```python
# 使用国内 CDN 加速
UNFAZED_SETTINGS = {
    "OPENAPI": {
        "swagger_ui": {
            "css": "https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
            "js": "https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            "favicon": "/static/favicon.ico"  # 使用本地图标
        },
        "redoc": {
            "js": "https://unpkg.com/redoc@latest/bundles/redoc.standalone.js"
        }
    }
}
```

### 路由级配置

```python
patterns = [
    # 包含在文档中
    path(
        "/api/public",
        endpoint=public_endpoint,
        include_in_schema=True,  # 默认值
        tags=["公开接口"],
        summary="公开接口",
        description="无需认证的公开接口"
    ),
    
    # 排除在文档外
    path(
        "/internal/health",
        endpoint=health_check,
        include_in_schema=False,  # 不在文档中显示
        tags=["内部接口"]
    ),
    
    # 自定义响应模型
    path(
        "/api/custom",
        endpoint=custom_endpoint,
        response_models=[
            ResponseSpec(model=SuccessResponse, code="200"),
            ResponseSpec(model=ErrorResponse, code="400")
        ],
        tags=["自定义接口"],
        deprecated=False,  # 是否已弃用
        externalDocs={
            "description": "详细文档",
            "url": "https://docs.example.com/custom"
        }
    )
]
```

## 生产环境部署

### 安全配置

```python
# production_settings.py
UNFAZED_SETTINGS = {
    "OPENAPI": {
        "allow_public": False,  # 禁止公开访问
        "info": {
            "title": "Production API",
            "version": "1.0.0"
        },
        "servers": [
            {"url": "https://api.yourdomain.com", "description": "生产环境"}
        ]
    }
}
```

### 条件性启用文档

```python
import os

# 根据环境变量控制文档可用性
ENABLE_DOCS = os.getenv("ENABLE_API_DOCS", "false").lower() == "true"

if ENABLE_DOCS:
    UNFAZED_SETTINGS["OPENAPI"] = {
        "allow_public": True,
        "info": {"title": "API Docs", "version": "1.0.0"}
    }
else:
    # 生产环境不启用 OpenAPI
    UNFAZED_SETTINGS["OPENAPI"] = None
```

通过 Unfazed 的 OpenAPI 系统，您可以轻松构建出专业、完整、交互式的 API 文档。该系统不仅提高了开发效率，还为 API 的使用者提供了优秀的开发体验。
