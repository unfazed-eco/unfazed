Unfazed 测试框架
===============

Unfazed 提供了强大的测试框架，基于 HTTPX 构建的 `Requestfactory` 测试客户端，让您能够轻松地对 Unfazed 应用进行全面的集成测试。该测试客户端支持完整的 ASGI 协议，包括生命周期管理、状态共享和各种 HTTP 方法。

## 系统概述

### 核心特性

- **ASGI 兼容**: 完全支持 ASGI 3.0 协议，包括 HTTP 和生命周期事件
- **生命周期管理**: 自动处理应用的启动和关闭事件
- **状态共享**: 支持请求间的状态共享，模拟真实应用环境
- **HTTPX 集成**: 基于 HTTPX 构建，提供丰富的 HTTP 客户端功能
- **异步支持**: 完整的异步操作支持
- **测试隔离**: 每个测试实例都有独立的应用状态

### 核心组件

- **Requestfactory**: 测试客户端类，扩展自 `httpx.AsyncClient`
- **ASGITransport**: 自定义 ASGI 传输层，支持状态管理
- **生命周期管理**: 自动处理 startup/shutdown 事件

## 快速开始

### 基本使用

```python
# test_basic.py
import pytest
from unfazed.core import Unfazed
from unfazed.test import Requestfactory
from unfazed.http import HttpRequest, JsonResponse

# 定义测试函数
async def hello_world(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"message": "Hello, World!"})

async def get_user(request: HttpRequest) -> JsonResponse:
    user_id = request.path_params.get("user_id")
    return JsonResponse({"user_id": user_id, "name": f"User {user_id}"})

# 基本测试
async def test_basic_request():
    """测试基本的 GET 请求"""
    # 创建应用实例
    unfazed = Unfazed()
    
    # 添加路由
    from unfazed.route import path
    unfazed.routes = [
        path("/", endpoint=hello_world),
        path("/users/{user_id:int}", endpoint=get_user),
    ]
    
    # 设置应用
    await unfazed.setup()
    
    # 创建测试客户端
    async with Requestfactory(unfazed) as client:
        # 测试根路径
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello, World!"}
        
        # 测试带参数的路径
        response = await client.get("/users/123")
        assert response.status_code == 200
        assert response.json() == {"user_id": "123", "name": "User 123"}
```

### HTTP 方法测试

```python
# test_http_methods.py
from unfazed.test import Requestfactory
from unfazed.http import HttpRequest, JsonResponse, PlainTextResponse

# 定义不同 HTTP 方法的端点
async def create_user(request: HttpRequest) -> JsonResponse:
    user_data = await request.json()
    return JsonResponse({"id": 1, **user_data}, status_code=201)

async def update_user(request: HttpRequest) -> JsonResponse:
    user_id = request.path_params.get("user_id")
    user_data = await request.json()
    return JsonResponse({"id": user_id, **user_data})

async def delete_user(request: HttpRequest) -> PlainTextResponse:
    return PlainTextResponse("User deleted", status_code=204)

async def test_http_methods():
    """测试各种 HTTP 方法"""
    unfazed = Unfazed()
    unfazed.routes = [
        path("/users", endpoint=create_user, methods=["POST"]),
        path("/users/{user_id:int}", endpoint=update_user, methods=["PUT"]),
        path("/users/{user_id:int}", endpoint=delete_user, methods=["DELETE"]),
    ]
    await unfazed.setup()
    
    async with Requestfactory(unfazed) as client:
        # 测试 POST 请求
        user_data = {"name": "Alice", "email": "alice@example.com"}
        response = await client.post("/users", json=user_data)
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == "Alice"
        assert result["email"] == "alice@example.com"
        
        # 测试 PUT 请求
        updated_data = {"name": "Alice Smith", "email": "alice.smith@example.com"}
        response = await client.put("/users/1", json=updated_data)
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "Alice Smith"
        
        # 测试 DELETE 请求
        response = await client.delete("/users/1")
        assert response.status_code == 204
        assert response.text == "User deleted"
```

## Lifespan 测试

`Requestfactory` 支持完整的应用 Lifespan 测试，包括启动和关闭事件。

### 基本 Lifespan 测试

```python
# test_lifespan.py
from unfazed.lifespan import BaseLifeSpan
from unfazed.test import Requestfactory

class DatabaseSetup(BaseLifeSpan):
    """模拟数据库设置生命周期组件"""
    
    async def on_startup(self):
        # 模拟数据库连接初始化
        self.state["db_connected"] = True
        self.state["user_count"] = 0
        print("数据库连接已建立")
    
    async def on_shutdown(self):
        # 模拟数据库连接清理
        self.state["db_connected"] = False
        print("数据库连接已关闭")

async def get_status(request: HttpRequest) -> JsonResponse:
    """返回数据库连接状态"""
    db_connected = request.app.state.get("db_connected", False)
    user_count = request.app.state.get("user_count", 0)
    return JsonResponse({
        "db_connected": db_connected,
        "user_count": user_count
    })

async def test_lifespan_events():
    """测试生命周期事件"""
    from unfazed.conf import UnfazedSettings
    
    unfazed = Unfazed(
        settings=UnfazedSettings(
            LIFESPAN=["test_lifespan.DatabaseSetup"]
        )
    )
    unfazed.routes = [path("/status", endpoint=get_status)]
    await unfazed.setup()
    
    # 使用 async with 自动管理生命周期
    async with Requestfactory(unfazed) as client:
        response = await client.get("/status")
        assert response.status_code == 200
        result = response.json()
        assert result["db_connected"] is True
        assert result["user_count"] == 0
    
    # 退出 async with 后，shutdown 事件已被调用

async def test_manual_lifespan():
    """手动控制生命周期测试"""
    unfazed = Unfazed()
    unfazed.routes = [path("/status", endpoint=get_status)]
    await unfazed.setup()
    
    # 禁用自动生命周期管理
    client = Requestfactory(unfazed, lifespan_on=False)
    
    # 手动启动
    await client.lifespan_startup()
    
    response = await client.get("/status")
    assert response.status_code == 200
    
    # 手动关闭
    await client.lifespan_shutdown()
```

## 测试配置

### Pytest

```python
# conftest.py
import pytest
from unfazed.core import Unfazed
from unfazed.test import Requestfactory
from unfazed.conf import UnfazedSettings

@pytest.fixture
async def app():
    """创建测试应用实例"""
    unfazed = Unfazed(
        settings=UnfazedSettings(
            DEBUG=True,
            DATABASE=None,  # 测试时不使用数据库
        )
    )
    
    # 添加测试路由
    from myapp.routes import patterns
    unfazed.routes = patterns
    
    await unfazed.setup()
    return unfazed

@pytest.fixture
async def client(app):
    """创建测试客户端"""
    async with Requestfactory(app) as client:
        yield client

# 在测试文件中使用夹具
async def test_with_fixtures(client):
    """使用夹具进行测试"""
    response = await client.get("/")
    assert response.status_code == 200
```

### 参数化测试

```python
# test_parametrized.py
import pytest

@pytest.mark.parametrize("method,path,expected_status", [
    ("GET", "/", 200),
    ("GET", "/users", 200),
    ("POST", "/users", 201),
    ("GET", "/non-existent", 404),
])
async def test_endpoints(client, method, path, expected_status):
    """参数化测试多个端点"""
    response = await getattr(client, method.lower())(path)
    assert response.status_code == expected_status

@pytest.mark.parametrize("user_data,expected_status", [
    ({"name": "Alice", "email": "alice@example.com"}, 201),
    ({"name": "Bob"}, 400),  # 缺少邮箱
    ({}, 400),  # 缺少必需字段
])
async def test_user_creation(client, user_data, expected_status):
    """参数化测试用户创建"""
    response = await client.post("/users", json=user_data)
    assert response.status_code == expected_status
```

通过 Unfazed 的测试框架，您可以轻松地对应用进行全面的测试，确保代码质量和应用稳定性。该测试框架提供了从简单的单元测试到复杂的集成测试的完整解决方案，支持生命周期管理等各种测试场景。

