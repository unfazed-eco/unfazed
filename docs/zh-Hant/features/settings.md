Unfazed 配置系统
================

Unfazed 的配置系统是一个基于 Pydantic 的类型安全配置管理系统，提供了强大的配置验证、自动补全和错误检查功能。通过 `settings.py` 文件和配置类的结合，为项目提供了清晰、可维护的配置管理方案。

## 系统概述

### 核心特性

- **类型安全**: 基于 Pydantic 的配置验证，确保配置的类型正确性
- **模块化设计**: 支持应用级配置模块，便于大型项目的配置管理
- **自动发现**: 通过装饰器自动注册配置类
- **延迟加载**: 配置在首次访问时才加载和验证
- **缓存机制**: 配置加载后自动缓存，提高访问性能

### 核心组件

- **SettingsProxy**: 配置代理类，负责配置的加载、缓存和访问
- **register_settings**: 装饰器，用于注册配置类
- **UnfazedSettings**: 框架核心配置类
- **配置模块**: 各种功能模块的配置类

### 设计理念

Unfazed 配置系统相比 Django 有以下优势：

**Django 的使用方式**：
```python
# settings.py
FOO = 'bar'
DATABASE_NAME = 'mydb'
CACHE_TIMEOUT = 3600

# app/views.py
from django.conf import settings

print(settings.FOO)  # 无类型提示，容易出错
print(settings.DATABASE_NAME)  # 配置散乱，难以管理
```

**Unfazed 的使用方式**：
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
    FOO: str = Field(..., description="应用标识符")
    BAR: int = Field(default=100, ge=1, description="数值配置")

@register_settings("DATABASE_SETTINGS")
class DatabaseSettings(BaseModel):
    NAME: str = Field(..., description="数据库名称")
    HOST: str = Field(default="localhost", description="数据库主机")
    PORT: int = Field(default=5432, ge=1, le=65535, description="数据库端口")

# app/services.py
from unfazed.conf import settings
from .settings import AppSettings, DatabaseSettings

app_settings: AppSettings = settings["APP_SETTINGS"]      # 完整类型提示
db_settings: DatabaseSettings = settings["DATABASE_SETTINGS"]

print(app_settings.FOO)  # 类型安全，IDE 自动补全
print(db_settings.NAME)  # 配置分组，便于管理
```

### 配置优势

1. **类型安全**: Pydantic 提供完整的类型验证和转换
2. **模块化**: 配置按功能模块分组，便于管理和维护
3. **文档化**: 配置项可以添加描述和验证规则
4. **IDE 支持**: 完整的类型提示和自动补全
5. **运行时验证**: 启动时自动验证配置的正确性

## 快速开始

### 基本使用

```python
# 1. 定义配置类 (myapp/settings.py)
from pydantic import BaseModel, Field
from unfazed.conf import register_settings

@register_settings("MYAPP_SETTINGS")
class MyAppSettings(BaseModel):
    app_name: str = Field(..., description="应用名称")
    debug_mode: bool = Field(default=False, description="调试模式")
    max_connections: int = Field(default=100, ge=1, le=1000, description="最大连接数")

# 2. 配置设置 (settings.py)
MYAPP_SETTINGS = {
    "app_name": "我的应用",
    "debug_mode": True,
    "max_connections": 200
}

# 3. 使用配置 (myapp/services.py)
from unfazed.conf import settings
from .settings import MyAppSettings

def get_app_config():
    config: MyAppSettings = settings["MYAPP_SETTINGS"]
    print(f"应用名称: {config.app_name}")
    print(f"调试模式: {config.debug_mode}")
    print(f"最大连接数: {config.max_connections}")
    return config
```

### 高级配置示例

```python
# advanced_settings.py
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from unfazed.conf import register_settings

@register_settings("API_SETTINGS")
class APISettings(BaseModel):
    base_url: str = Field(..., description="API 基础 URL")
    timeout: int = Field(default=30, ge=1, le=300, description="请求超时时间(秒)")
    retry_times: int = Field(default=3, ge=0, le=10, description="重试次数")
    headers: Dict[str, str] = Field(default_factory=dict, description="默认请求头")
    allowed_hosts: List[str] = Field(default_factory=list, description="允许的主机列表")
    
    @validator('base_url')
    def validate_base_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('base_url 必须以 http:// 或 https:// 开头')
        return v

@register_settings("FEATURE_FLAGS")
class FeatureFlags(BaseModel):
    enable_caching: bool = Field(default=True, description="启用缓存")
    enable_logging: bool = Field(default=True, description="启用日志")
    enable_metrics: bool = Field(default=False, description="启用指标收集")
    experimental_features: List[str] = Field(default_factory=list, description="实验性功能列表")

# settings.py 中的配置
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

## UnfazedSettings 核心配置

`UnfazedSettings` 是 Unfazed 框架的核心配置类，包含了启动和运行应用所需的所有基础配置。

### 完整配置示例

```python
# settings.py
UNFAZED_SETTINGS = {
    # 基础配置
    "DEBUG": True,
    "PROJECT_NAME": "我的项目",
    "VERSION": "1.0.0",
    "ROOT_URLCONF": "entry.routes",
    
    # 应用和中间件
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
    
    # 生命周期管理
    "LIFESPAN": [
        "unfazed.cache.lifespan.CacheClear",
        "myapp.lifespan.DatabaseSetup",
    ],
    
    # 数据库配置
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
    
    # 缓存配置
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
    
    # OpenAPI 配置
    "OPENAPI": {
        "info": {
            "title": "我的 API",
            "version": "1.0.0",
            "description": "这是一个示例 API",
            "contact": {
                "name": "API 支持",
                "email": "support@example.com"
            }
        },
        "servers": [
            {
                "url": "http://localhost:8000",
                "description": "开发环境"
            },
            {
                "url": "https://api.example.com",
                "description": "生产环境"
            }
        ],
        "allow_public": False,  # 生产环境关闭公开访问
    },
    
    # 中间件相关配置
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
    
    # 日志配置
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

### 配置项详解

#### 基础配置

| 配置项         | 类型   | 默认值      | 说明                             |
| -------------- | ------ | ----------- | -------------------------------- |
| `DEBUG`        | `bool` | `True`      | 调试模式，影响错误信息显示和性能 |
| `PROJECT_NAME` | `str`  | `"Unfazed"` | 项目名称，用于日志标识           |
| `VERSION`      | `str`  | `"0.0.1"`   | 项目版本号                       |
| `ROOT_URLCONF` | `str`  | `None`      | 路由配置根模块                   |

#### 应用和中间件

```python
# 应用配置
INSTALLED_APPS = [
    # 内置应用
    "unfazed.contrib.admin",        # 管理界面
    "unfazed.contrib.auth",         # 认证系统
    "unfazed.contrib.session",      # 会话管理
    
    # 自定义应用
    "myapp.users",                  # 用户模块
    "myapp.orders",                 # 订单模块
    "myapp.products",               # 产品模块
]

# 中间件配置 (按执行顺序)
MIDDLEWARE = [
    "unfazed.middleware.internal.common.CommonMiddleware",       # 通用中间件
    "unfazed.middleware.internal.cors.CORSMiddleware",          # 跨域处理
    "unfazed.middleware.internal.trustedhost.TrustedHostMiddleware", # 主机验证
    "unfazed.middleware.internal.gzip.GZipMiddleware",          # 压缩响应
    "unfazed.contrib.session.middleware.SessionMiddleware",     # 会话中间件
    "myapp.middleware.AuthMiddleware",                          # 自定义认证
]
```

#### 数据库配置

```python
DATABASE = {
    "CONNECTIONS": {
        # 主数据库
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
        
        # 只读数据库
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
        
        # 缓存数据库
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

#### 缓存配置

```python
CACHE = {
    # 本地内存缓存
    "default": {
        "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
        "OPTIONS": {
            "MAX_ENTRIES": 1000,    # 最大缓存条目数
            "TIMEOUT": 300,         # 默认超时时间(秒)
            "PREFIX": "myapp:",     # 缓存键前缀
            "VERSION": 1,           # 缓存版本
        }
    },
    
    # Redis 缓存
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
    
    # Redis 集群
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

## 自定义配置

### 应用级配置

```python
# myapp/settings.py
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from unfazed.conf import register_settings

@register_settings("EMAIL_SETTINGS")
class EmailSettings(BaseModel):
    smtp_host: str = Field(..., description="SMTP 服务器地址")
    smtp_port: int = Field(default=587, ge=1, le=65535, description="SMTP 端口")
    username: str = Field(..., description="SMTP 用户名")
    password: str = Field(..., description="SMTP 密码")
    use_tls: bool = Field(default=True, description="是否使用 TLS")
    from_email: str = Field(..., description="发件人邮箱")
    
    @validator('smtp_host')
    def validate_smtp_host(cls, v):
        if not v.strip():
            raise ValueError('SMTP 主机地址不能为空')
        return v.strip()

@register_settings("PAYMENT_SETTINGS")
class PaymentSettings(BaseModel):
    provider: str = Field(..., description="支付提供商")
    api_key: str = Field(..., description="API 密钥")
    secret_key: str = Field(..., description="密钥")
    webhook_url: str = Field(..., description="回调 URL")
    test_mode: bool = Field(default=True, description="测试模式")
    supported_currencies: List[str] = Field(
        default=["CNY", "USD"], 
        description="支持的货币"
    )
    
    @validator('api_key', 'secret_key')
    def validate_keys(cls, v):
        if len(v) < 32:
            raise ValueError('密钥长度不能少于32位')
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
    "provider": "alipay",
    "api_key": "your_very_long_api_key_here_32chars",
    "secret_key": "your_very_long_secret_key_here_32chars",
    "webhook_url": "https://api.example.com/payment/webhook",
    "test_mode": False,
    "supported_currencies": ["CNY", "USD", "EUR"]
}
```

### 环境相关配置

```python
# config/settings.py
import os
from typing import Dict, Any

# 环境变量读取
def get_env(key: str, default: Any = None, cast_type: type = str):
    """从环境变量获取配置"""
    value = os.environ.get(key, default)
    if value is None:
        return None
    
    if cast_type == bool:
        return value.lower() in ('true', '1', 'yes', 'on')
    elif cast_type == list:
        return [item.strip() for item in value.split(',') if item.strip()]
    
    return cast_type(value)

# 基础配置
UNFAZED_SETTINGS = {
    "DEBUG": get_env("DEBUG", True, bool),
    "PROJECT_NAME": get_env("PROJECT_NAME", "MyApp"),
    "VERSION": get_env("VERSION", "1.0.0"),
    
    # 数据库配置
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
    
    # Redis 配置
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
    
    # 安全配置
    "CORS": {
        "allow_origins": get_env("CORS_ORIGINS", ["*"], list),
        "allow_credentials": get_env("CORS_CREDENTIALS", True, bool),
    },
    
    "TRUSTED_HOST": {
        "allowed_hosts": get_env("ALLOWED_HOSTS", ["*"], list),
    }
}

# 生产环境特殊配置
if not get_env("DEBUG", True, bool):
    UNFAZED_SETTINGS.update({
        "OPENAPI": {
            "allow_public": False,  # 生产环境关闭 OpenAPI 公开访问
        }
    })
```

通过 Unfazed 的配置系统，您可以构建出类型安全、结构清晰、易于维护的应用配置。该系统提供了从简单配置到复杂企业级配置管理的完整解决方案，确保应用在各种环境下都能正确运行。

