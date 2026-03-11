Unfazed 命令
============

Unfazed 提供基于 [Click](https://click.palletsprojects.com/) 构建的 CLI 框架。内置多个命令（项目脚手架、shell、数据库迁移等），并自动发现各应用 `commands/` 目录中的自定义命令。支持同步和异步命令处理器。

## 快速开始

### 1. 创建命令文件

在应用的 `commands/` 目录下添加 Python 文件。文件名即为 CLI 命令名（下划线会替换为连字符）。

```
myapp/
├── app.py
└── commands/
    ├── __init__.py
    └── greet.py
```

### 2. 编写命令

每个命令文件必须定义一个继承自 `BaseCommand` 的 `Command` 类：

```python
# myapp/commands/greet.py
import typing as t

from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "Print a greeting message"

    async def handle(self, **options: t.Any) -> None:
        print("Hello from Unfazed!")
```

### 3. 运行

```bash
unfazed-cli greet
# Hello from Unfazed!
```

命令会被自动发现 —— 除将应用加入 `INSTALLED_APPS` 外无需额外注册。

## 创建自定义命令

### 基础

命令是 `myapp/commands/` 下文件中的 `Command` 类。Unfazed 在启动时扫描该目录，注册所有不以 `_` 开头的 `.py` 文件。

```
myapp/commands/
├── __init__.py
├── import_data.py      # 注册为 "import-data"
├── send_report.py      # 注册为 "send-report"
└── _helpers.py         # 忽略（以 _ 开头）
```

### 添加参数

重写 `add_arguments()` 返回 Click `Option` 对象列表：

```python
# myapp/commands/import_data.py
import typing as t

from click import Option
from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "Import data from a CSV file"

    def add_arguments(self) -> t.List[Option]:
        return [
            Option(
                ["--file", "-f"],
                type=str,
                help="Path to the CSV file",
                required=True,
            ),
            Option(
                ["--dry-run"],
                is_flag=True,
                default=False,
                help="Preview without writing to the database",
            ),
        ]

    async def handle(self, **options: t.Any) -> None:
        file_path = options["file"]
        dry_run = options["dry_run"]

        if dry_run:
            print(f"[DRY RUN] Would import from {file_path}")
            return

        # read and import data ...
        print(f"Imported data from {file_path}")
```

```bash
unfazed-cli import-data --file data.csv --dry-run
# [DRY RUN] Would import from data.csv
```

### 同步与异步处理器

`handle()` 方法可以是异步或同步。Unfazed 会检测你使用的类型并相应执行：

```python
# 异步处理器
class Command(BaseCommand):
    async def handle(self, **options: t.Any) -> None:
        await some_async_work()

# 同步处理器
class Command(BaseCommand):
    def handle(self, **options: t.Any) -> None:
        some_sync_work()
```

### 访问 Unfazed 实例

每个命令都可访问 `self.unfazed`（应用实例）和 `self.app_label`（命令所属应用的标签）：

```python
class Command(BaseCommand):
    async def handle(self, **options: t.Any) -> None:
        print(f"Running in app: {self.app_label}")
        print(f"Debug mode: {self.unfazed.settings.DEBUG}")
```

## 内置命令

### `startproject` — 创建新项目

无需项目上下文即可使用（可在任意位置通过 `unfazed-cli` 运行）。

```bash
unfazed-cli startproject -n myproject
unfazed-cli startproject -n myproject -l /path/to/parent
```

| 标志 | 描述 |
|------|-------------|
| `-n`, `--project_name` | 项目名称。 |
| `-l`, `--location` | 父目录（默认为当前目录）。 |

### `startapp` — 创建新应用

在项目目录内运行：

```bash
unfazed-cli startapp -n blog
unfazed-cli startapp -n blog -t standard
```

| 标志 | 描述 |
|------|-------------|
| `-n`, `--app_name` | 应用名称（仅小写字母、数字、下划线）。 |
| `-l`, `--location` | 父目录（默认为当前目录）。 |
| `-t`, `--template` | 模板类型：`simple`（默认）或 `standard`。 |

`simple` 模板创建扁平文件（`models.py`、`endpoints.py` 等）。`standard` 模板创建子包（`models/`、`endpoints/`、`serializers/` 等）。

### `shell` — 交互式 IPython shell

启动预加载 `unfazed` 应用实例的 IPython 会话：

```bash
unfazed-cli shell
```

需要安装 `ipython`。shell 支持直接使用 `await`。

### `create-superuser` — 创建管理员超级用户

```bash
unfazed-cli create-superuser --email admin@example.com
```

| 标志 | 描述 |
|------|-------------|
| `-e`, `--email` | 超级用户邮箱。 |

生成随机密码并输出到 stdout。需要配置 `unfazed.contrib.auth`。

### `export-openapi` — 导出 OpenAPI 模式

```bash
unfazed-cli export-openapi -l ./docs
```

| 标志 | 描述 |
|------|-------------|
| `-l`, `--location` | 输出目录（默认为当前目录）。 |

将 `openapi.yaml` 写入指定目录。需要 `pyyaml` 包。

### Tortoise ORM 命令

使用 Tortoise ORM 时，会提供额外的数据库迁移命令。详情请参阅 [Tortoise ORM](tortoise-orm.md) 文档。

## 示例

### 带多个选项的数据导出命令

```python
# myapp/commands/export_users.py
import typing as t
from pathlib import Path

from click import Choice, Option
from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "Export users to a file"

    def add_arguments(self) -> t.List[Option]:
        return [
            Option(
                ["--output", "-o"],
                type=str,
                required=True,
                help="Output file path",
            ),
            Option(
                ["--format", "-f"],
                type=Choice(["csv", "json"]),
                default="csv",
                show_choices=True,
                help="Output format",
            ),
            Option(
                ["--limit"],
                type=int,
                default=100,
                help="Maximum number of records",
            ),
        ]

    async def handle(self, **options: t.Any) -> None:
        output = Path(options["output"])
        fmt = options["format"]
        limit = options["limit"]

        # query users from database ...
        print(f"Exported {limit} users to {output} ({fmt})")
```

```bash
unfazed-cli export-users -o users.json -f json --limit 500
```

### 简单的同步工具命令

```python
# myapp/commands/check_config.py
import typing as t

from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "Validate the current project configuration"

    def handle(self, **options: t.Any) -> None:
        settings = self.unfazed.settings
        print(f"Project: {settings.PROJECT_NAME}")
        print(f"Debug:   {settings.DEBUG}")
        print(f"Apps:    {len(settings.INSTALLED_APPS)} installed")
        print("Configuration OK")
```

```bash
unfazed-cli check-config
# Project: myproject
# Debug:   True
# Apps:    3 installed
# Configuration OK
```

## API 参考

### BaseCommand

```python
class BaseCommand(click.Command, ABC):
    def __init__(self, unfazed: Unfazed, name: str, app_label: str, ...) -> None
```

所有命令的抽象基类。继承自 Click 的 `Command`。

**属性：**

- `help_text: str` — `--help` 显示的默认帮助文本。
- `unfazed: Unfazed` — 应用实例。
- `app_label: str` — 命令所属应用的标签。

**方法：**

- `add_arguments() -> List[click.Option]`：重写以声明 CLI 选项。默认返回 `[]`。
- `handle(**options: Any) -> Any`：*抽象。* 命令逻辑。可为 `async def` 或 `def`。

### CommandCenter

```python
class CommandCenter(click.Group):
    def __init__(self, unfazed: Unfazed, app_center: AppCenter, name: str) -> None
```

管理所有项目级命令。加载内部命令（startapp、shell、create-superuser、export-openapi）及每个已安装应用的命令。

**方法：**

- `async setup() -> None`：发现并加载所有命令。
- `load_command(command: Command) -> None`：将单个命令加载到组中。若类不是 `BaseCommand` 子类则抛出 `TypeError`。
- `list_internal_command() -> List[Command]`：返回内部框架命令（不含 `startproject`）。

### CliCommandCenter

```python
class CliCommandCenter(click.Group):
    def __init__(self, unfazed: Unfazed) -> None
```

在项目上下文外使用的轻量命令组。仅加载 `startproject` 命令。

**方法：**

- `setup() -> None`：加载仅 CLI 命令。
- `list_cli_command() -> List[Command]`：返回 CLI 命令列表。
