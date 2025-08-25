Unfazed 日志系统
======

Unfazed 提供了专为生产环境设计的日志系统，解决了多进程 Web 应用的日志安全问题，并提供了灵活的配置管理机制。

## 系统概述

### 核心组件

- **LogCenter**: 日志配置管理中心，负责配置合并和初始化
- **UnfazedRotatingFileHandler**: 进程安全的日志文件处理器，支持日志轮转
- **默认配置**: 为常见场景提供开箱即用的日志配置

### 主要特性

1. **进程安全**: 每个进程创建独立的日志文件，避免多进程写入冲突
2. **自动轮转**: 基于文件大小的智能日志轮转机制
3. **配置合并**: 自动将用户配置与默认配置合并
4. **灵活格式**: 支持自定义日志格式和多种输出方式

## 多进程安全问题

### 问题背景

在 Python 中，`logging` 模块是线程安全的，但不是进程安全的。当 Web 应用使用 `uvicorn`、`gunicorn` 等多进程部署方式时，多个进程同时写入同一个日志文件会导致：

- **数据竞争**: 文件写入冲突，导致日志内容混乱或丢失
- **文件锁定**: 进程间争抢文件锁，影响性能
- **日志损坏**: 并发写入可能导致日志文件格式错误

> 参考：[Python Logging Thread Safety](https://docs.python.org/3/library/logging.html#thread-safety)

### Unfazed 解决方案

Unfazed 通过为每个进程创建独立的日志文件来解决这个问题：

```
应用进程 1 → unfazed_hostname_pid12345_ts1630000000.log
应用进程 2 → unfazed_hostname_pid12346_ts1630000000.log
应用进程 3 → unfazed_hostname_pid12347_ts1630000000.log
```

## 快速开始

### 1. 基础配置

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

### 2. 应用程序中使用

```python
import logging
from unfazed.http import HttpRequest, JsonResponse

# 获取日志记录器
logger = logging.getLogger("myapp")

async def user_login(request: HttpRequest) -> JsonResponse:
    """用户登录端点"""

    # 记录请求信息
    logger.info(f"用户登录请求: IP={request.client.host}")
    
    # 业务逻辑
    username = request.json.get("username")
    password = request.json.get("password")
    
    if not username or not password:
        logger.warning(f"登录参数缺失: username={username}")
        return JsonResponse({"error": "用户名和密码不能为空"}, status_code=400)
    
    # 模拟身份验证
    user = await authenticate_user(username, password)
    
    if user:
        logger.info(f"用户登录成功: user_id={user.id}, username={username}")
        return JsonResponse({"message": "登录成功", "user_id": user.id})
    else:
        logger.warning(f"用户登录失败: username={username}, reason=invalid_credentials")
        return JsonResponse({"error": "用户名或密码错误"}, status_code=401)

async def authenticate_user(username: str, password: str):
    """模拟用户身份验证"""
    # 实际的身份验证逻辑
    return None
```

### 3. 启动应用

```bash
# 单进程启动
uvicorn asgi:application --host 0.0.0.0 --port 9527

# 多进程启动 
uvicorn asgi:application --host 0.0.0.0 --port 9527 --workers 4
```

**生成的日志文件示例:**
```
app_hostname_pid12345_ts1630000000.log  # 进程 1
app_hostname_pid12346_ts1630000000.log  # 进程 2
app_hostname_pid12347_ts1630000000.log  # 进程 3
app_hostname_pid12348_ts1630000000.log  # 进程 4
```

## 进程安全文件处理器详解

### UnfazedRotatingFileHandler 特性

```python
from unfazed.logging.handlers import UnfazedRotatingFileHandler

# 创建处理器
handler = UnfazedRotatingFileHandler(
    filename="myapp.log",        # 基础文件名
    maxBytes=10*1024*1024,       # 10MB 后轮转
    encoding="utf-8",            # 文件编码
    delay=True                   # 延迟创建文件
)
```

#### 文件命名规则

原始文件名: `myapp.log`
实际文件名: `myapp_{hostname}_pid{process_id}_ts{timestamp}.log`

例如:
```
myapp_server01_pid12345_ts1634567890.log
```

#### 日志轮转机制

当日志文件大小超过 `maxBytes` 时：

1. **关闭当前文件**: 停止向当前文件写入
2. **重命名归档**: 将当前文件重命名为 `{name}_archived.log`
3. **创建新文件**: 使用新的进程安全文件名创建文件
4. **继续写入**: 向新文件写入后续日志

```python
# 轮转前
myapp_server01_pid12345_ts1634567890.log  # 当前文件

# 轮转后  
myapp_server01_pid12345_ts1634567890_archived.log  # 归档文件
myapp_server01_pid12345_ts1634567891.log           # 新文件
```

## 配置系统详解

### LogCenter 配置管理

```python
from unfazed.logging import LogCenter
from unfazed.core import Unfazed

# 创建 Unfazed 应用
unfazed = Unfazed()

# 自定义日志配置
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

# 创建日志中心并设置
log_center = LogCenter(unfazed, custom_config)
log_center.setup()
```

### 默认配置

Unfazed 提供了开箱即用的默认配置：

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

### 配置合并策略

用户配置会与默认配置智能合并：

1. **格式化器合并**: `formatters` 部分会合并，用户配置覆盖同名项
2. **处理器合并**: `handlers` 部分会合并，用户配置覆盖同名项  
3. **记录器合并**: `loggers` 部分会合并，用户配置覆盖同名项
4. **其他配置**: `version`、`disable_existing_loggers` 等直接使用用户配置

## 实际应用场景

### 企业级应用配置

```python
# settings.py - 生产环境配置
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
            # 应用日志
            "app_file": {
                "class": "unfazed.logging.handlers.UnfazedRotatingFileHandler",
                "filename": "app.log",
                "maxBytes": 50*1024*1024,  # 50MB
                "formatter": "production",
                "encoding": "utf-8"
            },
            # 错误日志
            "error_file": {
                "class": "unfazed.logging.handlers.UnfazedRotatingFileHandler", 
                "filename": "error.log",
                "maxBytes": 20*1024*1024,  # 20MB
                "formatter": "production",
                "level": "ERROR",
                "encoding": "utf-8"
            },
            # 访问日志 (JSON 格式)
            "access_file": {
                "class": "unfazed.logging.handlers.UnfazedRotatingFileHandler",
                "filename": "access.log", 
                "maxBytes": 100*1024*1024,  # 100MB
                "formatter": "json",
                "encoding": "utf-8"
            },
            # 控制台输出
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "production",
                "level": "INFO"
            }
        },
        "loggers": {
            # 应用主日志
            "myapp": {
                "handlers": ["app_file", "error_file", "console"],
                "level": "INFO",
                "propagate": False
            },
            # 访问日志
            "myapp.access": {
                "handlers": ["access_file"],
                "level": "INFO",
                "propagate": False
            },
            # 数据库日志
            "myapp.database": {
                "handlers": ["app_file"],
                "level": "WARNING",
                "propagate": False
            },
            # 外部 API 调用日志
            "myapp.external": {
                "handlers": ["app_file", "error_file"],
                "level": "INFO",
                "propagate": False
            },
            # 框架日志
            "unfazed": {
                "handlers": ["app_file", "console"],
                "level": "WARNING",
                "propagate": False
            }
        }
    }
}
```
