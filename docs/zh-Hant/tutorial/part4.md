# 第四部分：API 接口设计与 Schema 定义

在上一节中，我们成功设计了数据模型和序列化器。现在我们将创建完整的 API 接口，学习如何使用 Unfazed 的参数注解系统、定义请求/响应模型，并生成自动化的 API 文档。

我们将为学生选课系统创建三个核心接口，展示 Unfazed 现代化的 API 开发方式。

## API 接口设计

### 接口规划

根据学生选课的业务逻辑，我们需要设计以下接口：

| 接口路径               | HTTP方法 | 功能描述     | 参数类型           |
| ---------------------- | -------- | ------------ | ------------------ |
| `/enroll/student-list` | GET      | 获取学生列表 | Query 参数（分页） |
| `/enroll/course-list`  | GET      | 获取课程列表 | Query 参数（分页） |
| `/enroll/bind`         | POST     | 学生选课绑定 | JSON 请求体        |

### API 设计原则

不同的 team 有不同的设计规范，以 unfazed 作者所在的 team 为例，我们不使用 restful 风格，遵循以下实践

- ✅ **HTTP Method**：仅使用 GET/POST 两种方法
- ✅ **URL**：/api/v1{version}/enroll{app-label}/student-list{resource-action}
- ✅ **状态码**：HTTP 状态码都为 200，在响应体中返回 code 字段，code 为 0 表示成功，其他值表示失败
- ✅ **响应体**：响应体结构统一，包含 message、data、code 字段


## Schema 定义

Schema 是 API 的数据契约，定义了请求和响应的数据结构。

### 创建基础 Schema

编辑 `enroll/schema.py` 文件：

```python
# src/backend/enroll/schema.py

import typing as t
from pydantic import BaseModel, Field
from .serializers import StudentSerializer, CourseSerializer

class BaseResponse[T](BaseModel):
    """统一响应基类"""
    code: int = Field(0, description="响应码")
    message: str = Field("", description="响应消息")
    data: T = Field(description="响应数据")

class PaginationMeta(BaseModel):
    """分页元数据"""
    page: int = Field(description="当前页码")
    size: int = Field(description="每页数量")
    total: int = Field(description="总记录数")
    total_pages: int = Field(description="总页数")

class StudentListResponse(BaseResponse[t.List[StudentSerializer]]):
    """学生列表响应"""
    pass


class CourseListResponse(BaseResponse[t.List[CourseSerializer]]):
    """课程列表响应"""
    pass


class BindRequest(BaseModel):
    """选课绑定请求"""
    student_id: int = Field(description="学生ID", gt=0)
    course_id: int = Field(description="课程ID", gt=0)

class BindResponse(BaseResponse[t.Dict]):
    """选课绑定响应"""
    pass

class StudentDetailResponse(BaseResponse[StudentSerializer]):
    """学生详情响应"""
    pass

class CourseDetailResponse(BaseResponse[CourseSerializer]):
    """课程详情响应"""
    pass
```

## Endpoint 实现

### 理解 Unfazed 参数注解

Unfazed 使用 Python 的 `Annotated` 类型注解来声明 API 参数：

```python
import typing as t
from unfazed.route import params as p

# Query 参数（URL 查询字符串）
page: t.Annotated[int, p.Query(default=1)] 

# Path 参数（URL 路径变量）
user_id: t.Annotated[int, p.Path()]

# JSON 请求体
data: t.Annotated[UserCreateRequest, p.Json()]

# 表单数据
form: t.Annotated[UserForm, p.Form()]

# 文件上传
file: t.Annotated[UploadFile, p.File()]

# 响应规范
-> t.Annotated[JsonResponse, p.ResponseSpec(model=UserResponse)]
```

### 实现视图函数

编辑 `enroll/endpoints.py` 文件：

```python
# src/backend/enroll/endpoints.py

import typing as t
import time
from unfazed.http import HttpRequest, JsonResponse, PlainTextResponse
from unfazed.route import params as p
from . import schema as s

# 保留之前的 hello 函数
async def hello(request: HttpRequest) -> PlainTextResponse:
    """Hello World 接口"""
    return PlainTextResponse("Hello, World!")

async def list_student(
    request: HttpRequest,
    page: t.Annotated[int, p.Query(default=1, description="页码", ge=1)],
    size: t.Annotated[int, p.Query(default=10, description="每页数量", ge=1, le=100)],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.StudentListResponse)]:
    """
    获取学生列表
    
    - **page**: 页码，从 1 开始
    - **size**: 每页数量，范围 1-100
    """
    # 这里暂时返回空数据，下一节会实现具体逻辑
    return JsonResponse({
        "message": "获取学生列表成功",
        "data": [],
        "code": 0,
    })

async def list_course(
    request: HttpRequest,
    page: t.Annotated[int, p.Query(default=1, description="页码", ge=1)],
    size: t.Annotated[int, p.Query(default=10, description="每页数量", ge=1, le=100)],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.CourseListResponse)]:
    """
    获取课程列表
    
    - **page**: 页码，从 1 开始  
    - **size**: 每页数量，范围 1-100
    """
    return JsonResponse({
        "message": "获取课程列表成功",
        "data": [],
        "code": 0,
    })

async def bind(
    request: HttpRequest,
    ctx: t.Annotated[s.BindRequest, p.Json()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.BindResponse)]:
    """
    学生选课绑定
    
    - **student_id**: 学生ID
    - **course_id**: 课程ID
    """
    return JsonResponse({
        "message": f"学生 {ctx.student_id} 成功选择课程 {ctx.course_id}",
        "data": {
            "student_id": ctx.student_id,
            "course_id": ctx.course_id
        },
        "code": 0,
    })

async def get_student(
    request: HttpRequest,
    student_id: t.Annotated[int, p.Path(description="学生ID")],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.StudentDetailResponse)]:
    """
    获取学生详情
    
    - **student_id**: 学生ID
    """
    # 暂时返回模拟数据
    return JsonResponse({
        "code": 0,
        "message": "获取学生详情成功",
        "data": {
            "id": student_id,
            "name": "示例学生",
            "email": "student@example.com",
            "age": 20,
            "student_id": "2024001"
        }
    })
```

### 参数验证特性

Unfazed 提供了强大的参数验证能力：

**1. 类型验证**：
```python
page: t.Annotated[int, p.Query()]  # 自动转换为整数
```

**2. 范围约束**：
```python
size: t.Annotated[int, p.Query(ge=1, le=100)]  # 值范围 1-100
```

**3. 默认值**：
```python
page: t.Annotated[int, p.Query(default=1)]  # 默认值为 1
```

**4. 必需参数**：
```python
user_id: t.Annotated[int, p.Path()]  # 路径参数必需
```

## 路由配置

### 更新路由定义

编辑 `enroll/routes.py` 文件：

```python
# src/backend/enroll/routes.py

import typing as t
from unfazed.route import Route, path
from .endpoints import hello, list_student, list_course, bind, get_student

patterns: t.List[Route] = [
    # Hello World 接口
    path("/hello", endpoint=hello, methods=["GET"], name="hello"),
    
    # 学生相关接口
    path("/student-list", endpoint=list_student, methods=["GET"], name="list_students"),

    # 课程相关接口  
    path("/course-list", endpoint=list_course, methods=["GET"], name="list_courses"),
    
    # 选课绑定接口
    path("/bind", endpoint=bind, methods=["POST"], name="bind_course"),
]
```

## 自动 API 文档

### OpenAPI 文档生成

Unfazed 基于你的代码自动生成 OpenAPI 3.0 文档，无需额外配置！

启动项目后，访问以下地址：

**Swagger UI（交互式文档）**：
```
http://127.0.0.1:9527/openapi/docs
```

**ReDoc（美观的文档）**：
```
http://127.0.0.1:9527/openapi/redoc
```

### 文档特性

Unfazed 生成的 API 文档包含：

1. **完整的接口信息**：
   - HTTP 方法和路径
   - 请求/响应参数
   - 数据类型和验证规则

2. **交互式测试**：
   - 在 Swagger UI 中直接测试 API
   - 查看实际的请求/响应数据

3. **代码示例**：
   - 自动生成多种语言的调用示例
   - curl、Python、JavaScript 等

4. **数据模型**：
   - 完整的 Schema 定义
   - 字段描述和约束信息

### 增强文档质量

**添加接口标签**：
```python
# 为接口分组
path("/students", endpoint=list_student, tags=["学生管理"])
path("/courses", endpoint=list_course, tags=["课程管理"])
```

**完善接口描述**：
```python
async def list_student(request: HttpRequest, ...):
    """
    获取学生列表
    
    获取系统中所有学生的分页列表，支持按页码和每页数量进行查询。
    
    **使用说明**：
    - 页码从 1 开始计算
    - 每页最多返回 100 条记录
    - 返回结果包含完整的分页元数据
    
    **返回数据包含**：
    - 学生基本信息（姓名、邮箱、年龄等）
    - 分页信息（当前页、总数、总页数等）
    """
    pass
```

## 测试 API 接口

### 使用 curl 测试

```bash
# 测试学生列表接口
curl "http://127.0.0.1:9527/enroll/students?page=1&size=5"

# 测试学生详情接口
curl "http://127.0.0.1:9527/enroll/students/1"

# 测试课程列表接口
curl "http://127.0.0.1:9527/enroll/courses"

# 测试选课绑定接口
curl -X POST "http://127.0.0.1:9527/enroll/bind" \
     -H "Content-Type: application/json" \
     -d '{"student_id": 1, "course_id": 1}'
```

### 使用 Python requests 测试

```python
import requests
import json

base_url = "http://127.0.0.1:9527/enroll"

# 测试学生列表
response = requests.get(f"{base_url}/students", params={"page": 1, "size": 10})
print("学生列表:", response.json())

# 测试选课绑定
bind_data = {"student_id": 1, "course_id": 1}
response = requests.post(
    f"{base_url}/bind", 
    json=bind_data,
    headers={"Content-Type": "application/json"}
)
print("绑定结果:", response.json())
```

### 自定义错误响应

```python
from unfazed.exception import ValidationError

async def bind(request: HttpRequest, ctx: s.BindRequest) -> JsonResponse:
    """选课绑定（带验证）"""
    
    # 自定义业务验证
    if ctx.student_id == ctx.course_id:
        raise ValidationError("学生ID和课程ID不能相同")
    
    # 正常处理逻辑
    return JsonResponse({
        "success": True,
        "message": "绑定成功",
        "data": {"student_id": ctx.student_id, "course_id": ctx.course_id}
    })
```

## 下一步

太棒了！你已经成功设计了完整的 API 接口和数据模型。在下一个教程中，我们将：

- 实现业务逻辑服务（Services）
- 连接数据库进行实际的 CRUD 操作
- 学习序列化器的高级用法
- 处理复杂的业务场景

让我们继续前往 **第五部分：业务逻辑实现**！

---
