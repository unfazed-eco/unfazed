Unfazed Logging System
=====================

Unfazed provides a logging system designed for production environments, solving log safety issues in multi-process web applications and providing flexible configuration management mechanisms.

## System Overview

### Core Components

- **LogCenter**: Log configuration management center responsible for configuration merging and initialization
- **UnfazedRotatingFileHandler**: Process-safe log file handler supporting log rotation
- **Default Configuration**: Provides out-of-the-box log configuration for common scenarios

### Key Features

1. **Process Safety**: Each process creates independent log files, avoiding multi-process write conflicts
2. **Automatic Rotation**: Intelligent log rotation mechanism based on file size
3. **Configuration Merging**: Automatically merge user configuration with default configuration
4. **Flexible Format**: Support custom log formats and multiple output methods

## Multi-Process Safety Issues

### Problem Background

In Python, the `logging` module is thread-safe but not process-safe. When web applications use multi-process deployment methods like `uvicorn` and `gunicorn`, multiple processes writing to the same log file simultaneously can cause:

- **Data Race**: File write conflicts leading to chaotic or lost log content
- **File Locking**: Processes competing for file locks, affecting performance
- **Log Corruption**: Concurrent writing may cause log file format errors

> Reference: [Python Logging Thread Safety](https://docs.python.org/3/library/logging.html#thread-safety)

### Unfazed Solution

Unfazed solves this problem by creating independent log files for each process:

```
App Process 1 → unfazed_hostname_pid12345_ts1630000000.log
App Process 2 → unfazed_hostname_pid12346_ts1630000000.log
App Process 3 → unfazed_hostname_pid12347_ts1630000000.log
```

## Quick Start

### 1. Basic Configuration

```python
# settings.py
UNFAZED_SETTINGS = {
    "LOGGING": {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "file": {
                "class": "unfazed.logging.handlers.UnfazedRotatingFileHandler",
                "filename": "app.log",
                "maxBytes": 10485760,  # 10MB
                "formatter": "detailed",
                "encoding": "utf-8"
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "INFO"
            }
        },
        "loggers": {
            "unfazed": {
                "handlers": ["file", "console"],
                "level": "DEBUG",
                "propagate": False
            },
            "myapp": {
                "handlers": ["file"],
                "level": "INFO",
                "propagate": False
            }
        }
    }
}
```

### 2. Using in Application

```python
import logging
from unfazed.http import HttpRequest, JsonResponse

# Get logger
logger = logging.getLogger("myapp")

async def user_login(request: HttpRequest) -> JsonResponse:
    """User login endpoint"""

    # Log request information
    logger.info(f"User login request: IP={request.client.host}")
    
    # Business logic
    username = request.json.get("username")
    password = request.json.get("password")
    
    if not username or not password:
        logger.warning(f"Login parameters missing: username={username}")
        return JsonResponse({"error": "Username and password cannot be empty"}, status_code=400)
    
    # Simulate authentication
    user = await authenticate_user(username, password)
    
    if user:
        logger.info(f"User login successful: user_id={user.id}, username={username}")
        return JsonResponse({"message": "Login successful", "user_id": user.id})
    else:
        logger.warning(f"User login failed: username={username}, reason=invalid_credentials")
        return JsonResponse({"error": "Incorrect username or password"}, status_code=401)

async def authenticate_user(username: str, password: str):
    """Simulate user authentication"""
    # Actual authentication logic
    return None
```

### 3. Start Application

```bash
# Single process startup
uvicorn asgi:application --host 0.0.0.0 --port 9527

# Multi-process startup 
uvicorn asgi:application --host 0.0.0.0 --port 9527 --workers 4
```

**Generated log file examples:**
```
app_hostname_pid12345_ts1630000000.log  # Process 1
app_hostname_pid12346_ts1630000000.log  # Process 2
app_hostname_pid12347_ts1630000000.log  # Process 3
app_hostname_pid12348_ts1630000000.log  # Process 4
```

## Process-Safe File Handler Details

### UnfazedRotatingFileHandler Features

```python
from unfazed.logging.handlers import UnfazedRotatingFileHandler

# Create handler
handler = UnfazedRotatingFileHandler(
    filename="myapp.log",        # Base filename
    maxBytes=10*1024*1024,       # Rotate after 10MB
    encoding="utf-8",            # File encoding
    delay=True                   # Delay file creation
)
```

#### File Naming Rules

Original filename: `myapp.log`
Actual filename: `myapp_{hostname}_pid{process_id}_ts{timestamp}.log`

For example:
```
myapp_server01_pid12345_ts1634567890.log
```

#### Log Rotation Mechanism

When log file size exceeds `maxBytes`:

1. **Close current file**: Stop writing to current file
2. **Rename archive**: Rename current file to `{name}_archived.log`
3. **Create new file**: Create file with new process-safe filename
4. **Continue writing**: Write subsequent logs to new file

```python
# Before rotation
myapp_server01_pid12345_ts1634567890.log  # Current file

# After rotation  
myapp_server01_pid12345_ts1634567890_archived.log  # Archived file
myapp_server01_pid12345_ts1634567891.log           # New file
```

## Configuration System Details

### LogCenter Configuration Management

```python
from unfazed.logging import LogCenter
from unfazed.core import Unfazed

# Create Unfazed application
unfazed = Unfazed()

# Custom log configuration
custom_config = {
    "version": 1,
    "formatters": {
        "json": {
            "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        }
    },
    "handlers": {
        "json_file": {
            "class": "unfazed.logging.handlers.UnfazedRotatingFileHandler",
            "filename": "app_json.log",
            "formatter": "json",
            "maxBytes": 5242880  # 5MB
        }
    },
    "loggers": {
        "api": {
            "handlers": ["json_file"],
            "level": "INFO"
        }
    }
}

# Create log center and setup
log_center = LogCenter(unfazed, custom_config)
log_center.setup()
```

### Default Configuration

Unfazed provides out-of-the-box default configuration:

```python
DEFAULT_LOGGING_CONFIG = {
    "formatters": {
        "_simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "_console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "_simple",
        }
    },
    "loggers": {
        "unfazed": {"level": "DEBUG", "handlers": ["_console"]},
        "uvicorn": {"level": "INFO", "handlers": ["_console"]},
        "tortoise": {"level": "INFO", "handlers": ["_console"]},
    },
    "version": 1,
}
```

### Configuration Merging Strategy

User configuration is intelligently merged with default configuration:

1. **Formatter Merging**: `formatters` section is merged, user configuration overrides items with same name
2. **Handler Merging**: `handlers` section is merged, user configuration overrides items with same name  
3. **Logger Merging**: `loggers` section is merged, user configuration overrides items with same name
4. **Other Configuration**: `version`, `disable_existing_loggers` etc. directly use user configuration

## Practical Application Scenarios

### Enterprise Application Configuration

```python
# settings.py - Production environment configuration
UNFAZED_SETTINGS = {
    "LOGGING": {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "production": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d [%(process)d:%(thread)d] - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "process": %(process)d, "thread": %(thread)d, "message": "%(message)s"}'
            }
        },
        "handlers": {
            # Application logs
            "app_file": {
                "class": "unfazed.logging.handlers.UnfazedRotatingFileHandler",
                "filename": "app.log",
                "maxBytes": 50*1024*1024,  # 50MB
                "formatter": "production",
                "encoding": "utf-8"
            },
            # Error logs
            "error_file": {
                "class": "unfazed.logging.handlers.UnfazedRotatingFileHandler", 
                "filename": "error.log",
                "maxBytes": 20*1024*1024,  # 20MB
                "formatter": "production",
                "level": "ERROR",
                "encoding": "utf-8"
            },
            # Access logs (JSON format)
            "access_file": {
                "class": "unfazed.logging.handlers.UnfazedRotatingFileHandler",
                "filename": "access.log", 
                "maxBytes": 100*1024*1024,  # 100MB
                "formatter": "json",
                "encoding": "utf-8"
            },
            # Console output
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "production",
                "level": "INFO"
            }
        },
        "loggers": {
            # Main application log
            "myapp": {
                "handlers": ["app_file", "error_file", "console"],
                "level": "INFO",
                "propagate": False
            },
            # Access log
            "myapp.access": {
                "handlers": ["access_file"],
                "level": "INFO",
                "propagate": False
            },
            # Database log
            "myapp.database": {
                "handlers": ["app_file"],
                "level": "WARNING",
                "propagate": False
            },
            # External API call log
            "myapp.external": {
                "handlers": ["app_file", "error_file"],
                "level": "INFO",
                "propagate": False
            },
            # Framework log
            "unfazed": {
                "handlers": ["app_file", "console"],
                "level": "WARNING",
                "propagate": False
            }
        }
    }
}
```
