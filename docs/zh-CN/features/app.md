Unfazed 应用系统
================

Unfazed 将代码组织为**应用**（apps）—— 每个应用都是一个自包含的 Python 包，提供项目功能的一部分。每个应用通过 `BaseAppConfig` 子类注册自身，框架的 `AppCenter` 在启动时加载所有应用。这种模块化结构使大型项目易于维护，并便于共享或复用组件。

## 快速开始

### 1. 创建应用

```bash
unfazed-cli startapp -n myapp
```

这将生成一个简单的应用骨架：

```
myapp/
├── app.py
├── endpoints.py
├── models.py
├── routes.py
├── schema.py
├── serializers.py
├── settings.py
├── admin.py
└── test_all.py
```

如需更结构化的布局（包含子包），可使用 `standard` 模板：

```bash
unfazed-cli startapp -n myapp -t standard
```

### 2. 编写 AppConfig

每个应用**必须**有一个 `app.py` 文件，其中包含继承自 `BaseAppConfig` 的 `AppConfig` 类：

```python
# myapp/app.py
from unfazed.app import BaseAppConfig


class AppConfig(BaseAppConfig):
    async def ready(self) -> None:
        pass
```

### 3. 注册应用

将应用的模块路径添加到项目配置中的 `INSTALLED_APPS`：

```python
# settings.py
UNFAZED_SETTINGS = {
    "PROJECT_NAME": "myproject",
    "INSTALLED_APPS": [
        "myapp",
    ],
}
```

服务器启动时，Unfazed 将导入 `myapp`，查找 `myapp.app.AppConfig`，并调用其 `ready()` 钩子。

## 应用结构

应用是任何包含带有 `AppConfig` 类的 `app.py` 的 Python 包。除此之外，你可以自由组织文件。常规布局如下：

| 文件/目录 | 用途 |
|------------------|---------|
| `app.py` | **必需。** 包含 `AppConfig` 类。 |
| `models.py` | Tortoise ORM 模型定义。 |
| `endpoints.py` | 请求处理函数或类。 |
| `routes.py` | URL 路由声明。 |
| `serializers.py` | 基于 Pydantic 的请求/响应验证序列化器。 |
| `settings.py` | 应用级配置 —— 通过 wakeup 机制在启动时自动导入。 |
| `admin.py` | 管理面板注册。 |
| `commands/` | 自定义 CLI 命令（参见 [命令发现](#command-discovery)）。 |

## `ready()` 钩子

`ready()` 方法是一个异步生命周期钩子，在应用加载后、启动期间调用一次。用于一次性初始化，例如填充缓存、注册信号处理器或记录启动信息。

```python
# myapp/app.py
from unfazed.app import BaseAppConfig


class AppConfig(BaseAppConfig):
    async def ready(self) -> None:
        print(f"{self.name} is ready")
```

每个应用的启动顺序为：

1. 导入应用模块。
2. 导入 `app.py` 并定位 `AppConfig`。
3. 实例化 `AppConfig`。
4. 调用 `await app_config.ready()`。
5. 若存在则自动导入 `settings.py`（wakeup 机制）。
6. 将应用存入注册表。

由于 `ready()` 是异步的，你可以在其中执行异步操作（数据库查询、HTTP 调用等）。

## 命令发现

若应用包含 `commands/` 目录，Unfazed 会自动发现其中所有 Python 文件（排除以 `_` 开头的文件），并将它们注册为 CLI 命令。

```
myapp/
├── app.py
└── commands/
    ├── __init__.py
    ├── import_data.py
    └── export_data.py
```

每个命令文件必须定义一个 `Command` 类。编写自定义命令的详情请参阅 [Command](command.md) 文档。

## API 参考

### BaseAppConfig

```python
class BaseAppConfig(ABC):
    def __init__(self, unfazed: Unfazed, app_module: ModuleType) -> None
```

应用配置的抽象基类。继承此类并实现 `ready()`。

**属性：**

- `app_path -> Path`：应用目录的绝对文件系统路径。
- `name -> str`：完全限定模块名（如 `"myapp"`）。
- `label -> str`：将点替换为下划线的模块名（如 `"my_app"`）。

**方法：**

- `async ready() -> None`：*抽象。* 在启动时调用一次 —— 在此放置初始化逻辑。
- `list_command() -> List[Command]`：发现应用 `commands/` 目录中的命令文件。
- `has_models() -> bool`：若应用有 `models` 子模块则返回 `True`。
- `wakeup(filename: str) -> bool`：按名称导入子模块；成功返回 `True`，未找到返回 `False`。
- `from_entry(entry: str, unfazed: Unfazed) -> BaseAppConfig` *(classmethod)*：从点分模块路径加载应用的工厂方法。若 entry 无效则抛出 `ImportError`、`ModuleNotFoundError`、`AttributeError` 或 `TypeError`。

### AppCenter

```python
class AppCenter:
    def __init__(self, unfazed: Unfazed, installed_apps: List[str]) -> None
```

管理所有已安装应用的中央注册表。通常无需直接与之交互 —— 框架会根据 `INSTALLED_APPS` 配置在内部创建一个实例。

**方法：**

- `async setup() -> None`：加载并初始化 `installed_apps` 中的每个应用。若检测到重复的应用路径则抛出 `RuntimeError`。
- `load_app(app_path: str) -> BaseAppConfig`：加载单个应用，不调用 `ready()`。

**容器操作：**

- `app_center["myapp"]` — 按模块名获取应用（缺失时抛出 `KeyError`）。
- `"myapp" in app_center` — 检查应用是否已注册。
- `for name, config in app_center` — 遍历所有已注册应用。
- `app_center.store` — 底层的 `Dict[str, BaseAppConfig]`。
