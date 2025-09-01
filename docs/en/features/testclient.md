Unfazed Testing Framework
===============

Unfazed provides a powerful testing framework with `Requestfactory` test client built on HTTPX, allowing you to easily perform comprehensive integration testing of Unfazed applications. This test client supports the complete ASGI protocol, including lifecycle management, state sharing, and various HTTP methods.

## System Overview

### Core Features

- **ASGI Compatible**: Full support for ASGI 3.0 protocol, including HTTP and lifecycle events
- **Lifecycle Management**: Automatically handles application startup and shutdown events
- **State Sharing**: Supports state sharing between requests, simulating real application environment
- **HTTPX Integration**: Built on HTTPX, providing rich HTTP client functionality
- **Async Support**: Complete async operation support
- **Test Isolation**: Each test instance has independent application state

### Core Components

- **Requestfactory**: Test client class, extends `httpx.AsyncClient`
- **ASGITransport**: Custom ASGI transport layer with state management support
- **Lifecycle Management**: Automatically handles startup/shutdown events

## Quick Start

### Basic Usage

```python
# test_basic.py
import pytest
from unfazed.core import Unfazed
from unfazed.test import Requestfactory
from unfazed.http import HttpRequest, JsonResponse

# Define test functions
async def hello_world(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"message": "Hello, World!"})

async def get_user(request: HttpRequest) -> JsonResponse:
    user_id = request.path_params.get("user_id")
    return JsonResponse({"user_id": user_id, "name": f"User {user_id}"})

# Basic test
async def test_basic_request():
    """Test basic GET request"""
    # Create application instance
    unfazed = Unfazed()
    
    # Add routes
    from unfazed.route import path
    unfazed.routes = [
        path("/", endpoint=hello_world),
        path("/users/{user_id:int}", endpoint=get_user),
    ]
    
    # Setup application
    await unfazed.setup()
    
    # Create test client
    async with Requestfactory(unfazed) as client:
        # Test root path
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello, World!"}
        
        # Test path with parameters
        response = await client.get("/users/123")
        assert response.status_code == 200
        assert response.json() == {"user_id": "123", "name": "User 123"}
```

### HTTP Method Testing

```python
# test_http_methods.py
from unfazed.test import Requestfactory
from unfazed.http import HttpRequest, JsonResponse, PlainTextResponse

# Define endpoints for different HTTP methods
async def create_user(request: HttpRequest) -> JsonResponse:
    user_data = await request.json()
    return JsonResponse({"id": 1, **user_data}, status_code=201)

async def update_user(request: HttpRequest) -> JsonResponse:
    user_id = request.path_params.get("user_id")
    user_data = await request.json()
    return JsonResponse({"id": user_id, **user_data})

async def delete_user(request: HttpRequest) -> PlainTextResponse:
    return PlainTextResponse("User deleted", status_code=204)

async def test_http_methods():
    """Test various HTTP methods"""
    unfazed = Unfazed()
    unfazed.routes = [
        path("/users", endpoint=create_user, methods=["POST"]),
        path("/users/{user_id:int}", endpoint=update_user, methods=["PUT"]),
        path("/users/{user_id:int}", endpoint=delete_user, methods=["DELETE"]),
    ]
    await unfazed.setup()
    
    async with Requestfactory(unfazed) as client:
        # Test POST request
        user_data = {"name": "Alice", "email": "alice@example.com"}
        response = await client.post("/users", json=user_data)
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == "Alice"
        assert result["email"] == "alice@example.com"
        
        # Test PUT request
        updated_data = {"name": "Alice Smith", "email": "alice.smith@example.com"}
        response = await client.put("/users/1", json=updated_data)
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "Alice Smith"
        
        # Test DELETE request
        response = await client.delete("/users/1")
        assert response.status_code == 204
        assert response.text == "User deleted"
```

## Lifespan Testing

`Requestfactory` supports complete application Lifespan testing, including startup and shutdown events.

### Basic Lifespan Testing

```python
# test_lifespan.py
from unfazed.lifespan import BaseLifeSpan
from unfazed.test import Requestfactory

class DatabaseSetup(BaseLifeSpan):
    """Simulate database setup lifecycle component"""
    
    async def on_startup(self):
        # Simulate database connection initialization
        self.state["db_connected"] = True
        self.state["user_count"] = 0
        print("Database connection established")
    
    async def on_shutdown(self):
        # Simulate database connection cleanup
        self.state["db_connected"] = False
        print("Database connection closed")

async def get_status(request: HttpRequest) -> JsonResponse:
    """Return database connection status"""
    db_connected = request.app.state.get("db_connected", False)
    user_count = request.app.state.get("user_count", 0)
    return JsonResponse({
        "db_connected": db_connected,
        "user_count": user_count
    })

async def test_lifespan_events():
    """Test lifecycle events"""
    from unfazed.conf import UnfazedSettings
    
    unfazed = Unfazed(
        settings=UnfazedSettings(
            LIFESPAN=["test_lifespan.DatabaseSetup"]
        )
    )
    unfazed.routes = [path("/status", endpoint=get_status)]
    await unfazed.setup()
    
    # Use async with to automatically manage lifecycle
    async with Requestfactory(unfazed) as client:
        response = await client.get("/status")
        assert response.status_code == 200
        result = response.json()
        assert result["db_connected"] is True
        assert result["user_count"] == 0
    
    # After exiting async with, shutdown event has been called

async def test_manual_lifespan():
    """Manual lifecycle control testing"""
    unfazed = Unfazed()
    unfazed.routes = [path("/status", endpoint=get_status)]
    await unfazed.setup()
    
    # Disable automatic lifecycle management
    client = Requestfactory(unfazed, lifespan_on=False)
    
    # Manual startup
    await client.lifespan_startup()
    
    response = await client.get("/status")
    assert response.status_code == 200
    
    # Manual shutdown
    await client.lifespan_shutdown()
```

## Test Configuration

### Pytest

```python
# conftest.py
import pytest
from unfazed.core import Unfazed
from unfazed.test import Requestfactory
from unfazed.conf import UnfazedSettings

@pytest.fixture
async def app():
    """Create test application instance"""
    unfazed = Unfazed(
        settings=UnfazedSettings(
            DEBUG=True,
            DATABASE=None,  # Don't use database in tests
        )
    )
    
    # Add test routes
    from myapp.routes import patterns
    unfazed.routes = patterns
    
    await unfazed.setup()
    return unfazed

@pytest.fixture
async def client(app):
    """Create test client"""
    async with Requestfactory(app) as client:
        yield client

# Use fixtures in test files
async def test_with_fixtures(client):
    """Test using fixtures"""
    response = await client.get("/")
    assert response.status_code == 200
```

### Parametrized Testing

```python
# test_parametrized.py
import pytest

@pytest.mark.parametrize("method,path,expected_status", [
    ("GET", "/", 200),
    ("GET", "/users", 200),
    ("POST", "/users", 201),
    ("GET", "/non-existent", 404),
])
async def test_endpoints(client, method, path, expected_status):
    """Parametrized test for multiple endpoints"""
    response = await getattr(client, method.lower())(path)
    assert response.status_code == expected_status

@pytest.mark.parametrize("user_data,expected_status", [
    ({"name": "Alice", "email": "alice@example.com"}, 201),
    ({"name": "Bob"}, 400),  # Missing email
    ({}, 400),  # Missing required fields
])
async def test_user_creation(client, user_data, expected_status):
    """Parametrized test for user creation"""
    response = await client.post("/users", json=user_data)
    assert response.status_code == expected_status
```

Through Unfazed's testing framework, you can easily perform comprehensive testing of applications, ensuring code quality and application stability. This testing framework provides a complete solution from simple unit tests to complex integration tests, supporting various testing scenarios including lifecycle management.
