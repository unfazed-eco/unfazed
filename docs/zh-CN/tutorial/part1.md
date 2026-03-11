# 第一部分：安装与项目创建

欢迎来到 Unfazed 教程！在本系列中，我们将逐步构建一个**学生选课系统**，涵盖完整的开发流程：项目创建、数据模型设计、API 开发、测试等。

完成本教程后，你将拥有一个可运行的应用，展示 Unfazed 框架的所有主要功能。

## 环境配置

### 系统要求

- **Python**：3.12 或更高版本
- **操作系统**：Windows、macOS 或 Linux
- **推荐工具**：[uv](https://docs.astral.sh/uv/) 包管理器（依赖安装更快）

### 安装 Unfazed

**方式一：使用 pip 安装（标准方式）**

```bash
pip install unfazed
```

**方式二：使用 uv 安装（推荐）**

```bash
# 首先安装 uv 包管理器
pip install uv

# 使用 uv 安装 unfazed
uv add unfazed
```

> **提示**：uv 是一款高性能 Python 包管理器，速度比 pip 快 10–100 倍。

## 创建项目

### 使用 CLI 工具创建项目

Unfazed 提供命令行工具 `unfazed-cli`，可快速创建项目脚手架。完整 CLI 参考见 [Command](../features/command.md)。

```bash
unfazed-cli startproject -n tutorial
```

该命令会在当前目录下创建一个名为 `tutorial` 的完整项目结构。

### 项目结构

创建完成后，你将看到以下结构：

```
tutorial/
├── README.md
├── changelog.md
├── deploy/
├── docs/
│   └── index.md
├── mkdocs.yml
└── src/
    ├── Dockerfile
    ├── docker-compose.yml
    └── backend/
        ├── asgi.py                # ASGI 应用入口文件
        ├── conftest.py            # Pytest 配置文件
        ├── entry/
        │   ├── __init__.py
        │   ├── routes.py          # 根 URL 配置
        │   └── settings/
        │       └── __init__.py    # 项目设置 (UNFAZED_SETTINGS)
        ├── logs/
        ├── Makefile
        ├── pyproject.toml
        └── static/
```

### 核心文件

| 文件/目录       | 说明                                                                   |
| --------------- | ---------------------------------------------------------------------- |
| `asgi.py`       | ASGI 应用入口 — 创建 `Unfazed` 实例并设置 settings 模块。见 [Settings](../features/settings.md)。 |
| `entry/routes.py` | 根 URL 配置 — 将 URL 前缀映射到应用路由的 `patterns` 列表。见 [Routing](../features/route.md)。 |
| `entry/settings/` | 项目设置 — 包含所有配置的 `UNFAZED_SETTINGS` 字典。见 [Settings](../features/settings.md)。 |
| `conftest.py`   | Pytest 配置 — 定义用于测试的 `unfazed` fixture。见 [Test Client](../features/testclient.md)。 |
| `pyproject.toml` | 项目依赖与工具配置（Ruff、MyPy、Pytest）。                             |
| `Makefile`      | 常用任务的快捷命令（run、test、format、migrate）。                     |

## 启动项目

### 安装依赖并运行

**步骤 1：进入 backend 目录**

```bash
cd tutorial/src/backend
```

**步骤 2：安装项目依赖**

```bash
# 使用 uv（推荐）
uv sync
```

**步骤 3：启动开发服务器**

```bash
# 方式 1：使用 Makefile（推荐）
make run

# 方式 2：直接使用 uvicorn
uvicorn asgi:application --host 0.0.0.0 --port 9527 --reload
```

### 验证启动

启动成功后，你会看到类似输出：

```
INFO:     Uvicorn running on http://127.0.0.1:9527 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 常用 Makefile 命令

生成的 Makefile 包含多个实用快捷命令：

```bash
make run          # 启动开发服务器
make test         # 运行测试并生成覆盖率
make format       # 代码格式化与检查
make init-db      # 初始化数据库迁移
make upgrade      # 应用数据库迁移
make shell        # 启动交互式 IPython shell
```

### Docker 部署

若使用 Docker 进行开发，可使用项目自带的 Docker Compose 配置：

```bash
cd tutorial/src
docker-compose up -d
docker-compose ps
```

## 下一步

你已经成功创建并启动了第一个 Unfazed 项目。下一部分我们将：

- 创建第一个应用（App）
- 编写 "Hello, World" API endpoint
- 理解 Unfazed 的路由配置

继续阅读 **[第二部分：创建应用与 Hello World](part2.md)**。

---

## 故障排除

**问：启动时端口被占用**
```bash
# 检查端口占用
lsof -i :9527

# 使用其他端口启动
uvicorn asgi:application --port 8000
```

**问：依赖安装失败**
```bash
# 清理缓存并重新安装
pip cache purge
pip install --no-cache-dir unfazed
```

**问：Python 版本不兼容**
```bash
# 检查 Python 版本（需要 3.12+）
python --version

# 如需要，可使用 pyenv 管理多个 Python 版本
```
