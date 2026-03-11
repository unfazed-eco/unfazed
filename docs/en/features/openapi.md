Unfazed OpenAPI
===============

Unfazed automatically generates an [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0) schema from your endpoint type hints and serves interactive documentation via Swagger UI and Redoc. Parameter annotations (`Path`, `Query`, `Header`, `Cookie`, `Json`, `Form`, `File`) and `ResponseSpec` return types are translated directly into the OpenAPI spec — no manual schema writing required.

## Quick Start

### 1. Add the OPENAPI setting

```python
# settings.py
UNFAZED_SETTINGS = {
    "PROJECT_NAME": "myproject",
    "OPENAPI": {
        "info": {
            "title": "My Project API",
            "version": "1.0.0",
            "description": "API documentation for My Project",
        },
    },
}
```

### 2. Browse the docs

Once the server is running, visit:

- **Swagger UI:** [http://localhost:8000/openapi/docs](http://localhost:8000/openapi/docs)
- **Redoc:** [http://localhost:8000/openapi/redoc](http://localhost:8000/openapi/redoc)
- **Raw JSON schema:** [http://localhost:8000/openapi/openapi.json](http://localhost:8000/openapi/openapi.json)

These routes are added automatically when the `OPENAPI` setting is present and `allow_public` is `True`.

## Configuration

The full `OPENAPI` setting:

```python
"OPENAPI": {
    # OpenAPI spec fields
    "openapi": "3.1.1",                     # spec version (default "3.1.1")
    "info": {
        "title": "My API",                  # required
        "version": "1.0.0",                 # required
        "description": "API description",
        "termsOfService": "https://example.com/terms",
        "contact": {"name": "Support", "email": "support@example.com"},
        "license": {"name": "MIT"},
    },
    "servers": [
        {"url": "/", "description": "Default"},
        {"url": "https://api.example.com", "description": "Production"},
    ],
    "externalDocs": {
        "url": "https://docs.example.com",
        "description": "Full documentation",
    },

    # UI configuration
    "json_route": "/openapi/openapi.json",  # path to the JSON schema endpoint
    "swagger_ui": {
        "css": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        "js": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        "favicon": "https://www.openapis.org/wp-content/uploads/sites/3/2016/11/favicon.png",
    },
    "redoc": {
        "js": "https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js",
    },

    # Access control
    "allow_public": True,                   # set to False in production
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `openapi` | `str` | `"3.1.1"` | OpenAPI spec version (`"3.1.0"` or `"3.1.1"`). |
| `info` | `dict` | required | API metadata (`title` and `version` are required). |
| `servers` | `List[dict]` | `[{"url": "/"}]` | Server URLs for the API. |
| `externalDocs` | `dict \| None` | `None` | Link to external documentation. |
| `json_route` | `str` | `"/openapi/openapi.json"` | URL path for the raw JSON schema. |
| `swagger_ui` | `dict` | CDN defaults | CSS/JS/favicon URLs for Swagger UI. |
| `redoc` | `dict` | CDN defaults | JS URL for Redoc. |
| `allow_public` | `bool` | `True` | Enable/disable the doc endpoints. |

## How It Works

Unfazed inspects every registered `Route` at startup and builds the OpenAPI schema from endpoint signatures:

1. **Parameters** — `Path`, `Query`, `Header`, and `Cookie` annotations become OpenAPI `parameters` with their types, defaults, and whether they are required.

2. **Request body** — `Json`, `Form`, and `File` annotations become the OpenAPI `requestBody`. The Pydantic model's JSON schema is included as a `$ref` in `components/schemas`.

3. **Responses** — `ResponseSpec` in the return type annotation becomes OpenAPI `responses`. Each spec maps to a status code with the model's JSON schema as the response body.

4. **Tags** — The `tags` argument on `Route` or `path()` becomes OpenAPI tags for grouping endpoints.

For example, this endpoint:

```python
import typing as t
from pydantic import BaseModel
from unfazed.http import HttpRequest, JsonResponse
from unfazed.route import params as p


class UserBody(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: int
    name: str


async def create_user(
    request: HttpRequest,
    body: t.Annotated[UserBody, p.Json()],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=UserResponse, code="201")]:
    return JsonResponse({"id": 1, "name": body.name}, status_code=201)
```

generates an OpenAPI path with:
- A `requestBody` containing `UserBody` as JSON schema
- A `201` response containing `UserResponse` as JSON schema

### Route-level OpenAPI metadata

Routes support additional fields that appear in the schema:

```python
from unfazed.route import path

routes = [
    path(
        "/users",
        endpoint=create_user,
        methods=["POST"],
        tags=["users"],
        summary="Create a new user",
        description="Register a new user account",
        deprecated=False,
        externalDocs={"url": "https://docs.example.com/users"},
    ),
]
```

### Excluding routes from the schema

Set `include_in_schema=False` to hide a route from the OpenAPI spec:

```python
path("/health", endpoint=health_check, include_in_schema=False)
```

## Exporting the Schema

Use the `export-openapi` CLI command to write the schema to a YAML file (requires `pyyaml`):

```bash
unfazed-cli export-openapi -l ./docs
# OpenAPI schema exported to ./docs/openapi.yaml
```

## Disabling in Production

Set `allow_public` to `False` to prevent the doc endpoints from being registered:

```python
"OPENAPI": {
    "info": {"title": "My API", "version": "1.0.0"},
    "allow_public": False,
}
```

When `allow_public` is `False`, the `/openapi/docs`, `/openapi/redoc`, and `/openapi/openapi.json` routes are not created. The schema is still generated internally (for `export-openapi`), but it is not served over HTTP.

## API Reference

### OpenApi

```python
class OpenApi:
    schema: Dict[str, Any] | None = None
```

Class that generates and stores the OpenAPI schema. Used internally by the framework.

**Class methods:**

- `create_schema(routes: List[Route], openapi_setting: OpenAPI) -> Dict`: Generate the full OpenAPI schema from routes and settings. Stores the result in `OpenApi.schema`.
- `create_openapi_model(routes: List[Route], openapi_setting: OpenAPI) -> openapi_pydantic.OpenAPI`: Generate the schema as a Pydantic model.
- `create_pathitem_from_route(route: Route) -> PathItem`: Convert a single route into an OpenAPI path item.
- `create_tags_from_route(route: Route, tags: Dict) -> None`: Extract tags from a route.
- `create_schema_from_route_resp_model(route: Route) -> Dict`: Extract response model schemas.
- `create_schema_from_route_request_model(route: Route) -> Dict`: Extract request body schemas.

### OpenAPI (settings model)

```python
class OpenAPI(BaseModel):
    openapi: Literal["3.1.0", "3.1.1"] = "3.1.1"
    servers: List[Server] = [Server(url="/")]
    info: Info
    externalDocs: ExternalDocumentation | None = None
    json_route: str = "/openapi/openapi.json"
    swagger_ui: SwaggerUI = SwaggerUI()
    redoc: Redoc = Redoc()
    allow_public: bool = True
```

Pydantic model for the `OPENAPI` setting.

### SwaggerUI

```python
class SwaggerUI(BaseModel):
    css: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"
    js: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"
    favicon: str = "https://www.openapis.org/wp-content/uploads/sites/3/2016/11/favicon.png"
```

CDN URLs for Swagger UI assets. Override to self-host.

### Redoc

```python
class Redoc(BaseModel):
    js: str = "https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"
```

CDN URL for Redoc JS bundle. Override to self-host.
