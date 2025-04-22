Unfazed 命令
=====

Unfazed 提供方便的命令行工具，和 Django 的 command 一样，并且提供相同入口。

## 快速开始

在 app 下创建一个命令

1、在 app 文件夹下创建 `commands` 文件夹

```shell

>>> mkdir app/commands

```

2、在 `commands` 文件夹下创建一个命令文件


```shell

>>> touch app/commands/hello.py

```


3、在 `hello.py` 文件中编写命令

```python


# app/commands/hello.py

from unfazed.command import BaseCommand
from click import Option


class Command(BaseCommand):
    name = "hello"
    help = "say hello"

    def add_arguments(self):
        self.add_argument(
            Option(["--name"], help="your name", required=True)
        )

    def handle(self, name: str):
        print(f"hello {name}")


```

4、运行命令

```shell

>>> unfazed-cli hello --name unfazed
# hello unfazed

```


## 内置命令

Unfazed 内置了一些命令，用于快速开发。

### startapp

创建一个新的 app

```shell

>>> unfazed-cli startapp -n myapp

```


### runserver


启动一个开发服务器

```shell


>>> unfazed-cli runserver --host 0.0.0.0 --port 9527

```

### startproject

创建一个新的项目，该命令通过 `unfazed-cli` 调用

```shell

>>> unfazed-cli startproject -n myproject

```


### aerich

aerich 是一个 tortoise-orm 配套的数据库迁移工具，用于管理数据库迁移

提供以下命令

```shell

>>> unfazed-cli init-db  # 初始化数据库
>>> unfazed-cli migrate  # 生成迁移文件
>>> unfazed-cli upgrade  # 执行迁移
>>> unfazed-cli downgrade  # 回滚迁移
>>> unfazed-cli history  # 查看迁移历史
>>> unfazed-cli heads   # 查看迁移头
>>> unfazed-cli inspectdb  # 生成模型文件

```