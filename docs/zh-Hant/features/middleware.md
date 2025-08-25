Unfazed 中间件系统
======

Unfazed 的中间件系统基于 ASGI 标准设计，提供了灵活且强大的请求/响应处理能力。系统继承了 Starlette 的中间件调用机制，支持全局中间件和路由级中间件，为开发者提供了完整的请求生命周期控制。

## 系统概述

### 核心组件

- **BaseMiddleware**: 中间件基类，定义了标准的 ASGI 中间件接口
- **内置中间件**: CommonMiddleware、CORSMiddleware、GZipMiddleware、TrustedHostMiddleware
- **中间件栈**: 支持多层中间件的组合和嵌套调用
- **配置系统**: 统一的配置管理，支持全局和路由级配置

### 中间件类型

1. **全局中间件**: 应用于所有请求，在 `MIDDLEWARE` 配置中定义
2. **路由中间件**: 应用于特定路由，在路由定义时指定
3. **内置中间件**: 框架提供的常用功能中间件
4. **自定义中间件**: 用户根据业务需求编写的中间件

### 执行流程

```
请求 → 全局中间件 1 → 全局中间件 2 → 路由中间件 → 视图函数处理 → 路由中间件 → 全局中间件 2 → 全局中间件 1 → 响应
```

## 快速开始

### 1. 创建自定义中间件

```python
from unfazed.middleware import BaseMiddleware
from unfazed.type import Scope, Receive, Send
import time
import logging

logger = logging.getLogger("myapp.middleware")

class TimingMiddleware(BaseMiddleware):
    """请求计时中间件"""
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        async def send_wrapper(message):
            """响应包装器，用于添加计时信息"""
            if message["type"] == "http.response.start":
                # 添加自定义响应头
                duration = time.time() - start_time
                headers = list(message.get("headers", []))
                headers.append((b"x-process-time", f"{duration:.4f}".encode()))
                message["headers"] = headers
                
                # 记录请求日志
                method = scope.get("method", "Unknown")
                path = scope.get("path", "Unknown")
                logger.info(f"{method} {path} - 处理时间: {duration:.4f}s")
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
```

### 2. 配置全局中间件

```python
# settings.py
UNFAZED_SETTINGS = {
    "MIDDLEWARE": [
        "myapp.middleware.TimingMiddleware",                           # 自定义计时中间件
        "unfazed.middleware.internal.common.CommonMiddleware",        # 错误处理
        "unfazed.middleware.internal.cors.CORSMiddleware",           # 跨域处理
        "unfazed.middleware.internal.gzip.GZipMiddleware",           # Gzip 压缩
        "unfazed.middleware.internal.trustedhost.TrustedHostMiddleware", # 主机验证
    ],
    
    # 中间件相关配置
    "CORS": {
        "ALLOW_ORIGINS": ["https://example.com", "https://app.example.com"],
        "ALLOW_METHODS": ["GET", "POST", "PUT", "DELETE"],
        "ALLOW_HEADERS": ["*"],
        "ALLOW_CREDENTIALS": True,
    },
    
    "GZIP": {
        "MINIMUM_SIZE": 1024,      # 最小压缩大小 1KB
        "COMPRESS_LEVEL": 6,       # 压缩级别 1-9
    },
    
    "TRUSTED_HOST": {
        "ALLOWED_HOSTS": ["example.com", "*.example.com"],
        "WWW_REDIRECT": True,
    }
}
```

### 3. 配置路由中间件

```python
# routes.py
from unfazed.route import path
from myapp.endpoints import api_view, admin_view
from myapp.middleware import AuthMiddleware, RateLimitMiddleware

patterns = [
    # 公开 API，只使用全局中间件
    path("/public/status", endpoint=status_view),
    
    # 需要认证的 API
    path("/api/users", endpoint=api_view, 
         middleware=["myapp.middleware.AuthMiddleware"]),
    
    # 管理员 API，需要认证和速率限制
    path("/admin/dashboard", endpoint=admin_view, 
         middleware=[
             "myapp.middleware.AuthMiddleware",
             "myapp.middleware.RateLimitMiddleware"
         ]),
]
```

### 4. 启动应用

```bash
uvicorn asgi:application --host 0.0.0.0 --port 9527
```

**请求示例:**
```bash
curl -i http://localhost:9527/api/users
```

**响应示例:**
```
HTTP/1.1 200 OK
content-type: application/json
x-process-time: 0.0023
content-length: 45

{"users": [], "total": 0}
```

## 中间件开发详解

### BaseMiddleware 详解

```python
from unfazed.middleware import BaseMiddleware
from unfazed.type import ASGIApp, Scope, Receive, Send

class BaseMiddleware(ABC):
    """中间件基类"""
    
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
    
    @abstractmethod
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI 应用接口"""
        pass
```

### 实际应用场景

#### 1. 认证中间件

```python
from unfazed.middleware import BaseMiddleware
from unfazed.http import JsonResponse
from unfazed.conf import settings
import jwt

class AuthMiddleware(BaseMiddleware):
    """JWT 认证中间件"""
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # 检查请求路径是否需要认证
        path = scope.get("path", "")
        if not self._requires_auth(path):
            await self.app(scope, receive, send)
            return
        
        # 获取 Authorization 头
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode()
        
        if not auth_header.startswith("Bearer "):
            await self._send_unauthorized(scope, receive, send)
            return
        
        try:
            # 验证 JWT token
            token = auth_header[7:]  # 移除 "Bearer " 前缀
            payload = jwt.decode(
                token, 
                settings["JWT_SECRET"], 
                algorithms=["HS256"]
            )
            
            # 将用户信息添加到 scope
            scope["user"] = {
                "id": payload["user_id"],
                "username": payload["username"],
                "roles": payload.get("roles", [])
            }
            
            await self.app(scope, receive, send)
            
        except jwt.ExpiredSignatureError:
            await self._send_error(scope, receive, send, "Token已过期", 401)
        except jwt.InvalidTokenError:
            await self._send_error(scope, receive, send, "无效的Token", 401)
    
    def _requires_auth(self, path: str) -> bool:
        """检查路径是否需要认证"""
        public_paths = ["/public/", "/health", "/docs"]
        return not any(path.startswith(p) for p in public_paths)
    
    async def _send_unauthorized(self, scope, receive, send):
        """发送未授权响应"""
        response = JsonResponse(
            {"error": "未提供认证凭据"}, 
            status_code=401
        )
        await response(scope, receive, send)
    
    async def _send_error(self, scope, receive, send, message: str, status_code: int):
        """发送错误响应"""
        response = JsonResponse(
            {"error": message}, 
            status_code=status_code
        )
        await response(scope, receive, send)
```

#### 2. 速率限制中间件

```python
import asyncio
import time
from collections import defaultdict
from unfazed.middleware import BaseMiddleware
from unfazed.http import JsonResponse

class RateLimitMiddleware(BaseMiddleware):
    """速率限制中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)  # {client_ip: [timestamp, ...]}
        self.max_requests = 100            # 每分钟最大请求数
        self.window_size = 60              # 时间窗口（秒）
        self.cleanup_interval = 300        # 清理间隔（秒）
        self.last_cleanup = time.time()
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # 获取客户端 IP
        client_ip = self._get_client_ip(scope)
        current_time = time.time()
        
        # 定期清理过期记录
        if current_time - self.last_cleanup > self.cleanup_interval:
            await self._cleanup_expired_records(current_time)
            self.last_cleanup = current_time
        
        # 检查速率限制
        if await self._is_rate_limited(client_ip, current_time):
            await self._send_rate_limit_error(scope, receive, send)
            return
        
        # 记录请求
        self.requests[client_ip].append(current_time)
        
        await self.app(scope, receive, send)
    
    def _get_client_ip(self, scope: Scope) -> str:
        """获取客户端 IP 地址"""
        # 首先检查 X-Forwarded-For 头
        headers = dict(scope.get("headers", []))
        forwarded_for = headers.get(b"x-forwarded-for")
        
        if forwarded_for:
            return forwarded_for.decode().split(",")[0].strip()
        
        # 其次检查 X-Real-IP 头
        real_ip = headers.get(b"x-real-ip")
        if real_ip:
            return real_ip.decode()
        
        # 最后使用直接连接的 IP
        client = scope.get("client")
        return client[0] if client else "unknown"
    
    async def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """检查是否超过速率限制"""
        requests = self.requests[client_ip]
        
        # 移除超出时间窗口的请求
        cutoff_time = current_time - self.window_size
        self.requests[client_ip] = [t for t in requests if t > cutoff_time]
        
        # 检查当前请求数量
        return len(self.requests[client_ip]) >= self.max_requests
    
    async def _cleanup_expired_records(self, current_time: float):
        """清理过期的请求记录"""
        cutoff_time = current_time - self.window_size
        
        for client_ip in list(self.requests.keys()):
            self.requests[client_ip] = [
                t for t in self.requests[client_ip] if t > cutoff_time
            ]
            
            # 移除空记录
            if not self.requests[client_ip]:
                del self.requests[client_ip]
    
    async def _send_rate_limit_error(self, scope, receive, send):
        """发送速率限制错误响应"""
        response = JsonResponse(
            {
                "error": "请求过于频繁，请稍后再试",
                "retry_after": self.window_size
            },
            status_code=429,
            headers={"Retry-After": str(self.window_size)}
        )
        await response(scope, receive, send)
```

#### 3. 请求日志中间件

```python
import json
import time
import logging
from unfazed.middleware import BaseMiddleware

logger = logging.getLogger("access")

class AccessLogMiddleware(BaseMiddleware):
    """访问日志中间件"""
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # 记录请求开始时间
        start_time = time.time()
        request_info = self._extract_request_info(scope)
        
        # 包装 send 函数以捕获响应信息
        response_info = {"status_code": None, "content_length": 0}
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                response_info["status_code"] = message["status"]
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                response_info["content_length"] += len(body)
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # 记录访问日志
            duration = time.time() - start_time
            self._log_access(request_info, response_info, duration)
    
    def _extract_request_info(self, scope: Scope) -> dict:
        """提取请求信息"""
        headers = dict(scope.get("headers", []))
        
        return {
            "method": scope.get("method", ""),
            "path": scope.get("path", ""),
            "query_string": scope.get("query_string", b"").decode(),
            "client_ip": self._get_client_ip(scope),
            "user_agent": headers.get(b"user-agent", b"").decode(),
            "referer": headers.get(b"referer", b"").decode(),
            "content_length": headers.get(b"content-length", b"0").decode(),
        }
    
    def _get_client_ip(self, scope: Scope) -> str:
        """获取客户端 IP"""
        headers = dict(scope.get("headers", []))
        
        # 检查代理头
        forwarded_for = headers.get(b"x-forwarded-for")
        if forwarded_for:
            return forwarded_for.decode().split(",")[0].strip()
        
        # 直接连接 IP
        client = scope.get("client")
        return client[0] if client else "unknown"
    
    def _log_access(self, request_info: dict, response_info: dict, duration: float):
        """记录访问日志"""
        log_entry = {
            "timestamp": time.time(),
            "method": request_info["method"],
            "path": request_info["path"],
            "query_string": request_info["query_string"],
            "status_code": response_info["status_code"],
            "content_length": response_info["content_length"],
            "duration": round(duration, 4),
            "client_ip": request_info["client_ip"],
            "user_agent": request_info["user_agent"],
            "referer": request_info["referer"],
        }
        
        # 以 JSON 格式记录日志
        logger.info(json.dumps(log_entry, ensure_ascii=False))
```

#### 4. 配置驱动的中间件

```python
from unfazed.middleware import BaseMiddleware
from unfazed.conf import settings

class ConfigurableMiddleware(BaseMiddleware):
    """可配置的中间件示例"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # 从配置中读取参数
        self.config = settings.get("CUSTOM_MIDDLEWARE", {})
        self.enabled = self.config.get("ENABLED", True)
        self.debug_mode = self.config.get("DEBUG_MODE", False)
        self.allowed_ips = set(self.config.get("ALLOWED_IPS", []))
        self.blocked_user_agents = set(self.config.get("BLOCKED_USER_AGENTS", []))
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        if not self.enabled:
            await self.app(scope, receive, send)
            return
        
        # IP 白名单检查
        if self.allowed_ips and not self._is_ip_allowed(scope):
            await self._send_forbidden(scope, receive, send)
            return
        
        # User-Agent 黑名单检查
        if self._is_user_agent_blocked(scope):
            await self._send_forbidden(scope, receive, send)
            return
        
        # 调试模式下添加额外信息
        if self.debug_mode:
            scope["debug_info"] = {
                "middleware": "ConfigurableMiddleware",
                "timestamp": time.time()
            }
        
        await self.app(scope, receive, send)
    
    def _is_ip_allowed(self, scope: Scope) -> bool:
        """检查 IP 是否在白名单中"""
        client_ip = self._get_client_ip(scope)
        return client_ip in self.allowed_ips
    
    def _is_user_agent_blocked(self, scope: Scope) -> bool:
        """检查 User-Agent 是否被阻止"""
        headers = dict(scope.get("headers", []))
        user_agent = headers.get(b"user-agent", b"").decode().lower()
        
        return any(blocked in user_agent for blocked in self.blocked_user_agents)
    
    def _get_client_ip(self, scope: Scope) -> str:
        """获取客户端 IP"""
        client = scope.get("client")
        return client[0] if client else "unknown"
    
    async def _send_forbidden(self, scope, receive, send):
        """发送禁止访问响应"""
        response = JsonResponse(
            {"error": "访问被拒绝"}, 
            status_code=403
        )
        await response(scope, receive, send)
```

### 配置示例

```python
# settings.py
UNFAZED_SETTINGS = {
    "MIDDLEWARE": [
        "myapp.middleware.AccessLogMiddleware",
        "myapp.middleware.ConfigurableMiddleware",
        "myapp.middleware.RateLimitMiddleware",
        "myapp.middleware.AuthMiddleware",
    ],
    
    # 自定义中间件配置
    "CUSTOM_MIDDLEWARE": {
        "ENABLED": True,
        "DEBUG_MODE": False,
        "ALLOWED_IPS": ["192.168.1.0/24", "10.0.0.0/8"],
        "BLOCKED_USER_AGENTS": ["bot", "crawler", "spider"]
    },

}
```


### CommonMiddleware

**引入方式**: `"unfazed.middleware.internal.common.CommonMiddleware"`

CommonMiddleware 是 Unfazed 的核心错误处理中间件，提供了智能的异常处理和调试支持。

#### 主要功能

- **异常捕获**: 捕获应用中未处理的异常
- **调试模式**: `DEBUG=True` 时显示详细的错误页面和堆栈跟踪
- **生产模式**: `DEBUG=False` 时返回通用的 500 错误响应
- **日志记录**: 自动记录所有异常到日志系统

#### 调试页面特性

当 `DEBUG=True` 时，CommonMiddleware 会生成一个美观的 HTML 错误页面，包含：

- 完整的异常堆栈跟踪
- 异常发生的具体位置
- 当前的 Unfazed 配置信息
- 响应式设计，支持移动端查看

#### 配置示例

```python
UNFAZED_SETTINGS = {
    "DEBUG": True,  # 开发环境设为 True，生产环境设为 False
    "MIDDLEWARE": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
}
```

#### 使用建议

- **开发环境**: 设置 `DEBUG=True` 以获得详细的错误信息
- **生产环境**: 务必设置 `DEBUG=False` 以防止敏感信息泄露
- **日志监控**: 配合日志系统监控生产环境的异常情况

### CORSMiddleware

**引入方式**: `"unfazed.middleware.internal.cors.CORSMiddleware"`

CORSMiddleware 基于 Starlette 的 CORSMiddleware 实现，用于处理跨域资源共享（CORS）请求。

#### 配置参数

```python
UNFAZED_SETTINGS = {
    "CORS": {
        "ALLOW_ORIGINS": ["https://example.com", "https://app.example.com"],
        "ALLOW_METHODS": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "ALLOW_HEADERS": ["Content-Type", "Authorization", "X-Requested-With"],
        "ALLOW_CREDENTIALS": True,
        "ALLOW_ORIGIN_REGEX": r"https://.*\.example\.com",
        "EXPOSE_HEADERS": ["X-Custom-Header"],
        "MAX_AGE": 3600,  # 预检请求缓存时间（秒）
    }
}
```

#### 参数说明

- **ALLOW_ORIGINS**: 允许的源域名列表，使用 `["*"]` 允许所有域名
- **ALLOW_METHODS**: 允许的 HTTP 方法列表
- **ALLOW_HEADERS**: 允许的请求头列表
- **ALLOW_CREDENTIALS**: 是否允许发送认证信息（cookies、authorization headers）
- **ALLOW_ORIGIN_REGEX**: 使用正则表达式匹配允许的源域名
- **EXPOSE_HEADERS**: 暴露给客户端的响应头列表
- **MAX_AGE**: 预检请求的缓存时间

#### 常见配置场景

```python
# 开发环境 - 允许所有源
"CORS": {
    "ALLOW_ORIGINS": ["*"],
    "ALLOW_METHODS": ["*"],
    "ALLOW_HEADERS": ["*"],
}

# 生产环境 - 严格控制
"CORS": {
    "ALLOW_ORIGINS": ["https://yourdomain.com"],
    "ALLOW_METHODS": ["GET", "POST", "PUT", "DELETE"],
    "ALLOW_HEADERS": ["Content-Type", "Authorization"],
    "ALLOW_CREDENTIALS": True,
}

# 多子域支持
"CORS": {
    "ALLOW_ORIGIN_REGEX": r"https://.*\.yourdomain\.com",
    "ALLOW_CREDENTIALS": True,
}
```

### GZipMiddleware

**引入方式**: `"unfazed.middleware.internal.gzip.GZipMiddleware"`

GZipMiddleware 基于 Starlette 的 GZipMiddleware 实现，提供 HTTP 响应的 Gzip 压缩功能。

#### 配置参数

```python
UNFAZED_SETTINGS = {
    "GZIP": {
        "MINIMUM_SIZE": 1024,        # 最小压缩大小（字节）
        "COMPRESS_LEVEL": 6,         # 压缩级别 1-9，9为最高压缩率
    }
}
```

#### 参数说明

- **MINIMUM_SIZE**: 只有响应体大小超过此值时才进行压缩
- **COMPRESS_LEVEL**: 压缩级别，1为最快压缩，9为最高压缩率

#### 工作原理

1. 检查客户端是否支持 gzip 压缩（Accept-Encoding 头）
2. 检查响应体大小是否超过最小压缩阈值
3. 对符合条件的响应进行 gzip 压缩
4. 添加相应的响应头（Content-Encoding: gzip）

#### 性能建议

```python
# 平衡性能和压缩率的配置
"GZIP": {
    "MINIMUM_SIZE": 500,    # 500字节以上才压缩
    "COMPRESS_LEVEL": 6,    # 平衡压缩率和速度
}

# 高压缩率配置（适合带宽受限环境）
"GZIP": {
    "MINIMUM_SIZE": 200,
    "COMPRESS_LEVEL": 9,
}

# 快速响应配置（适合高并发环境）
"GZIP": {
    "MINIMUM_SIZE": 1024,
    "COMPRESS_LEVEL": 1,
}
```

### TrustedHostMiddleware

**引入方式**: `"unfazed.middleware.internal.trustedhost.TrustedHostMiddleware"`

TrustedHostMiddleware 基于 Starlette 的 TrustedHostMiddleware 实现，用于验证请求的 Host 头，防止 Host 头注入攻击。

#### 配置参数

```python
UNFAZED_SETTINGS = {
    "TRUSTED_HOST": {
        "ALLOWED_HOSTS": ["example.com", "www.example.com", "*.example.com"],
        "WWW_REDIRECT": True,    # 是否将 www 重定向到非 www
    }
}
```

#### 参数说明

- **ALLOWED_HOSTS**: 允许的主机名列表，支持通配符 `*`
- **WWW_REDIRECT**: 是否自动将 www 子域重定向到主域名

#### 主机名模式

```python
# 精确匹配
"ALLOWED_HOSTS": ["example.com", "api.example.com"]

# 通配符匹配
"ALLOWED_HOSTS": ["*.example.com"]  # 匹配所有子域名

# 允许所有主机（仅开发环境）
"ALLOWED_HOSTS": ["*"]

# 本地开发配置
"ALLOWED_HOSTS": ["localhost", "127.0.0.1", "0.0.0.0"]
```

#### 安全建议

```python
# 生产环境严格配置
"TRUSTED_HOST": {
    "ALLOWED_HOSTS": ["yourdomain.com", "api.yourdomain.com"],
    "WWW_REDIRECT": True,
}

# 开发环境宽松配置
"TRUSTED_HOST": {
    "ALLOWED_HOSTS": ["localhost", "127.0.0.1", "*.local"],
    "WWW_REDIRECT": False,
}
```

### SessionMiddleware

**引入方式**: `"unfazed.contrib.session.middleware.SessionMiddleware"`

SessionMiddleware 来自 Unfazed 的 contrib 包，提供了灵活的会话管理功能。

#### 配置参数

```python
UNFAZED_CONTRIB_SESSION_SETTINGS = {
    "SECRET": "your-secret-key-here",
    "ENGINE": "signing",  # 或 "redis"
    "COOKIE_NAME": "sessionid",
    "COOKIE_MAX_AGE": 1209600,  # 2周
    "COOKIE_PATH": "/",
    "COOKIE_DOMAIN": None,
    "COOKIE_SECURE": False,
    "COOKIE_HTTPONLY": True,
    "COOKIE_SAMESITE": "lax",
}
```

#### 支持的引擎

1. **signing**: 基于签名的会话存储（默认）
2. **redis**: 基于 Redis 的会话存储

#### 使用示例

```python
from unfazed.http import HttpRequest, JsonResponse

async def login_view(request: HttpRequest) -> JsonResponse:
    # 设置会话数据
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    
    return JsonResponse({"message": "登录成功"})

async def profile_view(request: HttpRequest) -> JsonResponse:
    # 获取会话数据
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"error": "未登录"}, status_code=401)
    
    return JsonResponse({"user_id": user_id})

async def logout_view(request: HttpRequest) -> JsonResponse:
    # 清除会话
    request.session.flush()
    return JsonResponse({"message": "已退出登录"})
```
