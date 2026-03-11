Tortoise ORM 集成
================

Unfazed 使用 [Tortoise ORM](https://tortoise.github.io/) 作为数据库层，使用 [Aerich](https://github.com/tortoise/aerich) 进行 schema 迁移。数据库配置完全自动化 — 在 settings 中提供 `DATABASE` 配置后，Unfazed 会初始化 ORM、从已安装的 app 中发现模型，并注册迁移命令。如果未配置 `DATABASE`，则完全跳过 ORM 层。

## 快速开始

### 1. 配置数据库

```python
# entry/settings/__init__.py

UNFAZED_SETTINGS = {
    ...
    "INSTALLED_APPS": [
        "apps.blog",
    ],
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "tortoise.backends.mysql",
                "CREDENTIALS": {
                    "HOST": "localhost",
                    "PORT": 3306,
                    "USER": "root",
                    "PASSWORD": "secret",
                    "DATABASE": "mydb",
                },
            }
        }
    },
}
```

### 2. 在已安装的 app 中定义模型

在你的 app 包中创建 `models.py`。Unfazed 会自动发现：

```python
# apps/blog/models.py
from tortoise import Model, fields


class Post(Model):
    title = fields.CharField(max_length=255)
    body = fields.TextField()
    published = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "blog_post"
```

### 3. 运行迁移

```bash
# 初始化迁移目录（仅首次）
unfazed-cli init-db

# 模型变更后生成迁移
unfazed-cli migrate --name add_post

# 应用待执行的迁移
unfazed-cli upgrade
```

## 数据库配置

`DATABASE` 配置是一个由 `Database` Pydantic 模型验证的字典：

```python
UNFAZED_SETTINGS = {
    ...
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "tortoise.backends.mysql",
                "CREDENTIALS": {
                    "HOST": "localhost",
                    "PORT": 3306,
                    "USER": "root",
                    "PASSWORD": "secret",
                    "DATABASE": "mydb",
                },
            }
        },
        "DRIVER": "unfazed.db.tortoise.Driver",  # 可选，此为默认值
        "USE_TZ": True,                          # 可选
        "TIMEZONE": "Asia/Singapore",            # 可选
    },
}
```

**顶层字段：**

| 字段 | 类型 | 默认值 | 描述 |
|-------|------|---------|-------------|
| `CONNECTIONS` | `Dict[str, Connection]` | 必填 | 命名的数据库连接。 |
| `DRIVER` | `str` | `"unfazed.db.tortoise.Driver"` | 驱动类的点分路径。 |
| `APPS` | `Dict[str, AppModels]` | `None` | 显式模型分组。若省略则从已安装 app 自动构建。 |
| `ROUTERS` | `List[str]` | `None` | 多数据库场景下的数据库路由类。 |
| `USE_TZ` | `bool` | `None` | 启用时区感知的 datetime。 |
| `TIMEZONE` | `str` | `None` | 默认时区字符串（如 `"UTC"`、`"Asia/Singapore"`）。 |

### 连接引擎

每个连接需要 `ENGINE` 和 `CREDENTIALS`：

| Engine | 数据库 | 异步驱动 |
|--------|----------|-------------|
| `tortoise.backends.mysql` | MySQL / MariaDB | asyncmy |
| `tortoise.backends.sqlite` | SQLite | aiosqlite |

### MySQL 凭证

```python
"CREDENTIALS": {
    "HOST": "localhost",
    "PORT": 3306,
    "USER": "root",
    "PASSWORD": "secret",
    "DATABASE": "mydb",
    # optional
    "MIN_SIZE": 1,
    "MAX_SIZE": 10,
    "SSL": False,
    "CONNECT_TIMEOUT": 10,
    "ECHO": False,
    "CHARSET": "utf8mb4",
}
```

| 字段 | 类型 | 必填 | 描述 |
|-------|------|----------|-------------|
| `HOST` | `str` | 是 | 数据库主机。 |
| `PORT` | `int` | 是 | 数据库端口。 |
| `USER` | `str` | 是 | 用户名。 |
| `PASSWORD` | `str` | 是 | 密码。 |
| `DATABASE` | `str` | 是 | 数据库名。 |
| `MIN_SIZE` | `int` | 否 | 连接池最小大小。 |
| `MAX_SIZE` | `int` | 否 | 连接池最大大小。 |
| `SSL` | `bool` | 否 | 启用 SSL。 |
| `CONNECT_TIMEOUT` | `int` | 否 | 连接超时（秒）。 |
| `ECHO` | `bool` | 否 | 回显 SQL 语句。 |
| `CHARSET` | `str` | 否 | 字符集（如 `"utf8mb4"`）。 |

### SQLite 凭证

```python
"CREDENTIALS": {
    "FILE_PATH": "./db.sqlite3",
    # optional
    "JOURNAL_MODE": "wal",
    "JOURNAL_SIZE_LIMIT": 16384,
    "FOREIGN_KEYS": "ON",
}
```

| 字段 | 类型 | 必填 | 描述 |
|-------|------|----------|-------------|
| `FILE_PATH` | `str` | 是 | SQLite 文件路径。使用 `":memory:"` 表示内存数据库。 |
| `JOURNAL_MODE` | `str` | 否 | SQLite 日志模式。 |
| `JOURNAL_SIZE_LIMIT` | `int` | 否 | 日志大小限制（字节）。 |
| `FOREIGN_KEYS` | `str` | 否 | 启用外键约束（`"ON"` / `"OFF"`）。 |

## 自动模型发现

当**未**提供 `DATABASE.APPS`（默认情况）时，Unfazed 会在启动时自动扫描所有已安装的 app。任何包含 `models.py` 模块的 app 包都会被注册：

```python
UNFAZED_SETTINGS = {
    ...
    "INSTALLED_APPS": [
        "apps.account",  # 有 models.py → 模型被收集
        "apps.blog",     # 有 models.py → 模型被收集
        "apps.utils",    # 无 models.py  → 跳过
    ],
}
```

自动生成的配置等价于：

```python
DATABASE["APPS"] = {
    "models": {
        "MODELS": [
            "aerich.models",
            "apps.account.models",
            "apps.blog.models",
        ]
    }
}
```

`aerich.models` 始终包含在内，以支持 Aerich 内部的迁移追踪表。

如需更细粒度控制 — 例如将不同 app 路由到不同数据库 — 请显式提供 `APPS`。参见下文 [多数据库](#multiple-databases)。

## 迁移命令

配置 `DATABASE` 后，Unfazed 会自动注册基于 Aerich 的迁移命令。所有命令接受 `--location / -l`（默认 `./migrations`）指定迁移目录。

| 命令 | 描述 | 额外参数 |
|---------|-------------|-------------|
| `init-db` | 创建迁移目录并生成初始 schema。 | `--safe / -s`（默认 `True`） |
| `migrate` | 根据模型变更生成新的迁移文件。 | `--name / -n`（默认 `"update"`），`--app / -a`（默认 `"models"`） |
| `upgrade` | 应用待执行的迁移。 | `--transaction / -t`（默认 `True`） |
| `downgrade` | 回滚到指定迁移版本。 | `--version / -v`（默认 `-1`），`--delete / -d`（默认 `True`） |
| `history` | 列出所有已应用的迁移。 | — |
| `heads` | 显示可用的迁移头。 | — |
| `inspectdb` | 从现有数据库表反向生成模型定义。 | `--tables / -t`（指定要检查的表） |

### 典型工作流

```bash
# 1. 初始化迁移目录（每个项目一次）
unfazed-cli init-db

# 2. 修改模型后，生成迁移
unfazed-cli migrate --name add_published_field

# 3. 应用迁移
unfazed-cli upgrade

# 4. 查看迁移历史
unfazed-cli history

# 5. 如需回滚最后一次迁移
unfazed-cli downgrade --version -1
```

### 检查现有数据库

从已存在的表生成模型代码：

```bash
# 检查所有表
unfazed-cli inspectdb

# 检查指定表
unfazed-cli inspectdb --tables user --tables order
```

## 多数据库

若要将不同模型路由到不同数据库连接，请显式提供 `APPS`，并将 `DEFAULT_CONNECTION` 指向相应的连接别名。

### 1. 配置连接和 app 分组

```python
# entry/settings/__init__.py

UNFAZED_SETTINGS = {
    ...
    "INSTALLED_APPS": [
        "apps.account",
        "apps.analytics",
    ],
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "tortoise.backends.mysql",
                "CREDENTIALS": {
                    "HOST": "primary-db",
                    "PORT": 3306,
                    "USER": "app",
                    "PASSWORD": "secret",
                    "DATABASE": "main",
                },
            },
            "analytics": {
                "ENGINE": "tortoise.backends.mysql",
                "CREDENTIALS": {
                    "HOST": "analytics-db",
                    "PORT": 3306,
                    "USER": "app",
                    "PASSWORD": "secret",
                    "DATABASE": "analytics",
                },
            },
        },
        "APPS": {
            "models": {
                "MODELS": ["aerich.models", "apps.account.models"],
                "DEFAULT_CONNECTION": "default",
            },
            "analytics_models": {
                "MODELS": ["apps.analytics.models"],
                "DEFAULT_CONNECTION": "analytics",
            },
        },
    },
}
```

### 2. 在每个模型的 `Meta` 中设置 `app`

每个模型必须通过 `class Meta` 中的 `app = "<group_key>"` 声明所属的 app 组。该值必须与你在 `APPS` 中定义的键匹配：

```python
# apps/account/models.py
from tortoise import Model, fields


class User(Model):
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)

    class Meta:
        table = "user"
        app = "models"  # 匹配 APPS 中的 "models" 键 → 使用 "default" 连接
```

```python
# apps/analytics/models.py
from tortoise import Model, fields


class EventLog(Model):
    event = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "event_log"
        app = "analytics_models"  # 匹配 APPS 中的 "analytics_models" 键 → 使用 "analytics" 连接
```

在此配置下，`User` 的查询走 `default` 连接（primary-db），`EventLog` 的查询走 `analytics` 连接（analytics-db）。

提供 `APPS` 后，自动模型发现会被跳过。你必须自行列出所有模型模块（包括 `aerich.models`）。

## API 参考

### Database

```python
class Database(BaseModel):
    connections: Dict[str, Connection] = Field(..., alias="CONNECTIONS")
    driver: str = Field(default="unfazed.db.tortoise.Driver", alias="DRIVER")
    apps: Dict[str, AppModels] | None = Field(default=None, alias="APPS")
    routers: List[str] | None = Field(default=None, alias="ROUTERS")
    use_tz: bool | None = Field(default=None, alias="USE_TZ")
    timezone: str | None = Field(default=None, alias="TIMEZONE")
```

顶层数据库配置模型。

### Connection

```python
class Connection(BaseModel):
    engine: str = Field(..., alias="ENGINE")
    credentials: SqliteCredential | MysqlCredential = Field(..., alias="CREDENTIALS")
```

单个命名的数据库连接。

### AppModels

```python
class AppModels(BaseModel):
    models: List[str] = Field(..., alias="MODELS")
    default_connection: str = Field(default="default", alias="DEFAULT_CONNECTION")
```

将模型模块分组并映射到连接别名。

### Driver

```python
class Driver(DataBaseDriver):
    def __init__(self, unfazed: Unfazed, conf: Database) -> None
```

默认 Tortoise ORM 驱动（`unfazed.db.tortoise.Driver`）。

- `async setup() -> None`：构建 apps 配置（若未提供）、调用 `Tortoise.init()`，并加载 Aerich 命令。
- `async migrate() -> None`：调用 `Tortoise.generate_schemas()` 从模型创建表。
- `build_apps() -> Dict[str, AppModels]`：从已安装 app 自动发现模型并返回 Tortoise apps 字典。
- `list_aerich_command() -> List[Command]`：返回所有 Aerich CLI 命令的 `Command` 对象。

### ModelCenter

```python
class ModelCenter:
    def __init__(self, unfazed: Unfazed, conf: Database | None) -> None
```

管理数据库驱动生命周期的内部注册表。

- `async setup() -> None`：导入驱动类、实例化并调用 `driver.setup()`。若未配置 `DATABASE` 则不执行任何操作。
- `async migrate() -> None`：调用 `driver.migrate()`。若驱动尚未设置则抛出 `ValueError`。

### DataBaseDriver (Protocol)

```python
class DataBaseDriver(Protocol):
    async def setup(self) -> None: ...
    async def migrate(self) -> None: ...
```

自定义数据库驱动必须满足的协议。
