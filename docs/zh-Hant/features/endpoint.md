Unfazed Endpoint 系统
=====

Endpoint 是 Unfazed 框架中的核心组件，作为路由分发和业务逻辑处理之间的桥梁。它提供了强大的参数解析、类型验证和 API 文档生成功能。

## 系统架构

Unfazed 的 Endpoint 系统包含以下核心组件：

### EndpointHandler
负责处理请求参数的解析和验证，支持：
- 自动参数类型转换
- 请求验证和错误处理
- 同步和异步端点执行
- 参数注入和依赖解析

### EndPointDefinition
负责视图函数的元数据定义和模型构建：
- 解析函数签名和类型注解
- 构建请求参数模型（Path、Query、Header、Cookie、Body）
- 生成 OpenAPI 文档规范
- 支持 HttpResponse 模型定义

### 参数类型系统
支持多种参数来源和类型：
- **Path**: 路径参数（如 `/users/{user_id}`）
- **Query**: 查询参数（如 `?page=1&size=10`）
- **Header**: 请求头参数
- **Cookie**: Cookie 参数
- **Json**: JSON 请求体
- **Form**: 表单数据
- **File**: 文件上传

## 快速开始

### 基础视图函数

创建一个简单的视图函数：

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
    user_data = UserResponse(id=1, name="张三", email="zhangsan@example.com")
    return JsonResponse(user_data)
```

### 路由注册

将视图函数连接到路由系统：

```python
# routes.py
from unfazed.route import path
from .endpoints import hello_world, get_user

patterns = [
    path("/", endpoint=hello_world),
    path("/user", endpoint=get_user, methods=["GET"]),
]
```

### 视图函数特性

Unfazed 的视图函数系统具有以下特性：

1. **类型安全**: 基于 Python 类型注解进行参数验证
2. **自动文档**: 自动生成 OpenAPI/Swagger 文档
3. **依赖注入**: 自动解析和注入请求参数
4. **异步支持**: 原生支持 async/await
5. **错误处理**: 统一的错误处理和验证机制（依赖中间件处理）


## 请求参数系统

Unfazed 提供了强大的请求参数解析系统，支持多种参数来源和自动类型验证。系统支持以下参数类型：

| 参数类型   | 描述                            | 示例                                |
| ---------- | ------------------------------- | ----------------------------------- |
| **Path**   | 路径参数，从 URL 路径中提取     | `/users/{user_id}`                  |
| **Query**  | 查询参数，从 URL 查询字符串提取 | `?page=1&size=10`                   |
| **Header** | 请求头参数                      | `Authorization: Bearer token`       |
| **Cookie** | Cookie 参数                     | `session_id=abc123`                 |
| **Json**   | JSON 请求体                     | `{"name": "张三"}`                  |
| **Form**   | 表单数据                        | `application/x-www-form-urlencoded` |
| **File**   | 文件上传                        | `multipart/form-data`               |

### 参数定义方式

参数可以通过两种方式定义：

#### 1. 使用 typing.Annotated 注解（推荐）

```python
import typing as t
from unfazed.route import params as p

async def endpoint(
    request: HttpRequest,
    user_id: t.Annotated[int, p.Path()],              # 路径参数
    page: t.Annotated[int, p.Query(default=1)],       # 查询参数，带默认值
    auth: t.Annotated[str, p.Header()],               # 请求头参数
) -> JsonResponse:
    ...
```

#### 2. 自动推断（简化写法）

在实际的业务开发中，尽量避免使用自动推断，清晰的参数定义方式，可以提高代码的可读性和可维护性。

```python
async def endpoint(
    request: HttpRequest,
    user_id: int,        # 如果在路径中定义，自动识别为 Path 参数
    page: int,           # 基础类型自动识别为 Query 参数
    user: UserModel,     # BaseModel 类型自动识别为 Json 参数
) -> JsonResponse:
    ...
```

#### 3. 自动合并

同类型的参数可以自动合并，比如：

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
    return JsonResponse({"message": f"获取用户 {name} 成功", "age": age, "sex": profile.sex, "height": profile.height, "weight": profile.weight})


```

### 参数验证和错误处理

系统会自动验证参数类型和必填性：

```python
from pydantic import Field, BaseModel

class UserCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50, description="用户名")
    age: int = Field(ge=0, le=150, description="年龄")
    email: str = Field(regex=r'^[^@]+@[^@]+\.[^@]+$', description="邮箱")

async def create_user(
    request: HttpRequest,
    user_data: t.Annotated[UserCreateRequest, p.Json()]
) -> JsonResponse:
    # 参数会自动验证，如果验证失败会返回错误
    return JsonResponse({"message": f"创建用户 {user_data.name} 成功"})
```

下面详细介绍各种参数类型的使用方法。


### Path 参数

Path 参数从 URL 路径中提取，支持基础类型和复杂模型。

#### 基础用法

```python
import typing as t
from pydantic import BaseModel, Field
from unfazed.http import HttpRequest, JsonResponse
from unfazed.route import params as p


# 基础类型的路径参数
async def get_user(
    request: HttpRequest,
    user_id: t.Annotated[int, p.Path(description="用户ID")],
    category: t.Annotated[str, p.Path(description="用户分类")]
) -> JsonResponse:
    return JsonResponse({
        "user_id": user_id,
        "category": category
    })


# 路由定义
patterns = [
    path("/users/{user_id}/category/{category}", endpoint=get_user),
]

# 请求示例: GET /users/123/category/vip
# 结果: {"user_id": 123, "category": "vip"}
```

#### 使用 BaseModel 组织路径参数

```python
class UserPathParams(BaseModel):
    user_id: int = Field(description="用户ID", gt=0)
    org_id: int = Field(description="组织ID", gt=0)


class ProjectPathParams(BaseModel):
    project_id: str = Field(description="项目ID", min_length=1)
    version: str = Field(default="latest", description="版本号")


async def get_user_project(
    request: HttpRequest,
    user_params: t.Annotated[UserPathParams, p.Path()],
    project_params: t.Annotated[ProjectPathParams, p.Path()],
    action: t.Annotated[str, p.Path(default="view")]  # 单独的路径参数
) -> JsonResponse:
    return JsonResponse({
        "user_id": user_params.user_id,
        "org_id": user_params.org_id,
        "project_id": project_params.project_id,
        "version": project_params.version,
        "action": action
    })


# 路由定义
patterns = [
    path("/orgs/{org_id}/users/{user_id}/projects/{project_id}/{version}/{action}", 
         endpoint=get_user_project),
]

# 请求示例: GET /orgs/1/users/123/projects/myapp/v1.0/edit
```

#### 自动推断路径参数

```python
async def simple_path_endpoint(
    request: HttpRequest,
    user_id: int,      # 自动识别为路径参数（因为在路由中定义了 {user_id}）
    post_id: int,      # 自动识别为路径参数（因为在路由中定义了 {post_id}）
) -> JsonResponse:
    return JsonResponse({
        "user_id": user_id,
        "post_id": post_id
    })

# 路由定义
patterns = [
    path("/users/{user_id}/posts/{post_id}", endpoint=simple_path_endpoint),
]
```

#### 路径参数特性

- **类型转换**: 自动转换为指定的 Python 类型
- **验证**: 支持 Pydantic 的所有验证规则
- **文档生成**: 自动生成 OpenAPI 参数文档
- **错误处理**: 类型转换失败时返回错误(依赖中间件处理)


### Query 参数

Query 参数从 URL 查询字符串中提取，常用于分页、过滤和搜索等场景。

#### 基础用法

```python
# 基础类型的查询参数
async def search_users(
    request: HttpRequest,
    keyword: t.Annotated[str, p.Query(description="搜索关键词")],
    page: t.Annotated[int, p.Query(default=1, description="页码", ge=1)],
    size: t.Annotated[int, p.Query(default=10, description="每页大小", ge=1, le=100)],
    active: t.Annotated[bool, p.Query(default=True, description="是否激活")]
) -> JsonResponse:
    return JsonResponse({
        "keyword": keyword,
        "page": page,
        "size": size,
        "active": active,
        "results": []  # 模拟搜索结果
    })

# 请求示例: GET /search?keyword=张三&page=2&size=20&active=false
```

#### 使用 BaseModel 组织查询参数

```python
class SearchParams(BaseModel):
    keyword: str = Field(description="搜索关键词", min_length=1)
    category: str = Field(default="all", description="分类")


class PaginationParams(BaseModel):
    page: int = Field(default=1, description="页码", ge=1)
    size: int = Field(default=10, description="每页大小", ge=1, le=100)
    sort_by: str = Field(default="created_at", description="排序字段")
    order: str = Field(default="desc", regex="^(asc|desc)$", description="排序方向")


async def advanced_search(
    request: HttpRequest,
    search: t.Annotated[SearchParams, p.Query()],
    pagination: t.Annotated[PaginationParams, p.Query()],
    include_inactive: t.Annotated[bool, p.Query(default=False)]  # 单独的查询参数
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

# 请求示例: GET /advanced-search?keyword=python&category=tech&page=2&size=5&sort_by=title&order=asc&include_inactive=true
```

#### 自动推断查询参数

```python
async def simple_query_endpoint(
    request: HttpRequest,
    name: str,          # 基础类型自动识别为查询参数
    age: int,           # 基础类型自动识别为查询参数
    email: str,         # 基础类型自动识别为查询参数
) -> JsonResponse:
    return JsonResponse({
        "name": name,
        "age": age,
        "email": email
    })

# 请求示例: GET /simple?name=张三&age=25&email=zhangsan@example.com
```

#### 查询参数特性

- **可选参数**: 支持默认值，未提供时使用默认值
- **类型转换**: 自动转换字符串为指定类型（int、bool、float 等）
- **列表支持**: 支持多值参数（如 `?tags=python&tags=web`）
- **验证**: 支持 Pydantic 的所有验证规则

#### 高级查询参数示例

```python
from typing import List, Optional
from enum import Enum

class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class FilterParams(BaseModel):
    status: Optional[StatusEnum] = Field(default=None, description="状态过滤")
    tags: List[str] = Field(default=[], description="标签列表")
    min_price: Optional[float] = Field(default=None, ge=0, description="最低价格")
    max_price: Optional[float] = Field(default=None, ge=0, description="最高价格")
    created_after: Optional[str] = Field(default=None, description="创建时间过滤")

async def filter_products(
    request: HttpRequest,
    filters: t.Annotated[FilterParams, p.Query()]
) -> JsonResponse:
    return JsonResponse({
        "filters": filters.model_dump(exclude_none=True),
        "message": "查询成功"
    })

# 请求示例: GET /products?status=active&tags=electronics&tags=mobile&min_price=100&max_price=1000
```


### Header 参数

Header 参数从 HTTP 请求头中提取，常用于认证、内容协商和客户端信息传递。

#### 基础用法

```python
# 常见的请求头参数
async def authenticated_endpoint(
    request: HttpRequest,
    authorization: t.Annotated[str, p.Header(description="认证令牌")],
    user_agent: t.Annotated[str, p.Header(alias="User-Agent", description="用户代理")],
    content_type: t.Annotated[str, p.Header(
        alias="Content-Type", 
        default="application/json",
        description="内容类型"
    )],
    x_request_id: t.Annotated[str, p.Header(
        alias="X-Request-ID",
        default=None,
        description="请求追踪ID"
    )]
) -> JsonResponse:
    return JsonResponse({
        "authorization": authorization,
        "user_agent": user_agent,
        "content_type": content_type,
        "request_id": x_request_id
    })

# 请求示例:
# GET /api/data
# Authorization: Bearer your-token-here
# User-Agent: Mozilla/5.0...
# Content-Type: application/json
# X-Request-ID: 12345-67890
```

#### 使用 BaseModel 组织请求头

```python
class AuthHeaders(BaseModel):
    authorization: str = Field(description="认证令牌", min_length=1)
    x_api_key: str = Field(alias="X-API-Key", description="API密钥")


class ClientHeaders(BaseModel):
    user_agent: str = Field(alias="User-Agent", description="用户代理")
    accept_language: str = Field(
        alias="Accept-Language", 
        default="zh-CN",
        description="接受语言"
    )
    x_forwarded_for: str = Field(
        alias="X-Forwarded-For",
        default=None,
        description="客户端IP"
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

#### Header 参数特性

- **别名支持**: 使用 `alias` 处理 HTTP Header 的命名约定（如 `Content-Type`）
- **大小写不敏感**: HTTP 头名称不区分大小写
- **可选参数**: 支持默认值
- **验证**: 支持 Pydantic 验证规则


### Cookie 参数

Cookie 参数从 HTTP Cookie 中提取，常用于会话管理、用户偏好设置等。

#### 基础用法

```python
# 基础 Cookie 参数
async def user_dashboard(
    request: HttpRequest,
    session_id: t.Annotated[str, p.Cookie(description="会话ID")],
    user_preferences: t.Annotated[str, p.Cookie(
        default="default", 
        description="用户偏好设置"
    )],
    theme: t.Annotated[str, p.Cookie(default="light", description="主题设置")],
    language: t.Annotated[str, p.Cookie(default="zh-CN", description="语言设置")]
) -> JsonResponse:
    return JsonResponse({
        "session_id": session_id,
        "preferences": user_preferences,
        "theme": theme,
        "language": language
    })

# Cookie 设置示例:
# Cookie: session_id=abc123; user_preferences=compact; theme=dark; language=en-US
```

#### 使用 BaseModel 组织 Cookie

```python
class SessionCookies(BaseModel):
    session_id: str = Field(description="会话标识")
    csrf_token: str = Field(description="CSRF令牌", min_length=10)


class UserCookies(BaseModel):
    user_id: int = Field(description="用户ID", gt=0)
    remember_me: bool = Field(default=False, description="记住登录")
    last_visit: str = Field(default=None, description="最后访问时间")


async def authenticated_page(
    request: HttpRequest,
    session: t.Annotated[SessionCookies, p.Cookie()],
    user: t.Annotated[UserCookies, p.Cookie()],
    analytics_id: t.Annotated[str, p.Cookie(default=None, description="分析跟踪ID")]
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

#### Cookie 参数特性

- **自动解析**: 自动解析 Cookie 字符串
- **类型转换**: 支持基础类型的自动转换
- **可选参数**: 支持默认值
- **安全考虑**: 建议对敏感 Cookie 进行验证


### Json 参数

Json 参数从 HTTP 请求体中提取 JSON 数据，是 API 最常用的数据传输方式。

#### 基础用法

```python
# 简单的 JSON 请求体
class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50, description="用户名")
    email: str = Field(regex=r'^[^@]+@[^@]+\.[^@]+$', description="邮箱地址")
    age: int = Field(ge=0, le=150, description="年龄")
    is_active: bool = Field(default=True, description="是否激活")

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
    # 模拟创建用户
    new_user = UserResponse(
        id=12345,
        name=user_data.name,
        email=user_data.email,
        age=user_data.age,
        is_active=user_data.is_active,
        created_at="2024-01-15T10:30:00Z"
    )
    return JsonResponse(new_user)

# 请求示例:
# POST /users
# Content-Type: application/json
# {
#   "name": "张三",
#   "email": "zhangsan@example.com", 
#   "age": 25,
#   "is_active": true
# }
```

#### 自动推断 JSON 参数

```python
class ProductData(BaseModel):
    title: str = Field(description="产品标题")
    price: float = Field(gt=0, description="价格")
    description: str = Field(default="", description="产品描述")

async def create_product(
    request: HttpRequest,
    product: ProductData  # BaseModel 类型自动识别为 Json 参数
) -> JsonResponse:
    return JsonResponse({
        "message": "产品创建成功",
        "product": product.model_dump()
    })
```

#### 复杂 JSON 结构

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
    color: str = Field(regex=r'^#[0-9A-Fa-f]{6}$', description="颜色代码")

class TaskAttachment(BaseModel):
    filename: str
    url: str
    size: int = Field(ge=0, description="文件大小（字节）")

class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="任务标题")
    description: Optional[str] = Field(default=None, description="任务描述")
    priority: Priority = Field(default=Priority.MEDIUM, description="优先级")
    tags: List[TaskTag] = Field(default=[], description="标签列表")
    attachments: List[TaskAttachment] = Field(default=[], description="附件列表")
    metadata: Dict[str, Union[str, int, bool]] = Field(default={}, description="元数据")
    due_date: Optional[datetime] = Field(default=None, description="截止日期")

async def create_task(
    request: HttpRequest,
    task_data: t.Annotated[CreateTaskRequest, p.Json()]
) -> JsonResponse:
    return JsonResponse({
        "message": "任务创建成功",
        "task_id": "TASK-001",
        "title": task_data.title,
        "priority": task_data.priority,
        "tags_count": len(task_data.tags),
        "attachments_count": len(task_data.attachments)
    })

# 请求示例:
# POST /tasks
# {
#   "title": "完成项目文档",
#   "description": "编写项目的技术文档",
#   "priority": "high",
#   "tags": [
#     {"name": "文档", "color": "#ff0000"},
#     {"name": "重要", "color": "#00ff00"}
#   ],
#   "metadata": {
#     "project_id": "PROJ-001",
#     "estimate_hours": 8
#   },
#   "due_date": "2024-01-20T18:00:00Z"
# }
```

#### 组合多个 JSON 参数

```python
class AuthInfo(BaseModel):
    api_key: str = Field(description="API密钥")
    signature: str = Field(description="请求签名")

class RequestData(BaseModel):
    action: str = Field(description="操作类型")
    data: Dict[str, t.Any] = Field(description="操作数据")

async def secure_operation(
    request: HttpRequest,
    auth: t.Annotated[AuthInfo, p.Json()],
    request_data: t.Annotated[RequestData, p.Json()],
    timestamp: t.Annotated[int, p.Json(description="时间戳")]
) -> JsonResponse:
    # 验证认证信息和执行操作
    return JsonResponse({
        "status": "success",
        "action": request_data.action,
        "timestamp": timestamp
    })

# 请求示例:
# POST /secure-api
# {
#   "api_key": "your-api-key",
#   "signature": "request-signature",
#   "action": "update_profile",
#   "data": {"name": "新名称"},
#   "timestamp": 1705320600
# }
```

#### JSON 参数特性

- **自动验证**: 基于 Pydantic 模型进行数据验证
- **类型转换**: 自动进行类型转换和格式化
- **嵌套支持**: 支持复杂的嵌套数据结构
- **错误提示**: 提供详细的验证错误信息
- **文档生成**: 自动生成 JSON Schema 文档


### Form 参数

Form 参数从 HTTP 表单数据中提取，支持 `application/x-www-form-urlencoded` 格式。

#### 基础用法

```python
# 简单表单数据
class LoginForm(BaseModel):
    username: str = Field(min_length=1, description="用户名")
    password: str = Field(min_length=6, description="密码")
    remember_me: bool = Field(default=False, description="记住登录")

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: str = None

async def login(
    request: HttpRequest,
    form_data: t.Annotated[LoginForm, p.Form()]
) -> JsonResponse[LoginResponse]:
    # 验证登录信息（示例）
    if form_data.username == "admin" and form_data.password == "password":
        return JsonResponse(LoginResponse(
            success=True,
            message="登录成功",
            token="your-auth-token"
        ))
    else:
        return JsonResponse(LoginResponse(
            success=False,
            message="用户名或密码错误"
        ), status_code=401)

# 请求示例:
# POST /login
# Content-Type: application/x-www-form-urlencoded
# username=admin&password=password&remember_me=true
```

#### 复杂表单处理

```python
class UserProfileForm(BaseModel):
    full_name: str = Field(min_length=1, max_length=100, description="完整姓名")
    email: str = Field(regex=r'^[^@]+@[^@]+\.[^@]+$', description="邮箱")
    phone: str = Field(regex=r'^\+?1?\d{9,15}$', description="电话号码")
    bio: str = Field(default="", max_length=500, description="个人简介")
    age: int = Field(ge=0, le=150, description="年龄")
    newsletter: bool = Field(default=False, description="订阅新闻")

class AddressForm(BaseModel):
    street: str = Field(description="街道地址")
    city: str = Field(description="城市")
    state: str = Field(description="州/省")
    zip_code: str = Field(description="邮政编码")
    country: str = Field(default="CN", description="国家代码")

async def update_profile(
    request: HttpRequest,
    profile: t.Annotated[UserProfileForm, p.Form()],
    address: t.Annotated[AddressForm, p.Form()],
    timezone: t.Annotated[str, p.Form(default="Asia/Shanghai", description="时区")]
) -> JsonResponse:
    return JsonResponse({
        "message": "个人资料更新成功",
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

# 请求示例:
# POST /profile
# Content-Type: application/x-www-form-urlencoded
# full_name=张三&email=zhangsan@example.com&phone=13800138000&bio=软件工程师&age=30&newsletter=true&street=科技大道1号&city=深圳&state=广东&zip_code=518000&country=CN&timezone=Asia/Shanghai
```

### File 参数

File 参数用于处理文件上传，支持 `multipart/form-data` 格式。

#### 基础文件上传

```python
from unfazed.file import UploadFile

class FileUploadResponse(BaseModel):
    filename: str
    size: int
    content_type: str
    message: str

async def upload_avatar(
    request: HttpRequest,
    avatar: t.Annotated[UploadFile, p.File(description="用户头像")]
) -> JsonResponse[FileUploadResponse]:
    # 验证文件类型
    if not avatar.content_type.startswith('image/'):
        return JsonResponse(
            {"error": "只支持图片文件"},
            status_code=400
        )
    
    # 验证文件大小（例如：最大 5MB）
    content = await avatar.read()
    if len(content) > 5 * 1024 * 1024:
        return JsonResponse(
            {"error": "文件大小不能超过 5MB"},
            status_code=400
        )
    
    # 保存文件逻辑（示例）
    # save_file(avatar.filename, content)
    
    return JsonResponse(FileUploadResponse(
        filename=avatar.filename,
        size=len(content),
        content_type=avatar.content_type,
        message="头像上传成功"
    ))

# 请求示例:
# POST /upload-avatar
# Content-Type: multipart/form-data
# avatar: [binary file data]
```

#### 多文件上传

```python
from typing import List

class MultiFileUploadResponse(BaseModel):
    uploaded_files: List[dict]
    total_count: int
    total_size: int

async def upload_documents(
    request: HttpRequest,
    documents: t.Annotated[List[UploadFile], p.File(description="文档列表")],
    category: t.Annotated[str, p.Form(description="文档分类")]
) -> JsonResponse[MultiFileUploadResponse]:
    uploaded_files = []
    total_size = 0
    
    for doc in documents:
        # 验证文件类型
        allowed_types = ['application/pdf', 'application/msword', 'text/plain']
        if doc.content_type not in allowed_types:
            continue
            
        content = await doc.read()
        file_size = len(content)
        total_size += file_size
        
        # 保存文件逻辑
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

# 请求示例:
# POST /upload-documents
# Content-Type: multipart/form-data
# documents: [file1.pdf, file2.docx, file3.txt]
# category: reports
```

#### 文件与表单数据组合

```python
class DocumentForm(BaseModel):
    title: str = Field(description="文档标题")
    description: str = Field(default="", description="文档描述")
    is_public: bool = Field(default=False, description="是否公开")
    tags: str = Field(default="", description="标签（逗号分隔）")

async def create_document(
    request: HttpRequest,
    document_file: t.Annotated[UploadFile, p.File(description="文档文件")],
    form_data: t.Annotated[DocumentForm, p.Form()],
    author_id: t.Annotated[int, p.Form(description="作者ID")]
) -> JsonResponse:
    # 处理文件
    content = await document_file.read()
    
    # 解析标签
    tags = [tag.strip() for tag in form_data.tags.split(',') if tag.strip()]
    
    return JsonResponse({
        "message": "文档创建成功",
        "document": {
            "title": form_data.title,
            "filename": document_file.filename,
            "size": len(content),
            "author_id": author_id,
            "tags": tags,
            "is_public": form_data.is_public
        }
    })

# 请求示例:
# POST /documents
# Content-Type: multipart/form-data
# document_file: [binary file]
# title: 项目报告
# description: 2024年第一季度项目总结
# is_public: true
# tags: 报告,季度,项目
# author_id: 123
```

#### 文件参数特性

- **类型支持**: 继承自 Starlette 的 UploadFile，支持所有文件操作
- **异步操作**: 支持异步文件读取和处理
- **内容类型**: 自动检测文件的 MIME 类型
- **大小限制**: 可以设置文件大小限制
- **多文件**: 支持单个端点接收多个文件
- **组合使用**: 可以与表单数据一起使用

#### UploadFile 方法

```python
async def handle_file(file: UploadFile):
    # 文件属性
    filename = file.filename          # 原始文件名
    content_type = file.content_type  # MIME 类型
    
    # 文件操作
    content = await file.read()       # 读取全部内容
    await file.seek(0)               # 重置文件指针
    chunk = await file.read(1024)    # 读取指定字节数
    await file.close()               # 关闭文件
```

## 高级用法

### 响应模型定义

Unfazed 支持定义响应模型，用于生成 API 文档和类型提示：

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
    p.ResponseSpec(model=SuccessResponse, code="200", description="成功响应"),
    p.ResponseSpec(model=ErrorResponse, code="404", description="用户不存在"),
    p.ResponseSpec(model=ErrorResponse, code="500", description="服务器错误")
]:
    try:
        # 业务逻辑
        user_data = {"id": user_id, "name": "张三"}
        return JsonResponse(SuccessResponse(
            message="获取用户信息成功",
            data=user_data
        ))
    except UserNotFound:
        return JsonResponse(ErrorResponse(
            error="用户不存在",
            error_code=404
        ), status_code=404)
```

### 参数依赖和验证

#### 自定义验证器

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
            raise ValueError('邮箱格式不正确')
        return v.lower()
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('两次密码输入不一致')
        return v

async def register_user(
    request: HttpRequest,
    user_data: t.Annotated[CreateUserRequest, p.Json()]
) -> JsonResponse:
    # 用户数据已经通过验证
    return JsonResponse({"message": "用户注册成功"})
```

#### 条件参数

```python
from typing import Union

class BaseSearchParams(BaseModel):
    query: str = Field(min_length=1, description="搜索关键词")
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
        # 用户搜索逻辑
        return JsonResponse({"type": "user_search", "results": []})
    else:
        # 产品搜索逻辑
        return JsonResponse({"type": "product_search", "results": []})
```

