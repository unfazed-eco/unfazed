Unfazed 日志
============

Unfazed 通过 Python 标准的 `logging.config.dictConfig` 配置日志。你在配置中提供 `LOGGING` 字典，Unfazed 会将其与合理默认值合并，使框架内部日志（`unfazed`、`uvicorn`、`tortoise`）开箱即用。若不提供任何日志配置，则直接使用默认值。

## 快速开始

在配置中添加 `LOGGING` 键以配置应用级日志：

```python
# settings.py
UNFAZED_SETTINGS = {
    "PROJECT_NAME": "myproject",
    "LOGGING": {
        "version": 1,
        "formatters": {
            "verbose": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "verbose",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "myapp": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    },
}
```

然后在代码中使用标准 Python 日志：

```python
import logging

logger = logging.getLogger("myapp")

async def my_endpoint(request):
    logger.info("Request received")
    ...
```

## 配置

`LOGGING` 配置遵循 Python 的 [dictConfig 模式](https://docs.python.org/3/library/logging.config.html#dictionary-schema-details)：

```python
"LOGGING": {
    "version": 1,                          # 必填，始终为 1
    "disable_existing_loggers": False,      # 可选
    "formatters": {
        "<name>": {
            "format": "...",
            "datefmt": "...",
        },
    },
    "filters": {
        "<name>": {
            "()": "dotted.path.to.FilterClass",
        },
    },
    "handlers": {
        "<name>": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "<formatter_name>",
            "filters": ["<filter_name>"],
            # ... 处理器特定选项
        },
    },
    "loggers": {
        "<name>": {
            "level": "DEBUG",
            "handlers": ["<handler_name>"],
            "filters": ["<filter_name>"],
            "propagate": True,
        },
    },
    "root": {
        "level": "WARNING",
        "handlers": ["<handler_name>"],
    },
}
```

### 合并规则

你的配置会与 Unfazed 的默认值**合并** —— 不会完全替换。合并规则为：

- **formatters、handlers、filters、loggers** — 你的条目与默认值并存。若你定义的键在默认值中已存在，则你的值优先。
- **其他顶层键**（如 `version`、`root`、`disable_existing_loggers`）— 保留默认值；这些键的你的值会被忽略。这确保框架内部日志始终可用。

因此，除非要修改其配置，否则无需重新声明 `unfazed` 或 `tortoise` 日志器。

## 默认配置

未提供 `LOGGING` 配置（或为空）时，Unfazed 使用以下默认值：

```python
{
    "version": 1,
    "formatters": {
        "_simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "_console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "_simple",
        },
    },
    "loggers": {
        "unfazed": {
            "level": "DEBUG",
            "handlers": ["_console"],
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["_console"],
        },
        "tortoise": {
            "level": "INFO",
            "handlers": ["_console"],
        },
    },
    "filters": {},
}
```

默认 handler 和 formatter 名称以 `_` 为前缀，避免与你自己的配置冲突。

## API 参考

### LogCenter

```python
class LogCenter:
    def __init__(self, unfazed: Unfazed, dictconfig: Dict[str, Any]) -> None
```

中央日志配置管理器。将用户配置与默认值合并，并通过 `logging.config.dictConfig` 应用。

**方法：**

- `setup() -> None`：应用合并后的日志配置。
- `merge_default(dictconfig: Dict) -> Dict`：将用户配置与默认配置合并并返回结果。

**属性：**

- `config: Dict` — 最终合并后的配置。
- `raw_dictconfig: Dict` — 用户提供的原始配置。

### LogConfig

```python
class LogConfig(BaseModel):
    version: int = 1
    formatters: Dict[str, Formatter] | None = None
    filters: Dict[str, Filter] | None = None
    handlers: Dict[str, Handler] | None = None
    loggers: Dict[str, Logger] | None = None
    root: RootLogger | None = None
    incremental: bool | None = None
    disable_existing_loggers: bool | None = None
```

在传递给 `LogCenter` 之前用于验证 `LOGGING` 配置的 Pydantic 模型。
