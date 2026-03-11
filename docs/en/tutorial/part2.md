# Part 2: Creating Applications and Hello World

In the previous part, we created and started an Unfazed project. Now we will create our first application, implement a "Hello, World" API, and understand how Unfazed organizes code.

## What is an Application?

In Unfazed, an **Application (App)** is the basic unit for organizing business logic. Each app is an independent Python package containing models, endpoints, routes, serializers, and tests. This modular design keeps your codebase organized and enables code reuse across projects. See [App System](../features/app.md) for the full reference.

## Creating the enroll Application

We will create an application named `enroll` for our student course enrollment system.

### Using CLI to Create the App

```bash
# Make sure you're in the backend directory
cd tutorial/src/backend

# Create the enroll app
unfazed-cli startapp -n enroll -t simple
```

The `-t simple` flag uses the basic template. You can also use `-t standard` for a more structured layout with sub-packages. See [Command](../features/command.md) for details.

### Application Directory Structure

```
enroll/
├── admin.py         # Admin panel registration
├── app.py           # AppConfig class (required)
├── endpoints.py     # API endpoint functions
├── models.py        # Tortoise ORM model definitions
├── routes.py        # URL route declarations
├── schema.py        # Pydantic request/response models
├── serializers.py   # Data serializers for CRUD operations
├── services.py      # Business logic layer
├── settings.py      # App-level settings
└── test_all.py      # Test cases
```

### Key Files

| File             | Purpose                                                          | Feature Reference                              |
| ---------------- | ---------------------------------------------------------------- | ---------------------------------------------- |
| `app.py`         | AppConfig class — required for every app.                        | [App](../features/app.md)                      |
| `endpoints.py`   | Async functions that handle HTTP requests.                       | [Endpoint](../features/endpoint.md)            |
| `routes.py`      | URL path-to-endpoint mapping.                                    | [Routing](../features/route.md)                |
| `models.py`      | Database table structures and relationships.                     | [Tortoise ORM](../features/tortoise-orm.md)    |
| `serializers.py` | Auto-generated Pydantic models with CRUD operations.             | [Serializer](../features/serializer.md)        |
| `schema.py`      | Request/response Pydantic models for OpenAPI documentation.      | [OpenAPI](../features/openapi.md)              |
| `admin.py`       | Admin panel configuration.                                       | [Admin](../features/contrib/admin.md)          |

## Implementing Hello World

### Step 1: Define Endpoint Functions

Edit `enroll/endpoints.py`:

```python
# enroll/endpoints.py

from unfazed.http import HttpRequest, PlainTextResponse, JsonResponse


async def hello(request: HttpRequest) -> PlainTextResponse:
    """Simple plain text response"""
    return PlainTextResponse("Hello, World!")


async def hello_json(request: HttpRequest) -> JsonResponse:
    """JSON format response"""
    return JsonResponse({
        "message": "Hello, World!",
        "framework": "Unfazed",
    })
```

Key points:
- `HttpRequest` is Unfazed's request class, extended from Starlette. See [Request](../features/request.md).
- `PlainTextResponse` and `JsonResponse` are response classes. See [Response](../features/response.md).
- All endpoint functions are `async` — Unfazed natively supports asynchronous programming.

### Step 2: Configure Routes

Edit `enroll/routes.py`:

```python
# enroll/routes.py

from unfazed.route import path

from .endpoints import hello, hello_json

patterns = [
    path("/hello", endpoint=hello),
    path("/hello-json", endpoint=hello_json),
]
```

The `patterns` list defines URL-to-endpoint mappings. The `path()` function defaults to `GET` and `HEAD` methods when `methods` is not specified. See [Routing](../features/route.md).

### Step 3: Register App Routes in Root URL Config

Edit `entry/routes.py`:

```python
# entry/routes.py

from unfazed.route import path, include

patterns = [
    path("/api/enroll", routes=include("enroll.routes")),
]
```

`include()` imports the `patterns` list from `enroll.routes` and prefixes them with `/api/enroll`. This means `/api/enroll/hello` maps to the `hello` endpoint.

### Step 4: Register the App in Settings

Edit `entry/settings/__init__.py` and add `enroll` to `INSTALLED_APPS`:

```python
# entry/settings/__init__.py

UNFAZED_SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "Tutorial Project",
    "ROOT_URLCONF": "entry.routes",
    "INSTALLED_APPS": [
        "enroll",
    ],
    "MIDDLEWARE": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
}
```

`INSTALLED_APPS` tells Unfazed which apps to load at startup. Each app must contain an `app.py` with an `AppConfig` class. `ROOT_URLCONF` points to the module containing the root `patterns` list. See [Settings](../features/settings.md).

## Testing the API

### Start the Server

```bash
make run
# or: uvicorn asgi:application --host 127.0.0.1 --port 9527 --reload
```

### Send Requests

```bash
curl http://127.0.0.1:9527/api/enroll/hello
# Output: Hello, World!

curl http://127.0.0.1:9527/api/enroll/hello-json
# Output: {"message":"Hello, World!","framework":"Unfazed"}
```

## Request-Response Architecture

Through this simple example, we can see Unfazed's layered architecture:

```
HTTP Request → Routes → Endpoints (Controller) → Services (Business Logic) → Models (Data) → Database
                                                                                    ↓
HTTP Response ← Routes ← Endpoints ← Response
```

| Layer                     | Responsibility                              |
| ------------------------- | ------------------------------------------- |
| **Routes**                | URL path to handler mapping                 |
| **Endpoints (Controller)**| Handle HTTP requests, call business logic   |
| **Services (Business)**   | Implement core business rules               |
| **Models (Data)**         | Data models and database operations         |

Each layer has clear responsibilities, making the codebase easy to test and maintain.

## Automatic API Documentation

Unfazed has built-in OpenAPI support. After starting the project, you can access interactive API documentation at:

- **Swagger UI**: `http://127.0.0.1:9527/openapi/docs`
- **ReDoc**: `http://127.0.0.1:9527/openapi/redoc`

These are generated automatically from your endpoint type hints. See [OpenAPI](../features/openapi.md) for configuration options.

> **Note**: The OpenAPI documentation routes are only available when the `OPENAPI` setting is configured and `allow_public` is `True`.

## Next Steps

You have created your first Unfazed application and implemented a Hello World API. In the next part, we will:

- Define data models (Student and Course)
- Use Tortoise ORM for database operations
- Create serializers for data validation and CRUD

Continue to **[Part 3: Data Models and Serializers](part3.md)**.
