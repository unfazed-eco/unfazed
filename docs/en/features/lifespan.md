Unfazed Lifespan Management
=========================

Unfazed's lifespan management system is based on the ASGI Lifespan protocol, providing hook mechanisms for application startup and shutdown. Through lifespan management, you can gracefully handle resource initialization, cleanup tasks, and state sharing.

## System Overview

### Core Components

- **BaseLifeSpan**: Base class for lifespan components, defining standard interfaces
- **LifeSpanHandler**: Lifespan handler managing all registered lifespan components
- **State**: Application state container for sharing data between different components

### Lifespan Events

1. **Startup Event (on_startup)**: Executed when the application starts, used for resource initialization
2. **Shutdown Event (on_shutdown)**: Executed when the application stops, used for resource cleanup

### Workflow

```
App Start → Execute all on_startup → App Running → App Stop → Execute all on_shutdown → App Exit
```

## Quick Start

### 1. Create Lifespan Component

```python
from unfazed.lifespan import BaseLifeSpan
import typing as t

class DatabaseLifeSpan(BaseLifeSpan):
    """Database connection lifespan management"""
    
    def __init__(self, unfazed) -> None:
        super().__init__(unfazed)
        self.db_connection = None
    
    async def on_startup(self) -> None:
        """Initialize database connection when app starts"""
        print("Initializing database connection...")
        # Simulate database connection initialization
        self.db_connection = await self.create_database_connection()
        print("Database connection initialization complete")
    
    async def on_shutdown(self) -> None:
        """Close database connection when app stops"""
        print("Closing database connection...")
        if self.db_connection:
            await self.db_connection.close()
        print("Database connection closed")
    
    async def create_database_connection(self):
        """Create database connection (example)"""
        # Actual database connection logic
        return {"connection": "database_connection_object"}
    
    @property
    def state(self) -> t.Dict[str, t.Any]:
        """Return state to be shared"""
        return {
            "db_connection": self.db_connection,
            "db_status": "connected" if self.db_connection else "disconnected"
        }
```

### 2. Register Lifespan Component

Register lifespan components in the configuration file:

```python
# settings.py
UNFAZED_SETTINGS = {
    "LIFESPAN": [
        "yourapp.lifespan.DatabaseLifeSpan",
        "yourapp.lifespan.RedisLifeSpan",
        "yourapp.lifespan.LoggingLifeSpan",
    ]
}
```

### 3. Start Application

```shell
uvicorn asgi:application --host 0.0.0.0 --port 9527
```

**Example Output:**
```
Initializing database connection...
Database connection initialization complete
Initializing Redis connection...
Redis connection initialization complete
Application startup complete
```

## State Sharing Mechanism

### Accessing Shared State

Lifespan components can expose shared data to the entire application through the `state` attribute. This data can be accessed during request processing:

```python
from unfazed.http import HttpRequest, JsonResponse

async def get_database_status(request: HttpRequest) -> JsonResponse:
    """Get database connection status"""
    
    # Access shared state from lifespan components
    db_connection = request.state.db_connection
    db_status = request.state.db_status
    
    return JsonResponse({
        "database_connected": db_status == "connected",
        "connection_info": str(db_connection) if db_connection else None
    })

async def query_users(request: HttpRequest) -> JsonResponse:
    """Query user list"""
    
    # Use shared database connection
    db_connection = request.state.db_connection
    
    if not db_connection:
        return JsonResponse({"error": "Database connection unavailable"}, status_code=500)
    
    # Use database connection to execute query
    # users = await db_connection.fetch_all("SELECT * FROM users")
    
    return JsonResponse({
        "users": [],  # Actual user data
        "message": "Query successful"
    })
```

## Practical Application Scenarios

### External Service Connections

```python
import httpx
from unfazed.lifespan import BaseLifeSpan

class ExternalServiceLifeSpan(BaseLifeSpan):
    """External service connection management"""
    
    def __init__(self, unfazed) -> None:
        super().__init__(unfazed)
        self.http_client = None
        self.service_health = {}
    
    async def on_startup(self) -> None:
        """Initialize HTTP client and check external services"""
        # Create HTTP client
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=50, max_connections=100)
        )
        
        # Check external service health status
        await self.check_external_services()
        print("External service connections initialized")
    
    async def on_shutdown(self) -> None:
        """Close HTTP client"""
        if self.http_client:
            await self.http_client.aclose()
            print("External service connections closed")
    
    async def check_external_services(self):
        """Check external service health status"""
        services = {
            "payment_api": "https://api.payment.com/health",
            "notification_api": "https://api.notification.com/health"
        }
        
        for service_name, health_url in services.items():
            try:
                response = await self.http_client.get(health_url)
                self.service_health[service_name] = response.status_code == 200
            except Exception:
                self.service_health[service_name] = False
    
    @property
    def state(self) -> dict:
        return {
            "http_client": self.http_client,
            "service_health": self.service_health
        }
```
