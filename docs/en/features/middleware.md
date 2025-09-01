Unfazed Middleware System
========================

Unfazed's middleware system is designed based on the ASGI standard, providing flexible and powerful request/response processing capabilities. The system inherits Starlette's middleware invocation mechanism and supports both global and route-level middleware, giving developers complete control over the request lifecycle.

## System Overview

### Core Components

- **BaseMiddleware**: Middleware base class defining the standard ASGI middleware interface
- **Built-in Middleware**: CommonMiddleware, CORSMiddleware, GZipMiddleware, TrustedHostMiddleware
- **Middleware Stack**: Support for multi-layer middleware composition and nested calls
- **Configuration System**: Unified configuration management supporting global and route-level configuration

### Middleware Types

1. **Global Middleware**: Applied to all requests, defined in `MIDDLEWARE` configuration
2. **Route Middleware**: Applied to specific routes, specified when defining routes
3. **Built-in Middleware**: Common functionality middleware provided by the framework
4. **Custom Middleware**: User-written middleware based on business needs

### Execution Flow

```
Request → Global Middleware 1 → Global Middleware 2 → Route Middleware → View Function Processing → Route Middleware → Global Middleware 2 → Global Middleware 1 → Response
```

## Quick Start

### 1. Create Custom Middleware

```python
from unfazed.middleware import BaseMiddleware
from unfazed.type import Scope, Receive, Send
import time
import logging

logger = logging.getLogger("myapp.middleware")

class TimingMiddleware(BaseMiddleware):
    """Request timing middleware"""
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        async def send_wrapper(message):
            """Response wrapper for adding timing information"""
            if message["type"] == "http.response.start":
                # Add custom response header
                duration = time.time() - start_time
                headers = list(message.get("headers", []))
                headers.append((b"x-process-time", f"{duration:.4f}".encode()))
                message["headers"] = headers
                
                # Log request
                method = scope.get("method", "Unknown")
                path = scope.get("path", "Unknown")
                logger.info(f"{method} {path} - Processing time: {duration:.4f}s")
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
```

### 2. Configure Global Middleware

```python
# settings.py
UNFAZED_SETTINGS = {
    "MIDDLEWARE": [
        "myapp.middleware.TimingMiddleware",                           # Custom timing middleware
        "unfazed.middleware.internal.common.CommonMiddleware",        # Error handling
        "unfazed.middleware.internal.cors.CORSMiddleware",           # CORS handling
        "unfazed.middleware.internal.gzip.GZipMiddleware",           # Gzip compression
        "unfazed.middleware.internal.trustedhost.TrustedHostMiddleware", # Host verification
    ],
    
    # Middleware related configuration
    "CORS": {
        "ALLOW_ORIGINS": ["https://example.com", "https://app.example.com"],
        "ALLOW_METHODS": ["GET", "POST", "PUT", "DELETE"],
        "ALLOW_HEADERS": ["*"],
        "ALLOW_CREDENTIALS": True,
    },
    
    "GZIP": {
        "MINIMUM_SIZE": 1024,      # Minimum compression size 1KB
        "COMPRESS_LEVEL": 6,       # Compression level 1-9
    },
    
    "TRUSTED_HOST": {
        "ALLOWED_HOSTS": ["example.com", "*.example.com"],
        "WWW_REDIRECT": True,
    }
}
```

### 3. Configure Route Middleware

```python
# routes.py
from unfazed.route import path
from myapp.endpoints import api_view, admin_view
from myapp.middleware import AuthMiddleware, RateLimitMiddleware

patterns = [
    # Public API, only using global middleware
    path("/public/status", endpoint=status_view),
    
    # API requiring authentication
    path("/api/users", endpoint=api_view, 
         middleware=["myapp.middleware.AuthMiddleware"]),
    
    # Admin API requiring authentication and rate limiting
    path("/admin/dashboard", endpoint=admin_view, 
         middleware=[
             "myapp.middleware.AuthMiddleware",
             "myapp.middleware.RateLimitMiddleware"
         ]),
]
```

### 4. Start Application

```bash
uvicorn asgi:application --host 0.0.0.0 --port 9527
```

**Request Example:**
```bash
curl -i http://localhost:9527/api/users
```

**Response Example:**
```
HTTP/1.1 200 OK
content-type: application/json
x-process-time: 0.0023
content-length: 45

{"users": [], "total": 0}
```

## Middleware Development Details

### BaseMiddleware Details

```python
from unfazed.middleware import BaseMiddleware
from unfazed.type import ASGIApp, Scope, Receive, Send

class BaseMiddleware(ABC):
    """Middleware base class"""
    
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
    
    @abstractmethod
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI application interface"""
        pass
```

### Practical Application Scenarios

#### 1. Authentication Middleware

```python
from unfazed.middleware import BaseMiddleware
from unfazed.http import JsonResponse
from unfazed.conf import settings
import jwt

class AuthMiddleware(BaseMiddleware):
    """JWT authentication middleware"""
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if request path requires authentication
        path = scope.get("path", "")
        if not self._requires_auth(path):
            await self.app(scope, receive, send)
            return
        
        # Get Authorization header
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode()
        
        if not auth_header.startswith("Bearer "):
            await self._send_unauthorized(scope, receive, send)
            return
        
        try:
            # Verify JWT token
            token = auth_header[7:]  # Remove "Bearer " prefix
            payload = jwt.decode(
                token, 
                settings["JWT_SECRET"], 
                algorithms=["HS256"]
            )
            
            # Add user information to scope
            scope["user"] = {
                "id": payload["user_id"],
                "username": payload["username"],
                "roles": payload.get("roles", [])
            }
            
            await self.app(scope, receive, send)
            
        except jwt.ExpiredSignatureError:
            await self._send_error(scope, receive, send, "Token expired", 401)
        except jwt.InvalidTokenError:
            await self._send_error(scope, receive, send, "Invalid token", 401)
    
    def _requires_auth(self, path: str) -> bool:
        """Check if path requires authentication"""
        public_paths = ["/public/", "/health", "/docs"]
        return not any(path.startswith(p) for p in public_paths)
    
    async def _send_unauthorized(self, scope, receive, send):
        """Send unauthorized response"""
        response = JsonResponse(
            {"error": "No authentication credentials provided"}, 
            status_code=401
        )
        await response(scope, receive, send)
    
    async def _send_error(self, scope, receive, send, message: str, status_code: int):
        """Send error response"""
        response = JsonResponse(
            {"error": message}, 
            status_code=status_code
        )
        await response(scope, receive, send)
```

#### 2. Rate Limiting Middleware

```python
import asyncio
import time
from collections import defaultdict
from unfazed.middleware import BaseMiddleware
from unfazed.http import JsonResponse

class RateLimitMiddleware(BaseMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)  # {client_ip: [timestamp, ...]}
        self.max_requests = 100            # Max requests per minute
        self.window_size = 60              # Time window (seconds)
        self.cleanup_interval = 300        # Cleanup interval (seconds)
        self.last_cleanup = time.time()
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Get client IP
        client_ip = self._get_client_ip(scope)
        current_time = time.time()
        
        # Periodic cleanup of expired records
        if current_time - self.last_cleanup > self.cleanup_interval:
            await self._cleanup_expired_records(current_time)
            self.last_cleanup = current_time
        
        # Check rate limit
        if await self._is_rate_limited(client_ip, current_time):
            await self._send_rate_limit_error(scope, receive, send)
            return
        
        # Record request
        self.requests[client_ip].append(current_time)
        
        await self.app(scope, receive, send)
    
    def _get_client_ip(self, scope: Scope) -> str:
        """Get client IP address"""
        # First check X-Forwarded-For header
        headers = dict(scope.get("headers", []))
        forwarded_for = headers.get(b"x-forwarded-for")
        
        if forwarded_for:
            return forwarded_for.decode().split(",")[0].strip()
        
        # Then check X-Real-IP header
        real_ip = headers.get(b"x-real-ip")
        if real_ip:
            return real_ip.decode()
        
        # Finally use direct connection IP
        client = scope.get("client")
        return client[0] if client else "unknown"
    
    async def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if rate limit exceeded"""
        requests = self.requests[client_ip]
        
        # Remove requests outside time window
        cutoff_time = current_time - self.window_size
        self.requests[client_ip] = [t for t in requests if t > cutoff_time]
        
        # Check current request count
        return len(self.requests[client_ip]) >= self.max_requests
    
    async def _cleanup_expired_records(self, current_time: float):
        """Clean up expired request records"""
        cutoff_time = current_time - self.window_size
        
        for client_ip in list(self.requests.keys()):
            self.requests[client_ip] = [
                t for t in self.requests[client_ip] if t > cutoff_time
            ]
            
            # Remove empty records
            if not self.requests[client_ip]:
                del self.requests[client_ip]
    
    async def _send_rate_limit_error(self, scope, receive, send):
        """Send rate limit error response"""
        response = JsonResponse(
            {
                "error": "Too many requests, please try again later",
                "retry_after": self.window_size
            },
            status_code=429,
            headers={"Retry-After": str(self.window_size)}
        )
        await response(scope, receive, send)
```

#### 3. Access Logging Middleware

```python
import json
import time
import logging
from unfazed.middleware import BaseMiddleware

logger = logging.getLogger("access")

class AccessLogMiddleware(BaseMiddleware):
    """Access logging middleware"""
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Record request start time
        start_time = time.time()
        request_info = self._extract_request_info(scope)
        
        # Wrap send function to capture response information
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
            # Log access record
            duration = time.time() - start_time
            self._log_access(request_info, response_info, duration)
    
    def _extract_request_info(self, scope: Scope) -> dict:
        """Extract request information"""
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
        """Get client IP"""
        headers = dict(scope.get("headers", []))
        
        # Check proxy headers
        forwarded_for = headers.get(b"x-forwarded-for")
        if forwarded_for:
            return forwarded_for.decode().split(",")[0].strip()
        
        # Direct connection IP
        client = scope.get("client")
        return client[0] if client else "unknown"
    
    def _log_access(self, request_info: dict, response_info: dict, duration: float):
        """Log access record"""
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
        
        # Log in JSON format
        logger.info(json.dumps(log_entry, ensure_ascii=False))
```

#### 4. Configuration-Driven Middleware

```python
from unfazed.middleware import BaseMiddleware
from unfazed.conf import settings

class ConfigurableMiddleware(BaseMiddleware):
    """Configurable middleware example"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Read parameters from configuration
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
        
        # IP whitelist check
        if self.allowed_ips and not self._is_ip_allowed(scope):
            await self._send_forbidden(scope, receive, send)
            return
        
        # User-Agent blacklist check
        if self._is_user_agent_blocked(scope):
            await self._send_forbidden(scope, receive, send)
            return
        
        # Add extra information in debug mode
        if self.debug_mode:
            scope["debug_info"] = {
                "middleware": "ConfigurableMiddleware",
                "timestamp": time.time()
            }
        
        await self.app(scope, receive, send)
    
    def _is_ip_allowed(self, scope: Scope) -> bool:
        """Check if IP is in whitelist"""
        client_ip = self._get_client_ip(scope)
        return client_ip in self.allowed_ips
    
    def _is_user_agent_blocked(self, scope: Scope) -> bool:
        """Check if User-Agent is blocked"""
        headers = dict(scope.get("headers", []))
        user_agent = headers.get(b"user-agent", b"").decode().lower()
        
        return any(blocked in user_agent for blocked in self.blocked_user_agents)
    
    def _get_client_ip(self, scope: Scope) -> str:
        """Get client IP"""
        client = scope.get("client")
        return client[0] if client else "unknown"
    
    async def _send_forbidden(self, scope, receive, send):
        """Send forbidden access response"""
        response = JsonResponse(
            {"error": "Access denied"}, 
            status_code=403
        )
        await response(scope, receive, send)
```

### Configuration Example

```python
# settings.py
UNFAZED_SETTINGS = {
    "MIDDLEWARE": [
        "myapp.middleware.AccessLogMiddleware",
        "myapp.middleware.ConfigurableMiddleware",
        "myapp.middleware.RateLimitMiddleware",
        "myapp.middleware.AuthMiddleware",
    ],
    
    # Custom middleware configuration
    "CUSTOM_MIDDLEWARE": {
        "ENABLED": True,
        "DEBUG_MODE": False,
        "ALLOWED_IPS": ["192.168.1.0/24", "10.0.0.0/8"],
        "BLOCKED_USER_AGENTS": ["bot", "crawler", "spider"]
    },
}
```

## Built-in Middleware

### CommonMiddleware

**Import Path**: `"unfazed.middleware.internal.common.CommonMiddleware"`

CommonMiddleware is Unfazed's core error handling middleware, providing intelligent exception handling and debug support.

#### Main Features

- **Exception Capture**: Capture unhandled exceptions in the application
- **Debug Mode**: Display detailed error pages and stack traces when `DEBUG=True`
- **Production Mode**: Return generic 500 error responses when `DEBUG=False`
- **Logging**: Automatically log all exceptions to the logging system

#### Debug Page Features

When `DEBUG=True`, CommonMiddleware generates a beautiful HTML error page including:

- Complete exception stack trace
- Specific location where exception occurred
- Current Unfazed configuration information
- Responsive design supporting mobile viewing

#### Configuration Example

```python
UNFAZED_SETTINGS = {
    "DEBUG": True,  # Set to True in development, False in production
    "MIDDLEWARE": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
}
```

#### Usage Recommendations

- **Development Environment**: Set `DEBUG=True` for detailed error information
- **Production Environment**: Must set `DEBUG=False` to prevent sensitive information leakage
- **Log Monitoring**: Use logging system to monitor production environment exceptions

### CORSMiddleware

**Import Path**: `"unfazed.middleware.internal.cors.CORSMiddleware"`

CORSMiddleware is based on Starlette's CORSMiddleware implementation for handling Cross-Origin Resource Sharing (CORS) requests.

#### Configuration Parameters

```python
UNFAZED_SETTINGS = {
    "CORS": {
        "ALLOW_ORIGINS": ["https://example.com", "https://app.example.com"],
        "ALLOW_METHODS": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "ALLOW_HEADERS": ["Content-Type", "Authorization", "X-Requested-With"],
        "ALLOW_CREDENTIALS": True,
        "ALLOW_ORIGIN_REGEX": r"https://.*\.example\.com",
        "EXPOSE_HEADERS": ["X-Custom-Header"],
        "MAX_AGE": 3600,  # Preflight request cache time (seconds)
    }
}
```

#### Parameter Description

- **ALLOW_ORIGINS**: List of allowed origin domains, use `["*"]` to allow all domains
- **ALLOW_METHODS**: List of allowed HTTP methods
- **ALLOW_HEADERS**: List of allowed request headers
- **ALLOW_CREDENTIALS**: Whether to allow sending authentication information (cookies, authorization headers)
- **ALLOW_ORIGIN_REGEX**: Use regex to match allowed origin domains
- **EXPOSE_HEADERS**: List of response headers exposed to client
- **MAX_AGE**: Cache time for preflight requests

#### Common Configuration Scenarios

```python
# Development environment - allow all origins
"CORS": {
    "ALLOW_ORIGINS": ["*"],
    "ALLOW_METHODS": ["*"],
    "ALLOW_HEADERS": ["*"],
}

# Production environment - strict control
"CORS": {
    "ALLOW_ORIGINS": ["https://yourdomain.com"],
    "ALLOW_METHODS": ["GET", "POST", "PUT", "DELETE"],
    "ALLOW_HEADERS": ["Content-Type", "Authorization"],
    "ALLOW_CREDENTIALS": True,
}

# Multi-subdomain support
"CORS": {
    "ALLOW_ORIGIN_REGEX": r"https://.*\.yourdomain\.com",
    "ALLOW_CREDENTIALS": True,
}
```

### GZipMiddleware

**Import Path**: `"unfazed.middleware.internal.gzip.GZipMiddleware"`

GZipMiddleware is based on Starlette's GZipMiddleware implementation, providing Gzip compression functionality for HTTP responses.

#### Configuration Parameters

```python
UNFAZED_SETTINGS = {
    "GZIP": {
        "MINIMUM_SIZE": 1024,        # Minimum compression size (bytes)
        "COMPRESS_LEVEL": 6,         # Compression level 1-9, 9 is highest compression ratio
    }
}
```

#### Parameter Description

- **MINIMUM_SIZE**: Only compress when response body size exceeds this value
- **COMPRESS_LEVEL**: Compression level, 1 for fastest compression, 9 for highest compression ratio

#### Working Principle

1. Check if client supports gzip compression (Accept-Encoding header)
2. Check if response body size exceeds minimum compression threshold
3. Perform gzip compression on eligible responses
4. Add appropriate response headers (Content-Encoding: gzip)

#### Performance Recommendations

```python
# Balanced performance and compression ratio configuration
"GZIP": {
    "MINIMUM_SIZE": 500,    # Compress above 500 bytes
    "COMPRESS_LEVEL": 6,    # Balance compression ratio and speed
}

# High compression ratio configuration (for bandwidth-limited environments)
"GZIP": {
    "MINIMUM_SIZE": 200,
    "COMPRESS_LEVEL": 9,
}

# Fast response configuration (for high concurrency environments)
"GZIP": {
    "MINIMUM_SIZE": 1024,
    "COMPRESS_LEVEL": 1,
}
```

### TrustedHostMiddleware

**Import Path**: `"unfazed.middleware.internal.trustedhost.TrustedHostMiddleware"`

TrustedHostMiddleware is based on Starlette's TrustedHostMiddleware implementation for verifying request Host headers and preventing Host header injection attacks.

#### Configuration Parameters

```python
UNFAZED_SETTINGS = {
    "TRUSTED_HOST": {
        "ALLOWED_HOSTS": ["example.com", "www.example.com", "*.example.com"],
        "WWW_REDIRECT": True,    # Whether to redirect www to non-www
    }
}
```

#### Parameter Description

- **ALLOWED_HOSTS**: List of allowed hostnames, supports wildcard `*`
- **WWW_REDIRECT**: Whether to automatically redirect www subdomain to main domain

#### Hostname Patterns

```python
# Exact match
"ALLOWED_HOSTS": ["example.com", "api.example.com"]

# Wildcard match
"ALLOWED_HOSTS": ["*.example.com"]  # Match all subdomains

# Allow all hosts (development environment only)
"ALLOWED_HOSTS": ["*"]

# Local development configuration
"ALLOWED_HOSTS": ["localhost", "127.0.0.1", "0.0.0.0"]
```

#### Security Recommendations

```python
# Production environment strict configuration
"TRUSTED_HOST": {
    "ALLOWED_HOSTS": ["yourdomain.com", "api.yourdomain.com"],
    "WWW_REDIRECT": True,
}

# Development environment loose configuration
"TRUSTED_HOST": {
    "ALLOWED_HOSTS": ["localhost", "127.0.0.1", "*.local"],
    "WWW_REDIRECT": False,
}
```

### SessionMiddleware

**Import Path**: `"unfazed.contrib.session.middleware.SessionMiddleware"`

SessionMiddleware comes from Unfazed's contrib package, providing flexible session management functionality.

#### Configuration Parameters

```python
UNFAZED_CONTRIB_SESSION_SETTINGS = {
    "SECRET": "your-secret-key-here",
    "ENGINE": "signing",  # or "redis"
    "COOKIE_NAME": "sessionid",
    "COOKIE_MAX_AGE": 1209600,  # 2 weeks
    "COOKIE_PATH": "/",
    "COOKIE_DOMAIN": None,
    "COOKIE_SECURE": False,
    "COOKIE_HTTPONLY": True,
    "COOKIE_SAMESITE": "lax",
}
```

#### Supported Engines

1. **signing**: Signature-based session storage (default)
2. **redis**: Redis-based session storage

#### Usage Example

```python
from unfazed.http import HttpRequest, JsonResponse

async def login_view(request: HttpRequest) -> JsonResponse:
    # Set session data
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    
    return JsonResponse({"message": "Login successful"})

async def profile_view(request: HttpRequest) -> JsonResponse:
    # Get session data
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"error": "Not logged in"}, status_code=401)
    
    return JsonResponse({"user_id": user_id})

async def logout_view(request: HttpRequest) -> JsonResponse:
    # Clear session
    request.session.flush()
    return JsonResponse({"message": "Logged out"})
```
