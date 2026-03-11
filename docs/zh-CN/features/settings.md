配置
====

Unfazed 使用 Python 模块作为配置文件。模块通过 `UNFAZED_SETTINGS_MODULE` 环境变量加载，并通过 Pydantic 模型验证。这为你提供类型安全的配置和合理的默认值。

## 快速开始

### 1. 创建配置模块

```python
# entry/settings/__init__.py

UNFAZED_SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "myproject",
    "ROOT_URLCONF": "entry.routes",
    "INSTALLED_APPS": [
        "apps.account",
        "apps.blog",
    ],
    "MIDDLEWARE": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
}
```

### 2. 将环境变量指向你的模块

```python
# asgi.py
import os
from unfazed.core import Unfazed

os.environ.setdefault("UNFAZED_SETTINGS_MODULE", "entry.settings")

application = Unfazed()
```

当实例化 `Unfazed()` 时，它会读取 `UNFAZED_SETTINGS_MODULE`，导入模块，并将 `UNFAZED_SETTINGS` 字典根据 `UnfazedSettings` Pydantic 模型进行验证。

## 内置配置

所有内置配置都在 `UNFAZED_SETTINGS` 字典中。下表列出了所有支持的键。

| 键 | 类型 | 默认值 | 说明 |
|----|------|--------|------|
| `DEBUG` | `bool` | `True` | 启用调试模式。在调试模式下，`CommonMiddleware` 会在未处理异常时渲染详细错误页面。 |
| `PROJECT_NAME` | `str` | `"Unfazed"` | 人类可读的项目名称。用作 CLI 组名。 |
| `VERSION` | `str` | `"0.0.1"` | 项目版本字符串。 |
| `ROOT_URLCONF` | `str \| None` | `None` | 根 URL 配置模块的点分路径（必须导出 `patterns` 列表）。 |
| `INSTALLED_APPS` | `List[str]` | `[]` | 应用包的点分路径。每个必须包含带有 `AppConfig` 类的 `app.py`。 |
| `MIDDLEWARE` | `List[str]` | `[]` | 中间件类的点分路径，按顺序执行。 |
| `DATABASE` | `Database \| None` | `None` | Tortoise ORM 的数据库配置。参见 [Tortoise ORM](tortoise-orm.md) 文档。 |
| `CACHE` | `Dict[str, Cache] \| None` | `None` | 命名缓存后端配置。参见 [Cache](cache.md) 文档。 |
| `LOGGING` | `Dict[str, Any] \| None` | `None` | Python `dictConfig` 风格的日志配置。与 Unfazed 默认值合并。参见 [Logging](logging.md) 文档。 |
| `LIFESPAN` | `List[str] \| None` | `None` | lifespan 类的点分路径。参见 [Lifespan](lifespan.md) 文档。 |
| `OPENAPI` | `OpenAPI \| None` | `None` | OpenAPI 文档配置。参见 [OpenAPI](openapi.md) 文档。 |
| `CORS` | `Cors \| None` | `None` | CORS 中间件配置。参见 [Middleware](middleware.md) 文档。 |
| `TRUSTED_HOST` | `TrustedHost \| None` | `None` | 可信主机中间件配置。参见 [Middleware](middleware.md) 文档。 |
| `GZIP` | `GZip \| None` | `None` | GZip 中间件配置。参见 [Middleware](middleware.md) 文档。 |

## 配置代理

Unfazed 暴露一个全局 `settings` 对象，作为配置模块的惰性、缓存代理。

```python
from unfazed.conf import settings

unfazed_settings = settings["UNFAZED_SETTINGS"]
print(unfazed_settings.PROJECT_NAME)
```

`settings` 是 `SettingsProxy` 的实例。在首次访问某个键时，它会：

1. 导入 `UNFAZED_SETTINGS_MODULE` 指向的模块。
2. 在模块命名空间中查找该键。
3. 根据注册的 Pydantic 模型验证值。
4. 缓存验证后的实例供后续访问。

也可以像字典一样使用 — 设置、删除和迭代：

```python
settings["MY_KEY"] = my_model_instance
del settings["MY_KEY"]
settings.clear()
```

## 自定义配置

应用可以使用 `@register_settings` 装饰器定义自己的配置节：

```python
# myapp/settings.py
from pydantic import BaseModel
from unfazed.conf import register_settings


@register_settings("MYAPP_SETTINGS")
class MyAppSettings(BaseModel):
    api_key: str
    timeout: int = 30
    retry: bool = True
```

然后在项目配置模块中添加对应的字典：

```python
# entry/settings/__init__.py

UNFAZED_SETTINGS = { ... }

MYAPP_SETTINGS = {
    "api_key": "sk-xxx",
    "timeout": 60,
}
```

在任意位置访问：

```python
from unfazed.conf import settings

myapp = settings["MYAPP_SETTINGS"]
print(myapp.api_key)   # "sk-xxx"
print(myapp.timeout)   # 60
print(myapp.retry)     # True（默认值）
```

`@register_settings` 装饰器将 Pydantic 模型注册到 `SettingsProxy`，以便在首次访问时验证原始字典并转换为类型化对象。若键被重复注册，会发出 `UserWarning` 并覆盖之前的注册。

## 示例：完整配置文件

以下是 `unfazed startproject` 生成的典型配置模块：

```python
import os

DEPLOY = os.getenv("DEPLOY", "dev")
PROJECT_NAME = os.getenv("PROJECT_NAME", "myproject")
SECRET = os.getenv("SECRET", "change-me")

UNFAZED_SETTINGS = {
    "DEBUG": DEPLOY != "prod",
    "PROJECT_NAME": PROJECT_NAME,
    "ROOT_URLCONF": "entry.routes",
    "INSTALLED_APPS": [],
    "MIDDLEWARE": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
    "LOGGING": {
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/unfazed.log",
            },
        },
        "loggers": {
            "common": {
                "handlers": ["default"],
                "level": "INFO",
            },
        },
    },
    "OPENAPI": {
        "servers": [
            {"url": "http://127.0.0.1:9527", "description": "Local dev"},
        ],
        "info": {
            "title": PROJECT_NAME,
            "version": "1.0.0",
            "description": f"API for {PROJECT_NAME}",
        },
        "allow_public": DEPLOY != "prod",
    },
}
```

## API 参考

### UnfazedSettings

```python
class UnfazedSettings(BaseModel)
```

验证 `UNFAZED_SETTINGS` 字典的 Pydantic 模型。参见 [内置配置](#内置配置) 表了解所有字段和默认值。

### SettingsProxy

```python
class SettingsProxy(Storage[T])
```

配置模块的惰性、缓存代理。

| 方法 / 属性 | 说明 |
|-------------|------|
| `__getitem__(key)` | 返回 `key` 对应的验证后配置对象。若键不存在则抛出 `KeyError`。 |
| `__setitem__(key, value)` | 存储预构建的配置实例。 |
| `__delitem__(key)` | 移除缓存的配置实例。 |
| `clear()` | 重置所有缓存实例**以及**已导入的配置模块引用。 |
| `register_client_cls(key, cls)` | 为给定配置键注册 Pydantic 模型类。重复注册时发出 `UserWarning`。 |
| `settingskv` | （属性）惰性导入并返回原始配置模块命名空间作为 dict。 |

### register_settings

```python
@register_settings(key: str)
class MySettings(BaseModel): ...
```

类装饰器，将 Pydantic 模型在全局 `settings` 代理下以给定 `key` 注册。
