Unfazed Routing
===============

Unfazed's routing system maps URL paths to endpoint functions. Routes are defined using the `path()` helper, organized into `patterns` lists, and composed with `include()` for multi-app projects. The framework also supports static file serving via `static()`, mounting external ASGI apps via `mount()`, and per-route middleware.

## Quick Start

### 1. Define routes in your app

```python
# myapp/routes.py
from unfazed.route import path
from myapp.endpoints import list_users, get_user, create_user

patterns = [
    path("/users", endpoint=list_users),
    path("/users/{user_id:int}", endpoint=get_user),
    path("/users", endpoint=create_user, methods=["POST"]),
]
```

### 2. Wire them into the root URL config

```python
# routes.py (project root)
from unfazed.route import path, include

patterns = [
    path("/api", routes=include("myapp.routes")),
]
```

### 3. Set ROOT_URLCONF in settings

```python
# settings.py
UNFAZED_SETTINGS = {
    "PROJECT_NAME": "myproject",
    "ROOT_URLCONF": "routes",
}
```

The routes module must define a `patterns` list at module level.

## Defining Routes

### Basic route

```python
from unfazed.route import path

path("/users", endpoint=list_users)
```

When no `methods` are specified, the route defaults to `GET` and `HEAD`.

### Specifying HTTP methods

```python
path("/users", endpoint=create_user, methods=["POST"])
path("/users/{user_id}", endpoint=update_user, methods=["PUT", "PATCH"])
```

`HEAD` is automatically added when `GET` is specified.

### Path parameters

Use `{name}` or `{name:type}` placeholders in the path:

```python
path("/users/{user_id:int}", endpoint=get_user)
path("/files/{path:path}", endpoint=serve_file)
```

Built-in convertors: `str` (default), `int`, `float`, `path`. You can register custom convertors:

```python
from unfazed.route import Convertor, register_url_convertor


class LangConvertor(Convertor):
    regex = r"[-_a-zA-Z]+"

    def convert(self, value: str) -> str:
        return value

    def to_string(self, value: str) -> str:
        return value


register_url_convertor("lang", LangConvertor())

# Now use it:
path("/docs/{lang:lang}", endpoint=get_docs)
```

### OpenAPI metadata

Routes accept metadata fields that appear in the generated OpenAPI spec:

```python
path(
    "/users",
    endpoint=list_users,
    tags=["users"],
    summary="List all users",
    description="Returns a paginated list of users",
    deprecated=False,
    operation_id="listUsers",
    externalDocs={"url": "https://docs.example.com/users"},
    include_in_schema=True,
)
```

Set `include_in_schema=False` to hide a route from the OpenAPI spec.

## Composing Routes

### Nesting with `routes`

Use the `routes` parameter to prefix a group of routes:

```python
user_routes = [
    path("/", endpoint=list_users),
    path("/{user_id}", endpoint=get_user),
]

patterns = [
    path("/api/users", routes=user_routes),
]
# Results in: /api/users/ and /api/users/{user_id}
```

### Including from another module with `include()`

`include()` imports a module's `patterns` list and automatically sets the `app_label`:

```python
from unfazed.route import path, include

patterns = [
    path("/api/blog", routes=include("blog.routes")),
    path("/api/auth", routes=include("unfazed.contrib.auth.routes")),
]
```

The target module must define a `patterns` list:

```python
# blog/routes.py
from unfazed.route import path
from blog.endpoints import list_posts, get_post

patterns = [
    path("/posts", endpoint=list_posts),
    path("/posts/{post_id}", endpoint=get_post),
]
```

### Per-route middleware

Apply middleware to specific routes or route groups:

```python
path(
    "/admin",
    routes=include("admin.routes"),
    middlewares=["myapp.middleware.AdminAuthMiddleware"],
)

# Or on a single route:
path(
    "/secret",
    endpoint=secret_endpoint,
    middlewares=["myapp.middleware.RateLimitMiddleware"],
)
```

Middleware is applied in reverse list order (same as the global `MIDDLEWARE` setting).

## Static Files

Serve static files from a directory:

```python
from unfazed.route import static

patterns = [
    static("/static", "/path/to/staticfiles"),
    static("/docs", "/path/to/site", html=True),
    static("/", "/path/to/dist", html=True, fallback="index.html"),
]
```

| Parameter | Description |
|-----------|-------------|
| `path` | URL prefix (e.g. `"/static"`). |
| `directory` | Absolute path to the files directory. |
| `html` | If `True`, serve `index.html` for directory requests. |
| `fallback` | Optional file served for missing route-like paths, useful for SPA history fallback. |

Static routes are excluded from the OpenAPI schema.

Notes:

- Directory indexes are served for directory requests, so `/docs/` maps to `/path/to/site/index.html`.
- `fallback` only applies to route-like paths such as `/dashboard` or `/users/profile`.
- Missing asset files such as `.js`, `.css`, or `.png` still raise `404` instead of falling back to HTML.

SPA example:

```python
patterns = [
    static("/", "/path/to/dist", html=True, fallback="index.html"),
]
```

Assuming the build output looks like this:

```text
dist/
  index.html
  404.html
  assets/
    app.js
    app.css
```

Expected behavior:

- `/` -> `dist/index.html`
- `/assets/app.js` -> `dist/assets/app.js`
- `/dashboard` -> `dist/index.html`
- `/users/profile` -> `dist/index.html`
- `/assets/missing.js` -> `404`

## Mounting External Apps

Mount any ASGI application under a path prefix:

```python
from starlette.applications import Starlette
from unfazed.route import mount

other_app = Starlette(...)

patterns = [
    mount("/legacy", app=other_app),
]
```

You can also mount a sub-group of routes:

```python
patterns = [
    mount("/v2", routes=[
        Route("/users", endpoint=list_users_v2),
    ]),
]
```

Mount routes are excluded from the OpenAPI schema.

## API Reference

### path()

```python
def path(
    path: str,
    *,
    endpoint: Callable = None,
    routes: List[Route] = None,
    methods: List[str] = None,
    name: str = None,
    app_label: str = None,
    middlewares: List[str] = None,
    include_in_schema: bool = True,
    tags: List[str] = None,
    summary: str = None,
    description: str = None,
    externalDocs: Dict = None,
    deprecated: bool = False,
    operation_id: str = None,
) -> Route | List[Route]
```

Create a `Route` (when `endpoint` is given) or a list of prefixed routes (when `routes` is given). Exactly one of `endpoint` or `routes` must be provided.

### include()

```python
def include(route_path: str) -> List[Route]
```

Import a module's `patterns` list. The module must define `patterns` at module level.

### static()

```python
def static(path: str, directory: str, *, name: str = None, app_label: str = None, html: bool = False, fallback: str | None = None) -> Static
```

Create a static file serving route.

### mount()

```python
def mount(path: str, app: ASGIApp = None, routes: List[Route] = None, *, name: str = None, app_label: str = None, middlewares: List[str] = None) -> Mount
```

Mount an ASGI app or route group under a path prefix.

### Route

```python
class Route(starlette.routing.Route):
    def __init__(self, path, endpoint, *, methods=None, name=None, middlewares=None, app_label=None, tags=None, include_in_schema=True, summary=None, description=None, externalDocs=None, deprecated=None, operation_id=None, response_models=None)
```

A single URL-to-endpoint mapping. Paths must start with `/`.

### register_url_convertor()

```python
def register_url_convertor(key: str, convertor: Convertor) -> None
```

Register a custom URL path convertor for use in `{name:type}` path parameters.
