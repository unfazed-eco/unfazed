## 安装与创建项目


### 安装


安装 unfazed 非常简单，只需要运行以下命令即可：


```bash

pip install unfazed

```


### 创建项目

在 unfazed 安装完成后，可以使用 unfazed-cli 命令来创建一个新的项目。


```bash

unfazed-cli startproject -n tutorial

```


该命令会在当前目录下创建一个名为 tutorial 的项目。其文件结构如下：

```
├── README.md
├── changelog.md
├── deploy
├── docs
│   └── index.md
├── mkdocs.yml
└── src
    ├── Dockerfile
    ├── backend
    │   ├── Makefile
    │   ├── entry
    │   │   ├── __init__.py
    │   │   ├── asgi.py
    │   │   ├── routes.py
    │   │   └── settings
    │   ├── logs
    │   ├── manage.py
    │   ├── pyproject.toml
    │   ├── static
    └── docker-compose.yml
```


解释一下各个文件的作用：

- README.md: 项目的说明文档
- changelog.md: 项目的更新日志
- deploy: 项目的部署文件存放目录
- docs: 项目的文档存放目录
- mkdocs.yml: 项目的文档配置文件，推荐使用 [mkdocs](https://www.mkdocs.org/) 来生成文档
- src: 项目的源代码存放目录
- src/Dockerfile: unfazed 的 Dockerfile 文件（推荐使用 docker-compose 来启动项目）
- src/docker-compose.yml: 项目的 docker-compose 配置文件(推荐使用 docker-compose 来启动项目)
- src/backend: 项目的后端代码存放目录
- src/backend/Makefile: 项目的 Makefile 文件，定义了一些快捷命令用于管理项目
- src/backend/entry: 项目的入口文件存放目录
- src/backend/entry/asgi.py: 项目的 ASGI 入口文件
- src/backend/entry/routes.py: 项目的入口路由文件
- src/backend/entry/settings: 项目的配置文件存放目录
- src/backend/logs: 项目的日志存放目录
- src/backend/manage.py: 项目的命令行入口文件
- src/backend/pyproject.toml: 项目的 pyproject.toml 文件
- src/backend/static: 项目的静态文件存放目录


### 启动项目

在实际的项目开发中可以根据业务需求来定开发的方式，docker 或者 venv 做环境隔离都是不错的选择。

以下是使用 venv 的方式来启动项目：


1、安装 uv 包管理器

```bash

pip install uv

```

关于 uv 的使用可以参考 [uv](https://docs.astral.sh/uv/)


2、安装项目依赖

```bash

cd tutorial/src/backend

uv sync

```


3、启动项目

```bash

# 如果安装了 make 命令，可以直接使用 make 命令来启动项目
make run

# 否则
uvicorn asgi:application --host 127.0.0.1 --port 9527

```


正常情况下，控制台会打印出

```bash

    uvicorn asgi:application --host 0.0.0.0 --port 9527
    INFO:     Uvicorn running on http://0.0.0.0:9527 (Press CTRL+C to quit)
    INFO:     Started server process [5912]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.

```

表示项目启动成功。

