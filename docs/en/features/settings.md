Unfazed Configuration System
================

Unfazed's configuration system is a type-safe configuration management system based on Pydantic, providing powerful configuration validation, auto-completion, and error checking functionality. Through the combination of `settings.py` files and configuration classes, it provides a clear and maintainable configuration management solution for projects.

## System Overview

### Core Features

- **Type Safety**: Pydantic-based configuration validation ensures configuration type correctness
- **Modular Design**: Supports application-level configuration modules for easy configuration management in large projects
- **Auto Discovery**: Automatically registers configuration classes through decorators
- **Lazy Loading**: Configuration is loaded and validated only on first access
- **Caching Mechanism**: Configuration is automatically cached after loading to improve access performance

### Core Components

- **SettingsProxy**: Configuration proxy class responsible for configuration loading, caching, and access
- **register_settings**: Decorator for registering configuration classes
- **UnfazedSettings**: Framework core configuration class
- **Configuration Modules**: Configuration classes for various functional modules

### Design Philosophy

Unfazed configuration system has the following advantages over Django:

**Django's approach**:
```python
# settings.py
FOO = 'bar'
DATABASE_NAME = 'mydb'
CACHE_TIMEOUT = 3600

# app/views.py
from django.conf import settings

print(settings.FOO)  # No type hints, error-prone
print(settings.DATABASE_NAME)  # Scattered configuration, hard to manage
```

**Unfazed's approach**:
```python
# settings.py
APP_SETTINGS = {
    'FOO': 'bar',
    'BAR': 123
}

DATABASE_SETTINGS = {
    'NAME': 'mydb',
    'HOST': 'localhost',
    'PORT': 5432
}

# app/settings.py
from pydantic import BaseModel, Field
from unfazed.conf import register_settings

@register_settings("APP_SETTINGS")
class AppSettings(BaseModel):
    FOO: str = Field(..., description="Application identifier")
    BAR: int = Field(default=100, ge=1, description="Numeric configuration")

@register_settings("DATABASE_SETTINGS")
class DatabaseSettings(BaseModel):
    NAME: str = Field(..., description="Database name")
    HOST: str = Field(default="localhost", description="Database host")
    PORT: int = Field(default=5432, ge=1, le=65535, description="Database port")

# app/services.py
from unfazed.conf import settings
from .settings import AppSettings, DatabaseSettings

app_settings: AppSettings = settings["APP_SETTINGS"]      # Complete type hints
db_settings: DatabaseSettings = settings["DATABASE_SETTINGS"]

print(app_settings.FOO)  # Type safe, IDE auto-completion
print(db_settings.NAME)  # Grouped configuration, easy to manage
```

### Configuration Advantages

1. **Type Safety**: Pydantic provides complete type validation and conversion
2. **Modular**: Configuration grouped by functional modules for easy management and maintenance
3. **Documentation**: Configuration items can add descriptions and validation rules
4. **IDE Support**: Complete type hints and auto-completion
5. **Runtime Validation**: Automatically validates configuration correctness at startup

## Quick Start

### Basic Usage

```python
# 1. Define configuration class (myapp/settings.py)
from pydantic import BaseModel, Field
from unfazed.conf import register_settings

@register_settings("MYAPP_SETTINGS")
class MyAppSettings(BaseModel):
    app_name: str = Field(..., description="Application name")
    debug_mode: bool = Field(default=False, description="Debug mode")
    max_connections: int = Field(default=100, ge=1, le=1000, description="Maximum connections")

# 2. Configuration settings (settings.py)
MYAPP_SETTINGS = {
    "app_name": "My Application",
    "debug_mode": True,
    "max_connections": 200
}

# 3. Use configuration (myapp/services.py)
from unfazed.conf import settings
from .settings import MyAppSettings

def get_app_config():
    config: MyAppSettings = settings["MYAPP_SETTINGS"]
    print(f"Application name: {config.app_name}")
    print(f"Debug mode: {config.debug_mode}")
    print(f"Maximum connections: {config.max_connections}")
    return config
```

### Advanced Configuration Example

```python
# advanced_settings.py
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from unfazed.conf import register_settings

@register_settings("API_SETTINGS")
class APISettings(BaseModel):
    base_url: str = Field(..., description="API base URL")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout (seconds)")
    retry_times: int = Field(default=3, ge=0, le=10, description="Retry count")
    headers: Dict[str, str] = Field(default_factory=dict, description="Default request headers")
    allowed_hosts: List[str] = Field(default_factory=list, description="Allowed host list")
    
    @validator('base_url')
    def validate_base_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('base_url must start with http:// or https://')
        return v

@register_settings("FEATURE_FLAGS")
class FeatureFlags(BaseModel):
    enable_caching: bool = Field(default=True, description="Enable caching")
    enable_logging: bool = Field(default=True, description="Enable logging")
    enable_metrics: bool = Field(default=False, description="Enable metrics collection")
    experimental_features: List[str] = Field(default_factory=list, description="Experimental features list")

# Configuration in settings.py
API_SETTINGS = {
    "base_url": "https://api.example.com",
    "timeout": 60,
    "retry_times": 5,
    "headers": {
        "User-Agent": "MyApp/1.0",
        "Accept": "application/json"
    },
    "allowed_hosts": ["api.example.com", "backup.example.com"]
}

FEATURE_FLAGS = {
    "enable_caching": True,
    "enable_logging": True,
    "enable_metrics": True,
    "experimental_features": ["new_algorithm", "beta_ui"]
}
```

## UnfazedSettings Core Configuration

`UnfazedSettings` is Unfazed framework's core configuration class, containing all basic configurations required for starting and running applications.

### Complete Configuration Example

```python
# settings.py
UNFAZED_SETTINGS = {
    # Basic configuration
    "DEBUG": True,
    "PROJECT_NAME": "My Project",
    "VERSION": "1.0.0",
    "ROOT_URLCONF": "entry.routes",
    
    # Applications and middleware
    "INSTALLED_APPS": [
        "unfazed.contrib.admin",
        "unfazed.contrib.auth",
        "unfazed.contrib.session",
        "myapp1",
        "myapp2",
    ],
    "MIDDLEWARE": [
        "unfazed.middleware.internal.common.CommonMiddleware",
        "unfazed.middleware.internal.cors.CORSMiddleware",
        "unfazed.middleware.internal.gzip.GZipMiddleware",
        "unfazed.middleware.internal.trustedhost.TrustedHostMiddleware",
        "unfazed.contrib.session.middleware.SessionMiddleware",
    ],
    
    # Lifecycle management
    "LIFESPAN": [
        "unfazed.cache.lifespan.CacheClear",
        "myapp.lifespan.DatabaseSetup",
    ],
    
    # Database configuration
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "tortoise.backends.asyncpg",
                "CREDENTIALS": {
                    "host": "localhost",
                    "port": "5432",
                    "user": "app",
                    "password": "app",
                    "database": "app",
                    "minsize": 1,
                    "maxsize": 10,
                }
            },
            "cache_db": {
                "ENGINE": "tortoise.backends.sqlite",
                "CREDENTIALS": {
                    "file_path": "cache.db"
                }
            }
        },
        "APPS": {
            "models": {
                "models": ["myapp.models", "unfazed.contrib.auth.models"],
                "default_connection": "default",
            }
        },
        "USE_TZ": True,
        "TIMEZONE": "Asia/Shanghai"
    },
    
    # Cache configuration
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "OPTIONS": {
                "MAX_ENTRIES": 1000,
                "TIMEOUT": 300,
            }
        },
        "redis": {
            "BACKEND": "unfazed.cache.backends.redis.defaultclient.DefaultBackend",
            "LOCATION": "redis://localhost:6379/0",
            "OPTIONS": {
                "max_connections": 100,
                "decode_responses": True,
                "retry_on_timeout": True,
                "health_check_interval": 30,
            }
        }
    },
    
    # OpenAPI configuration
    "OPENAPI": {
        "info": {
            "title": "My API",
            "version": "1.0.0",
            "description": "This is an example API",
            "contact": {
                "name": "API Support",
                "email": "support@example.com"
            }
        },
        "servers": [
            {
                "url": "http://localhost:8000",
                "description": "Development Environment"
            },
            {
                "url": "https://api.example.com",
                "description": "Production Environment"
            }
        ],
        "allow_public": False,  # Close public access in production
    },
    
    # Middleware related configuration
    "CORS": {
        "allow_origins": ["http://localhost:3000", "https://example.com"],
        "allow_methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["*"],
        "allow_credentials": True,
        "max_age": 3600,
    },
    
    "TRUSTED_HOST": {
        "allowed_hosts": ["localhost", "example.com", "*.example.com"],
        "www_redirect": True,
    },
    
    "GZIP": {
        "minimum_size": 1024,
        "compresslevel": 6,
    },
    
    # Logging configuration
    "LOGGING": {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "{asctime} [{levelname}] {name}: {message}",
                "style": "{",
            },
            "simple": {
                "format": "{levelname} {message}",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "verbose",
                "level": "INFO",
            },
            "file": {
                "class": "unfazed.logging.handlers.UnfazedRotatingFileHandler",
                "filename": "logs/app.log",
                "formatter": "verbose",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "level": "DEBUG",
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
        "loggers": {
            "unfazed": {
                "level": "DEBUG",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "myapp": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": True,
            },
        },
    },
}
```

### Configuration Item Details

#### Basic Configuration

| Configuration Item | Type   | Default Value | Description                                       |
| ------------------ | ------ | ------------- | ------------------------------------------------- |
| `DEBUG`            | `bool` | `True`        | Debug mode, affects error display and performance |
| `PROJECT_NAME`     | `str`  | `"Unfazed"`   | Project name, used for log identification         |
| `VERSION`          | `str`  | `"0.0.1"`     | Project version number                            |
| `ROOT_URLCONF`     | `str`  | `None`        | Route configuration root module                   |

#### Applications and Middleware

```python
# Application configuration
INSTALLED_APPS = [
    # Built-in applications
    "unfazed.contrib.admin",        # Admin interface
    "unfazed.contrib.auth",         # Authentication system
    "unfazed.contrib.session",      # Session management
    
    # Custom applications
    "myapp.users",                  # User module
    "myapp.orders",                 # Order module
    "myapp.products",               # Product module
]

# Middleware configuration (in execution order)
MIDDLEWARE = [
    "unfazed.middleware.internal.common.CommonMiddleware",       # Common middleware
    "unfazed.middleware.internal.cors.CORSMiddleware",          # CORS handling
    "unfazed.middleware.internal.trustedhost.TrustedHostMiddleware", # Host validation
    "unfazed.middleware.internal.gzip.GZipMiddleware",          # Response compression
    "unfazed.contrib.session.middleware.SessionMiddleware",     # Session middleware
    "myapp.middleware.AuthMiddleware",                          # Custom authentication
]
```

#### Database Configuration

```python
DATABASE = {
    "CONNECTIONS": {
        # Primary database
        "default": {
            "ENGINE": "tortoise.backends.asyncpg",  # PostgreSQL
            "CREDENTIALS": {
                "host": "localhost",
                "port": 5432,
                "user": "myapp",
                "password": "secret",
                "database": "myapp_db",
                "minsize": 1,
                "maxsize": 20,
                "command_timeout": 60,
                "server_settings": {
                    "application_name": "myapp",
                }
            }
        },
        
        # Read-only database
        "readonly": {
            "ENGINE": "tortoise.backends.asyncpg",
            "CREDENTIALS": {
                "host": "readonly.example.com",
                "port": 5432,
                "user": "readonly_user",
                "password": "readonly_pass",
                "database": "myapp_db",
                "minsize": 1,
                "maxsize": 10,
            }
        },
        
        # Cache database
        "cache": {
            "ENGINE": "tortoise.backends.sqlite",
            "CREDENTIALS": {
                "file_path": "cache.db",
                "journal_mode": "WAL",
                "synchronous": "NORMAL",
            }
        }
    },
    
    "APPS": {
        "models": {
            "models": [
                "myapp.users.models",
                "myapp.orders.models",
                "unfazed.contrib.auth.models",
            ],
            "default_connection": "default",
        },
        "cache_models": {
            "models": ["myapp.cache.models"],
            "default_connection": "cache",
        }
    },
    
    "USE_TZ": True,
    "TIMEZONE": "Asia/Shanghai"
}
```

#### Cache Configuration

```python
CACHE = {
    # Local memory cache
    "default": {
        "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
        "OPTIONS": {
            "MAX_ENTRIES": 1000,    # Maximum cache entries
            "TIMEOUT": 300,         # Default timeout (seconds)
            "PREFIX": "myapp:",     # Cache key prefix
            "VERSION": 1,           # Cache version
        }
    },
    
    # Redis cache
    "redis": {
        "BACKEND": "unfazed.cache.backends.redis.defaultclient.DefaultBackend",
        "LOCATION": "redis://localhost:6379/0",
        "OPTIONS": {
            "max_connections": 100,
            "decode_responses": True,
            "retry_on_timeout": True,
            "retry_on_error": ["ConnectionError", "TimeoutError"],
            "health_check_interval": 30,
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
        }
    },
    
    # Redis cluster
    "redis_cluster": {
        "BACKEND": "unfazed.cache.backends.redis.clusterclient.ClusterBackend",
        "LOCATION": [
            "redis://node1.example.com:6379",
            "redis://node2.example.com:6379",
            "redis://node3.example.com:6379",
        ],
        "OPTIONS": {
            "max_connections_per_node": 50,
            "skip_full_coverage_check": True,
            "decode_responses": True,
        }
    }
}
```

## Custom Configuration

### Application-level Configuration

```python
# myapp/settings.py
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from unfazed.conf import register_settings

@register_settings("EMAIL_SETTINGS")
class EmailSettings(BaseModel):
    smtp_host: str = Field(..., description="SMTP server address")
    smtp_port: int = Field(default=587, ge=1, le=65535, description="SMTP port")
    username: str = Field(..., description="SMTP username")
    password: str = Field(..., description="SMTP password")
    use_tls: bool = Field(default=True, description="Use TLS")
    from_email: str = Field(..., description="Sender email")
    
    @validator('smtp_host')
    def validate_smtp_host(cls, v):
        if not v.strip():
            raise ValueError('SMTP host address cannot be empty')
        return v.strip()

@register_settings("PAYMENT_SETTINGS")
class PaymentSettings(BaseModel):
    provider: str = Field(..., description="Payment provider")
    api_key: str = Field(..., description="API key")
    secret_key: str = Field(..., description="Secret key")
    webhook_url: str = Field(..., description="Callback URL")
    test_mode: bool = Field(default=True, description="Test mode")
    supported_currencies: List[str] = Field(
        default=["USD", "EUR"], 
        description="Supported currencies"
    )
    
    @validator('api_key', 'secret_key')
    def validate_keys(cls, v):
        if len(v) < 32:
            raise ValueError('Key length cannot be less than 32 characters')
        return v

# settings.py
EMAIL_SETTINGS = {
    "smtp_host": "smtp.example.com",
    "smtp_port": 587,
    "username": "noreply@example.com",
    "password": "your_password",
    "use_tls": True,
    "from_email": "noreply@example.com"
}

PAYMENT_SETTINGS = {
    "provider": "stripe",
    "api_key": "your_very_long_api_key_here_32chars",
    "secret_key": "your_very_long_secret_key_here_32chars",
    "webhook_url": "https://api.example.com/payment/webhook",
    "test_mode": False,
    "supported_currencies": ["USD", "EUR", "GBP"]
}
```

### Environment-related Configuration

```python
# config/settings.py
import os
from typing import Dict, Any

# Environment variable reading
def get_env(key: str, default: Any = None, cast_type: type = str):
    """Get configuration from environment variables"""
    value = os.environ.get(key, default)
    if value is None:
        return None
    
    if cast_type == bool:
        return value.lower() in ('true', '1', 'yes', 'on')
    elif cast_type == list:
        return [item.strip() for item in value.split(',') if item.strip()]
    
    return cast_type(value)

# Basic configuration
UNFAZED_SETTINGS = {
    "DEBUG": get_env("DEBUG", True, bool),
    "PROJECT_NAME": get_env("PROJECT_NAME", "MyApp"),
    "VERSION": get_env("VERSION", "1.0.0"),
    
    # Database configuration
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "tortoise.backends.asyncpg",
                "CREDENTIALS": {
                    "host": get_env("DB_HOST", "localhost"),
                    "port": get_env("DB_PORT", 5432, int),
                    "user": get_env("DB_USER", "app"),
                    "password": get_env("DB_PASSWORD", "password"),
                    "database": get_env("DB_NAME", "app"),
                    "minsize": get_env("DB_MIN_SIZE", 1, int),
                    "maxsize": get_env("DB_MAX_SIZE", 10, int),
                }
            }
        }
    },
    
    # Redis configuration
    "CACHE": {
        "redis": {
            "BACKEND": "unfazed.cache.backends.redis.defaultclient.DefaultBackend",
            "LOCATION": get_env("REDIS_URL", "redis://localhost:6379/0"),
            "OPTIONS": {
                "max_connections": get_env("REDIS_MAX_CONN", 100, int),
                "decode_responses": True,
            }
        }
    },
    
    # Security configuration
    "CORS": {
        "allow_origins": get_env("CORS_ORIGINS", ["*"], list),
        "allow_credentials": get_env("CORS_CREDENTIALS", True, bool),
    },
    
    "TRUSTED_HOST": {
        "allowed_hosts": get_env("ALLOWED_HOSTS", ["*"], list),
    }
}

# Production environment special configuration
if not get_env("DEBUG", True, bool):
    UNFAZED_SETTINGS.update({
        "OPENAPI": {
            "allow_public": False,  # Close OpenAPI public access in production
        }
    })
```

Through Unfazed's configuration system, you can build type-safe, well-structured, and maintainable application configurations. This system provides a complete solution from simple configuration to complex enterprise-level configuration management, ensuring applications run correctly in various environments.
