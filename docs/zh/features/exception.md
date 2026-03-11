Unfazed 异常
============

Unfazed 提供以 `BaseUnfazedException` 为根的结构化异常层次。每个异常携带人类可读的 `message` 和数字 `code`，便于将框架错误转换为合适的 HTTP 响应。内置异常涵盖 HTTP 错误、认证失败、路由问题和配置问题。

## 快速开始

在 endpoint 或 middleware 中抛出任意内置异常：

```python
from unfazed.http import HttpRequest, JsonResponse
from unfazed.exception import PermissionDenied


async def admin_only(request: HttpRequest) -> JsonResponse:
    if not request.user.is_superuser:
        raise PermissionDenied("Admin access required")
    return JsonResponse({"status": "ok"})
```

异常同时携带 `message`（`"Admin access required"`）和 `code`（`403`），可在错误处理 middleware 中用于构建结构化错误响应。

## 异常层次

所有框架异常继承自 `BaseUnfazedException`：

```
BaseUnfazedException(message, code=-1)
├── UnfazedSetupError          — 框架初始化失败
├── MethodNotAllowed            — HTTP 405
├── ParameterError              — 请求参数验证失败
├── PermissionDenied            — HTTP 403
├── LoginRequired               — HTTP 401
├── AccountNotFound             — HTTP 404
├── WrongPassword               — HTTP 405
└── AccountExisted              — HTTP 406

TypeHintRequired(Exception)     — endpoint 缺少类型注解
```

### HTTP 异常

| 异常 | 默认消息 | 默认 code | 何时抛出 |
|-----------|----------------|--------------|-------------|
| `MethodNotAllowed` | `"Method not allowed"` | `405` | 请求使用了不支持的 HTTP 方法。 |

### 认证异常

| 异常 | 默认消息 | 默认 code | 何时抛出 |
|-----------|----------------|--------------|-------------|
| `PermissionDenied` | `"Permission Denied"` | `403` | 用户缺少所需权限。 |
| `LoginRequired` | `"Login Required"` | `401` | 请求需要认证。 |
| `AccountNotFound` | `"Account Not Found"` | `404` | 用户账户查找失败。 |
| `WrongPassword` | `"Wrong password"` | `405` | 密码验证失败。 |
| `AccountExisted` | `"Account existed"` | `406` | 使用重复账户注册。 |

### 路由异常

| 异常 | 默认消息 | 默认 code | 何时抛出 |
|-----------|----------------|--------------|-------------|
| `ParameterError` | `"Request Parameter Error"` | `401` | 请求参数 Pydantic 验证失败。 |

### 配置异常

| 异常 | 默认消息 | 默认 code | 何时抛出 |
|-----------|----------------|--------------|-------------|
| `UnfazedSetupError` | （调用方定义） | `-1` | 框架初始化失败。 |

### 其他异常

| 异常 | 父类 | 何时抛出 |
|-----------|--------|-------------|
| `TypeHintRequired` | `Exception` | endpoint 参数或返回类型缺少类型注解。 |

## 自定义异常

继承 `BaseUnfazedException` 创建应用特定错误：

```python
# myapp/exceptions.py
from unfazed.exception import BaseUnfazedException


class ResourceNotFound(BaseUnfazedException):
    def __init__(self, message: str = "Resource not found", code: int = 404):
        super().__init__(message, code)


class RateLimitExceeded(BaseUnfazedException):
    def __init__(self, message: str = "Rate limit exceeded", code: int = 429):
        super().__init__(message, code)
```

然后在 endpoint 中抛出：

```python
from myapp.exceptions import ResourceNotFound


async def get_article(request: HttpRequest, article_id: int) -> JsonResponse:
    article = await Article.filter(id=article_id).first()
    if not article:
        raise ResourceNotFound(f"Article {article_id} not found")
    return JsonResponse({"id": article.id, "title": article.title})
```

可在 middleware 中捕获 `BaseUnfazedException`，为应用构建一致的错误响应格式：

```python
from unfazed.exception import BaseUnfazedException
from unfazed.http import JsonResponse


class ErrorHandlingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except BaseUnfazedException as exc:
            response = JsonResponse(
                {"error": exc.message, "code": exc.code},
                status_code=exc.code,
            )
            await response(scope, receive, send)
```

## API 参考

### BaseUnfazedException

```python
class BaseUnfazedException(Exception):
    def __init__(self, message: str, code: int = -1)
```

所有 Unfazed 框架异常的基类。

**属性：**

- `message: str` — 人类可读的错误描述。
- `code: int` — 数字错误码（通常为 HTTP 状态码）。

### UnfazedSetupError

```python
class UnfazedSetupError(BaseUnfazedException)
```

框架初始化失败时抛出。

### MethodNotAllowed

```python
class MethodNotAllowed(BaseUnfazedException):
    def __init__(self, message: str = "Method not allowed", code: int = 405)
```

### ParameterError

```python
class ParameterError(BaseUnfazedException):
    def __init__(self, message: str = "Request Parameter Error", code: int = 401)
```

### PermissionDenied

```python
class PermissionDenied(BaseUnfazedException):
    def __init__(self, message: str = "Permission Denied", code: int = 403)
```

### LoginRequired

```python
class LoginRequired(BaseUnfazedException):
    def __init__(self, message: str = "Login Required", code: int = 401)
```

### AccountNotFound

```python
class AccountNotFound(BaseUnfazedException):
    def __init__(self, message: str = "Account Not Found", code: int = 404)
```

### WrongPassword

```python
class WrongPassword(BaseUnfazedException):
    def __init__(self, message: str = "Wrong password", code: int = 405)
```

### AccountExisted

```python
class AccountExisted(BaseUnfazedException):
    def __init__(self, message: str = "Account existed", code: int = 406)
```

### TypeHintRequired

```python
class TypeHintRequired(Exception)
```

当 endpoint 参数或返回类型缺少类型注解时抛出。这是普通的 `Exception`，不是 `BaseUnfazedException`。
