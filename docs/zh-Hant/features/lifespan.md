Unfazed 生命周期管理
=====

Unfazed 的生命周期管理系统基于 ASGI Lifespan 协议，提供了应用程序启动和停止时的钩子机制。通过生命周期管理，您可以优雅地处理资源初始化、清理工作以及状态共享等任务。

## 系统概述

### 核心组件

- **BaseLifeSpan**: 生命周期组件的基类，定义了标准接口
- **LifeSpanHandler**: 生命周期处理器，管理所有注册的生命周期组件
- **State**: 应用状态容器，用于在不同组件间共享数据

### 生命周期事件

1. **启动事件 (on_startup)**: 应用启动时执行，用于资源初始化
2. **停止事件 (on_shutdown)**: 应用停止时执行，用于资源清理

### 工作流程

```
应用启动 → 执行所有 on_startup → 应用运行 → 应用停止 → 执行所有 on_shutdown → 应用退出
```

## 快速开始

### 1. 创建生命周期组件

```python
from unfazed.lifespan import BaseLifeSpan
import typing as t

class DatabaseLifeSpan(BaseLifeSpan):
    """数据库连接生命周期管理"""
    
    def __init__(self, unfazed) -> None:
        super().__init__(unfazed)
        self.db_connection = None
    
    async def on_startup(self) -> None:
        """应用启动时初始化数据库连接"""
        print("正在初始化数据库连接...")
        # 模拟数据库连接初始化
        self.db_connection = await self.create_database_connection()
        print("数据库连接初始化完成")
    
    async def on_shutdown(self) -> None:
        """应用停止时关闭数据库连接"""
        print("正在关闭数据库连接...")
        if self.db_connection:
            await self.db_connection.close()
        print("数据库连接已关闭")
    
    async def create_database_connection(self):
        """创建数据库连接（示例）"""
        # 实际的数据库连接逻辑
        return {"connection": "database_connection_object"}
    
    @property
    def state(self) -> t.Dict[str, t.Any]:
        """返回要共享的状态"""
        return {
            "db_connection": self.db_connection,
            "db_status": "connected" if self.db_connection else "disconnected"
        }
```

### 2. 注册生命周期组件

在配置文件中注册生命周期组件：

```python
# settings.py
UNFAZED_SETTINGS = {
    "LIFESPAN": [
        "yourapp.lifespan.DatabaseLifeSpan",
        "yourapp.lifespan.RedisLifeSpan",
        "yourapp.lifespan.LoggingLifeSpan",
    ]
}
```

### 3. 启动应用

```shell
uvicorn asgi:application --host 0.0.0.0 --port 9527
```

**输出示例：**
```
正在初始化数据库连接...
数据库连接初始化完成
正在初始化 Redis 连接...
Redis 连接初始化完成
应用启动完成
```



## 状态共享机制

### 访问共享状态

生命周期组件可以通过 `state` 属性向整个应用暴露共享数据，这些数据可以在请求处理过程中访问：

```python
from unfazed.http import HttpRequest, JsonResponse

async def get_database_status(request: HttpRequest) -> JsonResponse:
    """获取数据库连接状态"""
    
    # 访问生命周期组件共享的状态
    db_connection = request.state.db_connection
    db_status = request.state.db_status
    
    return JsonResponse({
        "database_connected": db_status == "connected",
        "connection_info": str(db_connection) if db_connection else None
    })

async def query_users(request: HttpRequest) -> JsonResponse:
    """查询用户列表"""
    
    # 使用共享的数据库连接
    db_connection = request.state.db_connection
    
    if not db_connection:
        return JsonResponse({"error": "数据库连接不可用"}, status_code=500)
    
    # 使用数据库连接执行查询
    # users = await db_connection.fetch_all("SELECT * FROM users")
    
    return JsonResponse({
        "users": [],  # 实际的用户数据
        "message": "查询成功"
    })
```

## 实际应用场景

### 外部服务连接

```python
import httpx
from unfazed.lifespan import BaseLifeSpan

class ExternalServiceLifeSpan(BaseLifeSpan):
    """外部服务连接管理"""
    
    def __init__(self, unfazed) -> None:
        super().__init__(unfazed)
        self.http_client = None
        self.service_health = {}
    
    async def on_startup(self) -> None:
        """初始化 HTTP 客户端和检查外部服务"""
        # 创建 HTTP 客户端
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=50, max_connections=100)
        )
        
        # 检查外部服务健康状态
        await self.check_external_services()
        print("外部服务连接已初始化")
    
    async def on_shutdown(self) -> None:
        """关闭 HTTP 客户端"""
        if self.http_client:
            await self.http_client.aclose()
            print("外部服务连接已关闭")
    
    async def check_external_services(self):
        """检查外部服务健康状态"""
        services = {
            "payment_api": "https://api.payment.com/health",
            "notification_api": "https://api.notification.com/health"
        }
        
        for service_name, health_url in services.items():
            try:
                response = await self.http_client.get(health_url)
                self.service_health[service_name] = response.status_code == 200
            except Exception:
                self.service_health[service_name] = False
    
    @property
    def state(self) -> dict:
        return {
            "http_client": self.http_client,
            "service_health": self.service_health
        }
```
