Unfazed HttpRequest
===================

`HttpRequest` 在 Starlette 的 `Request` 类基础上扩展了一些 Unfazed 特有的功能：通过 `orjson` 进行快速 JSON 解析，以及访问 session、已认证用户和应用实例的便捷属性。关于从 path、query、headers、cookies 和 body 中提取参数，请参阅 [Endpoint](endpoint.md) 文档。

## 快速开始

```python
from unfazed.http import HttpRequest, JsonResponse


async def my_endpoint(request: HttpRequest) -> JsonResponse:
    # 请求元数据
    method = request.method          # "GET", "POST" 等
    path = request.path              # "/api/users"
    scheme = request.scheme          # "http" 或 "https"

    # Headers、query 参数、cookies
    auth = request.headers.get("authorization", "")
    page = request.query_params.get("page", "1")
    token = request.cookies.get("csrf_token", "")

    # JSON 请求体（使用 orjson 解析，首次调用时缓存）
    body = await request.json()

    return JsonResponse({"method": method, "path": path})
```

## 自定义 Request 子类

你可以继承 `HttpRequest` 来补充项目自己的辅助属性或方法，然后在 endpoint 中直接标注这个子类：

```python
from unfazed.http import HttpRequest, JsonResponse


class CustomRequest(HttpRequest):
    @property
    def trace_id(self) -> str:
        return self.headers.get("x-trace-id", "")


async def my_endpoint(request: CustomRequest) -> JsonResponse:
    return JsonResponse({"trace_id": request.trace_id})
```

这个自定义 request 参数必须位于 endpoint 签名的第一个位置，并且只能出现一次。

## 可用属性

### 继承自 Starlette

`HttpRequest` 继承自 `starlette.requests.Request` 的所有属性：

| 属性 / 方法 | 类型 | 说明 |
|-------------|------|------|
| `method` | `str` | HTTP 方法（`GET`、`POST` 等）。 |
| `url` | `URL` | 完整 URL 对象，包含 `.scheme`、`.hostname`、`.port`、`.path`、`.query`。 |
| `headers` | `Headers` | 大小写不敏感的 header 映射。 |
| `query_params` | `QueryParams` | 解析后的 query 字符串参数。 |
| `path_params` | `dict` | 由路由器提取的 URL 路径参数。 |
| `cookies` | `dict` | 请求 cookies。 |
| `client` | `Address \| None` | 客户端的 `(host, port)`。 |
| `state` | `State` | 每次请求的状态（由 lifespan 的 `state` 属性填充）。 |
| `await body()` | `bytes` | 原始请求体。 |
| `await form()` | `FormData` | 解析后的表单数据。 |
| `await stream()` | `AsyncGenerator` | 分块流式读取请求体。 |

### Unfazed 特有

| 属性 / 方法 | 类型 | 说明 |
|-------------|------|------|
| `scheme` | `str` | `url.scheme` 的简写。 |
| `path` | `str` | `url.path` 的简写。 |
| `await json()` | `dict` | 使用 `orjson` 将请求体解析为 JSON。首次调用后缓存。 |
| `session` | `SessionBase` | session 对象。需要 `SessionMiddleware`。若未安装则抛出 `ValueError`。 |
| `user` | `AbstractUser \| BaseModel \| None` | 当前请求用户。通常由 middleware 写入 `scope["user"]`。未安装相关 middleware 时访问会抛出 `ValueError`。 |
| `unfazed` | `Unfazed` | 应用实例。 |

## API 参考

### HttpRequest

```python
class HttpRequest(starlette.requests.Request)
```

Unfazed 框架的增强型 HTTP 请求类。

**方法：**

- `async json() -> Dict`: 使用 `orjson` 将请求体解析为 JSON。结果会被缓存 — 后续调用返回同一 dict，不会重新解析。

**属性：**

- `scheme -> str`: URL 协议（`"http"` 或 `"https"`）。
- `path -> str`: URL 路径（如 `"/api/users"`）。
- `session -> SessionBase`: session 对象。若未安装 `SessionMiddleware` 则抛出 `ValueError`。
- `user -> Optional[AbstractUser | BaseModel]`: 当前请求用户。通常由 `AuthenticationMiddleware` 或自定义 middleware 注入；匿名请求时可为 `None`。若没有 middleware 写入 `scope["user"]`，则抛出 `ValueError`。
- `unfazed -> Unfazed`: 从 ASGI scope 中获取的 Unfazed 应用实例。
