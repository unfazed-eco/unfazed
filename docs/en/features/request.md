Unfazed HttpRequest
===================

`HttpRequest` extends Starlette's `Request` class with a few Unfazed-specific additions: fast JSON parsing via `orjson`, and convenient properties for accessing the session, authenticated user, and the application instance. For parameter extraction from path, query, headers, cookies, and body, see the [Endpoint](endpoint.md) documentation.

## Quick Start

```python
from unfazed.http import HttpRequest, JsonResponse


async def my_endpoint(request: HttpRequest) -> JsonResponse:
    # Request metadata
    method = request.method          # "GET", "POST", etc.
    path = request.path              # "/api/users"
    scheme = request.scheme          # "http" or "https"

    # Headers, query params, cookies
    auth = request.headers.get("authorization", "")
    page = request.query_params.get("page", "1")
    token = request.cookies.get("csrf_token", "")

    # JSON body (parsed with orjson, cached on first call)
    body = await request.json()

    return JsonResponse({"method": method, "path": path})
```

## Custom Request Subclasses

You can extend `HttpRequest` to add project-specific helpers, then type your endpoint with that subclass:

```python
from unfazed.http import HttpRequest, JsonResponse


class CustomRequest(HttpRequest):
    @property
    def trace_id(self) -> str:
        return self.headers.get("x-trace-id", "")


async def my_endpoint(request: CustomRequest) -> JsonResponse:
    return JsonResponse({"trace_id": request.trace_id})
```

The custom request parameter must be the first parameter in the endpoint signature, and it can only appear once.

## Available Properties

### Inherited from Starlette

`HttpRequest` inherits all properties from `starlette.requests.Request`:

| Property / Method | Type | Description |
|-------------------|------|-------------|
| `method` | `str` | HTTP method (`GET`, `POST`, etc.). |
| `url` | `URL` | Full URL object with `.scheme`, `.hostname`, `.port`, `.path`, `.query`. |
| `headers` | `Headers` | Case-insensitive header mapping. |
| `query_params` | `QueryParams` | Parsed query string parameters. |
| `path_params` | `dict` | URL path parameters extracted by the router. |
| `cookies` | `dict` | Request cookies. |
| `client` | `Address \| None` | Client's `(host, port)`. |
| `state` | `State` | Per-request state (populated by lifespan `state` property). |
| `await body()` | `bytes` | Raw request body. |
| `await form()` | `FormData` | Parsed form data. |
| `await stream()` | `AsyncGenerator` | Stream the request body in chunks. |

### Unfazed-specific

| Property / Method | Type | Description |
|-------------------|------|-------------|
| `scheme` | `str` | Shortcut for `url.scheme`. |
| `path` | `str` | Shortcut for `url.path`. |
| `await json()` | `dict` | Parse body as JSON using `orjson`. Cached after first call. |
| `session` | `SessionBase` | The session object. Requires `SessionMiddleware`. Raises `ValueError` if not installed. |
| `user` | `AbstractUser \| BaseModel \| None` | The current request user. Usually populated by middleware via `scope["user"]`. Raises `ValueError` when no relevant middleware has populated it. |
| `unfazed` | `Unfazed` | The application instance. |

## API Reference

### HttpRequest

```python
class HttpRequest(starlette.requests.Request)
```

Enhanced HTTP request class for the Unfazed framework.

**Methods:**

- `async json() -> Dict`: Parse the request body as JSON using `orjson`. The result is cached — subsequent calls return the same dict without re-parsing.

**Properties:**

- `scheme -> str`: URL scheme (`"http"` or `"https"`).
- `path -> str`: URL path (e.g. `"/api/users"`).
- `session -> SessionBase`: Session object. Raises `ValueError` if `SessionMiddleware` is not installed.
- `user -> Optional[AbstractUser | BaseModel]`: Current request user. Usually injected by `AuthenticationMiddleware` or custom middleware; may be `None` for anonymous requests. Raises `ValueError` when `scope["user"]` has not been populated.
- `unfazed -> Unfazed`: The Unfazed application instance from the ASGI scope.
