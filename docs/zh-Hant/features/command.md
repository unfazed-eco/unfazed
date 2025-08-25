Unfazed 命令系统
=====

Unfazed 提供强大的命令行工具系统，类似 Django 的 management commands，支持同步和异步命令执行。

## 命令系统架构

Unfazed 的命令系统基于 Click 框架构建，提供以下核心组件：

- **BaseCommand**: 所有命令的基类，支持同步和异步执行
- **CommandCenter**: 命令管理中心，负责加载和管理命令
- **CliCommandCenter**: CLI 专用命令中心，用于处理项目级别的命令

## 快速开始

### 创建自定义命令

在 app 下创建一个命令：

1、在 app 文件夹下创建 `commands` 文件夹

```shell
mkdir app/commands
```

2、在 `commands` 文件夹下创建一个命令文件

```shell
touch app/commands/hello.py
```

3、在 `hello.py` 文件中编写命令

```python
# app/commands/hello.py
from unfazed.command import BaseCommand
from click import Option
import typing as t


class Command(BaseCommand):
    help_text = "打招呼命令 - 向指定的人问好"

    def add_arguments(self) -> t.List[Option]:
        return [
            Option(
                ["--name", "-n"], 
                help="你的名字", 
                required=True,
                type=str
            ),
            Option(
                ["--greeting", "-g"], 
                help="问候语", 
                default="Hello",
                type=str
            )
        ]

    def handle(self, **options: t.Any) -> None:
        name = options["name"]
        greeting = options["greeting"]
        print(f"{greeting}, {name}!")
```

### 异步命令示例

```python
# app/commands/async_hello.py
from unfazed.command import BaseCommand
from click import Option
import typing as t
import asyncio


class Command(BaseCommand):
    help_text = "异步问候命令"

    def add_arguments(self) -> t.List[Option]:
        return [
            Option(["--name", "-n"], help="你的名字", required=True),
            Option(["--delay", "-d"], help="延迟秒数", default=1, type=int)
        ]

    async def handle(self, **options: t.Any) -> None:
        name = options["name"]
        delay = options["delay"]
        
        print(f"正在准备问候 {name}...")
        await asyncio.sleep(delay)
        print(f"Hello, {name}! (延迟了 {delay} 秒)")
```

4、运行命令

```shell
# 运行同步命令
unfazed-cli hello --name unfazed --greeting "你好"
# 你好, unfazed!

# 运行异步命令
unfazed-cli async-hello --name unfazed --delay 2
# 正在准备问候 unfazed...
# Hello, unfazed! (延迟了 2 秒)
```


## 内置命令

Unfazed 提供了丰富的内置命令，涵盖项目创建、应用管理、数据库迁移等功能。

### 项目管理命令

#### startproject - 创建新项目

创建一个新的 Unfazed 项目骨架。

```shell
# 创建项目
unfazed-cli startproject -n myproject

# 指定创建位置
unfazed-cli startproject -n myproject -l /path/to/location
```

**参数说明：**
- `--project_name, -n`: 项目名称（必需）
- `--location, -l`: 项目创建位置（默认为当前目录）

#### startapp - 创建新应用

在现有项目中创建新的应用模块。

```shell
# 创建标准应用（推荐）
unfazed-cli startapp -n myapp

# 创建简单应用
unfazed-cli startapp -n myapp -t simple

# 指定创建位置
unfazed-cli startapp -n myapp -l /path/to/apps
```

**参数说明：**
- `--app_name, -n`: 应用名称（必需）
- `--location, -l`: 应用创建位置（默认为当前目录）
- `--template, -t`: 模板类型（`simple` 或 `standard`，默认为 `standard`）

**模板类型：**
- **simple**: 基础模板，包含最少的文件
- **standard**: 标准模板，包含完整的应用结构

### 开发工具命令

#### shell - 交互式 Shell

启动带有 Unfazed 应用上下文的交互式 Python Shell。

```shell
unfazed-cli shell
```

**功能特性：**
- 自动导入 Unfazed 应用实例
- 支持 IPython（如果已安装）
- 内置 asyncio 支持，可直接使用 `await`
- 预设变量：`unfazed` - 当前应用实例

#### export-openapi - 导出 OpenAPI 文档

将应用的 OpenAPI 规范导出为 YAML 文件。

```shell
# 导出到当前目录
unfazed-cli export-openapi

# 指定导出位置
unfazed-cli export-openapi -l /path/to/export
```

**参数说明：**
- `--location, -l`: 导出文件位置（默认为当前目录）

**注意：** 需要安装 `pyyaml` 依赖。

### 数据库迁移命令（Aerich）

Unfazed 集成了 Aerich 作为 Tortoise ORM 的数据库迁移工具，提供完整的数据库版本管理功能。

#### init-db - 初始化数据库

初始化迁移环境并创建初始迁移配置。

```shell
# 初始化数据库迁移
unfazed-cli init-db

# 指定迁移文件位置
unfazed-cli init-db -l ./custom_migrations
```

**参数说明：**
- `--location, -l`: 迁移文件存储位置（默认为 `./migrations`）
- `--safe, -s`: 安全模式（默认为 `True`）

#### migrate - 生成迁移文件

检测模型变化并生成迁移文件。

```shell
# 生成迁移文件
unfazed-cli migrate

# 指定迁移名称
unfazed-cli migrate -n "add_user_model"

# 指定迁移文件位置
unfazed-cli migrate -l ./custom_migrations
```

**参数说明：**
- `--location, -l`: 迁移文件存储位置（默认为 `./migrations`）
- `--name, -n`: 迁移文件名称（默认为 `update`）

#### upgrade - 执行迁移

应用挂起的迁移到数据库。

```shell
# 执行所有挂起的迁移
unfazed-cli upgrade

# 指定迁移文件位置
unfazed-cli upgrade -l ./custom_migrations

# 禁用事务模式
unfazed-cli upgrade -t False
```

**参数说明：**
- `--location, -l`: 迁移文件存储位置（默认为 `./migrations`）
- `--transaction, -t`: 是否在事务中运行（默认为 `True`）

#### downgrade - 回滚迁移

回滚数据库到指定版本。

```shell
# 回滚到上一个版本
unfazed-cli downgrade

# 回滚到指定版本
unfazed-cli downgrade -v 20231201_01

# 回滚时删除迁移文件
unfazed-cli downgrade -d True
```

**参数说明：**
- `--location, -l`: 迁移文件存储位置（默认为 `./migrations`）
- `--version, -v`: 要回滚到的版本（默认为 `-1`，即上一版本）
- `--delete, -d`: 是否删除迁移文件（默认为 `True`）

#### history - 查看迁移历史

显示所有迁移历史记录。

```shell
# 查看迁移历史
unfazed-cli history

# 指定迁移文件位置
unfazed-cli history -l ./custom_migrations
```

#### heads - 查看迁移头

显示当前可用的迁移头信息。

```shell
# 查看迁移头
unfazed-cli heads

# 指定迁移文件位置
unfazed-cli heads -l ./custom_migrations
```

#### inspectdb - 检查数据库

从现有数据库生成模型代码。

```shell
# 检查所有表
unfazed-cli inspectdb

# 检查指定表
unfazed-cli inspectdb -t users -t orders

# 指定迁移文件位置
unfazed-cli inspectdb -l ./custom_migrations
```

**参数说明：**
- `--location, -l`: 迁移文件存储位置（默认为 `./migrations`）
- `--tables, -t`: 要检查的表名（可多次指定）

### 启动开发服务器

Unfazed 推荐使用 Uvicorn 作为 ASGI 服务器来运行应用：

```shell
# 启动开发服务器
uvicorn asgi:application --host 0.0.0.0 --port 9527

# 启用热重载
uvicorn asgi:application --host 0.0.0.0 --port 9527 --reload

# 或者使用 Makefile（如果项目包含）
make run
```

## 命令扩展

### 访问 Unfazed 应用实例

在自定义命令中，可以通过 `self.unfazed` 访问应用实例：

```python
class Command(BaseCommand):
    help_text = "展示应用信息"

    async def handle(self, **options: t.Any) -> None:
        # 访问应用配置
        print(f"应用名称: {self.unfazed.settings.APP_NAME}")
        
        # 访问数据库
        if self.unfazed.settings.DATABASE:
            print(f"数据库配置: {self.unfazed.settings.DATABASE}")
        
        # 访问应用注册中心
        print(f"已注册应用数量: {len(list(self.unfazed.app_center))}")
```

### 错误处理

命令系统会自动处理异常，建议在命令中使用适当的错误处理：

```python
class Command(BaseCommand):
    help_text = "带错误处理的命令"

    async def handle(self, **options: t.Any) -> None:
        try:
            # 命令逻辑
            await some_async_operation()
        except ValueError as e:
            print(f"参数错误: {e}")
            raise  # 重新抛出异常以正确退出
        except Exception as e:
            print(f"执行失败: {e}")
            raise
```

## 高级用法

### 命令参数类型

Click 支持多种参数类型，以下是常用的参数配置：

```python
from click import Option, Choice, Path as ClickPath, IntRange
import typing as t

class Command(BaseCommand):
    help_text = "高级参数示例"

    def add_arguments(self) -> t.List[Option]:
        return [
            # 字符串选择
            Option(
                ["--mode", "-m"],
                type=Choice(["dev", "prod", "test"]),
                default="dev",
                help="运行模式"
            ),
            # 文件路径
            Option(
                ["--config", "-c"],
                type=ClickPath(exists=True, file_okay=True, dir_okay=False),
                help="配置文件路径"
            ),
            # 数字范围
            Option(
                ["--workers", "-w"],
                type=IntRange(1, 20),
                default=4,
                help="工作进程数量 (1-20)"
            ),
            # 多值选项
            Option(
                ["--apps", "-a"],
                multiple=True,
                help="要处理的应用列表"
            ),
            # 布尔标志
            Option(
                ["--verbose", "-v"],
                is_flag=True,
                help="详细输出"
            )
        ]
```

