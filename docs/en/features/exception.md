Unfazed Exceptions
==================

Unfazed provides a structured exception hierarchy rooted in `BaseUnfazedException`. Each exception carries a human-readable `message` and a numeric `code`, making it easy to translate framework errors into appropriate HTTP responses. Built-in exceptions cover HTTP errors, authentication failures, routing issues, and setup problems.

## Quick Start

Raise any built-in exception from an endpoint or middleware:

```python
from unfazed.http import HttpRequest, JsonResponse
from unfazed.exception import PermissionDenied


async def admin_only(request: HttpRequest) -> JsonResponse:
    if not request.user.is_superuser:
        raise PermissionDenied("Admin access required")
    return JsonResponse({"status": "ok"})
```

The exception carries both a `message` (`"Admin access required"`) and a `code` (`403`), which you can use in an error-handling middleware to build a structured error response.

## Exception Hierarchy

All framework exceptions inherit from `BaseUnfazedException`:

```
BaseUnfazedException(message, code=-1)
├── UnfazedSetupError          — framework initialization failures
├── MethodNotAllowed            — HTTP 405
├── ParameterError              — request parameter validation failures
├── PermissionDenied            — HTTP 403
├── LoginRequired               — HTTP 401
├── AccountNotFound             — HTTP 404
├── WrongPassword               — HTTP 405
└── AccountExisted              — HTTP 406

TypeHintRequired(Exception)     — missing type annotations on endpoints
```

### HTTP Exceptions

| Exception | Default message | Default code | When raised |
|-----------|----------------|--------------|-------------|
| `MethodNotAllowed` | `"Method not allowed"` | `405` | A request uses an unsupported HTTP method. |

### Auth Exceptions

| Exception | Default message | Default code | When raised |
|-----------|----------------|--------------|-------------|
| `PermissionDenied` | `"Permission Denied"` | `403` | The user lacks required permissions. |
| `LoginRequired` | `"Login Required"` | `401` | The request requires authentication. |
| `AccountNotFound` | `"Account Not Found"` | `404` | A user account lookup fails. |
| `WrongPassword` | `"Wrong password"` | `405` | Password verification fails. |
| `AccountExisted` | `"Account existed"` | `406` | Registration with a duplicate account. |

### Route Exceptions

| Exception | Default message | Default code | When raised |
|-----------|----------------|--------------|-------------|
| `ParameterError` | `"Request Parameter Error"` | `401` | Request parameters fail Pydantic validation. |

### Setup Exceptions

| Exception | Default message | Default code | When raised |
|-----------|----------------|--------------|-------------|
| `UnfazedSetupError` | (caller-defined) | `-1` | The framework fails to initialize. |

### Other Exceptions

| Exception | Parent | When raised |
|-----------|--------|-------------|
| `TypeHintRequired` | `Exception` | An endpoint parameter or return type is missing a type annotation. |

## Custom Exceptions

Subclass `BaseUnfazedException` to create application-specific errors:

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

Then raise them in your endpoints:

```python
from myapp.exceptions import ResourceNotFound


async def get_article(request: HttpRequest, article_id: int) -> JsonResponse:
    article = await Article.filter(id=article_id).first()
    if not article:
        raise ResourceNotFound(f"Article {article_id} not found")
    return JsonResponse({"id": article.id, "title": article.title})
```

You can catch `BaseUnfazedException` in a middleware to build a consistent error response format across your application:

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

## API Reference

### BaseUnfazedException

```python
class BaseUnfazedException(Exception):
    def __init__(self, message: str, code: int = -1)
```

Base class for all Unfazed framework exceptions.

**Attributes:**

- `message: str` — Human-readable error description.
- `code: int` — Numeric error code (typically an HTTP status code).

### UnfazedSetupError

```python
class UnfazedSetupError(BaseUnfazedException)
```

Raised when the framework fails to initialize.

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

Raised when an endpoint parameter or return type is missing a type annotation. This is a plain `Exception`, not a `BaseUnfazedException`.
