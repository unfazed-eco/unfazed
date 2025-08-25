# 第一部分：安装与创建项目

欢迎来到 Unfazed 教程！在这个系列教程中，我们将通过构建一个学生选课系统，全面学习 Unfazed 框架的核心功能。本教程将涵盖项目创建、数据模型设计、API 开发、测试等完整的开发流程。

## 环境准备

### 系统要求

- **Python**: 3.12 或更高版本
- **操作系统**: Windows、macOS 或 Linux
- **推荐工具**: uv 包管理器（更快的依赖安装）

### 安装 Unfazed

安装 Unfazed 非常简单，推荐使用以下方式：

**方式一：使用 pip 安装（标准方式）**

```bash
pip install unfazed
```

**方式二：使用 uv 安装（推荐）**

```bash
# 先安装 uv 包管理器
pip install uv

# 使用 uv 安装 unfazed
uv add unfazed
```

> 💡 **提示**: [uv](https://docs.astral.sh/uv/) 是一个高性能的 Python 包管理器，安装速度比 pip 快 10-100 倍。

## 创建项目

### 使用 CLI 工具创建项目

Unfazed 提供了强大的命令行工具 `unfazed-cli`，可以快速创建项目脚手架：

```bash
unfazed-cli startproject -n tutorial
```

这个命令会在当前目录下创建一个名为 `tutorial` 的完整项目结构。

### 项目结构详解

创建完成后，你会看到以下项目结构：

```
tutorial/
├── README.md                    # 项目说明文档
├── changelog.md                 # 版本更新日志
├── deploy/                      # 部署配置目录
├── docs/                        # 项目文档目录
│   └── index.md                 # 文档主页
├── mkdocs.yml                   # MkDocs 文档配置
└── src/                         # 源代码目录
    ├── Dockerfile               # Docker 镜像构建文件
    ├── docker-compose.yml       # Docker Compose 配置
    └── backend/                 # 后端应用目录
        ├── asgi.py              # ASGI 应用入口文件
        ├── conftest.py          # Pytest 配置文件
        ├── entry/               # 项目入口配置
        │   ├── __init__.py      # 入口模块初始化
        │   ├── routes.py        # 全局路由配置
        │   └── settings/        # 项目配置目录
        │       └── __init__.py  # 配置模块（包含 UNFAZED_SETTINGS）
        ├── logs/                # 日志文件目录
        ├── Makefile             # 项目管理命令
        ├── pyproject.toml       # 项目依赖和工具配置
        └── static/              # 静态文件目录
```

### 核心文件说明

| 文件/目录         | 作用说明                                               |
| ----------------- | ------------------------------------------------------ |
| `asgi.py`         | **ASGI 应用入口**，定义 Unfazed 应用实例和启动逻辑     |
| `entry/routes.py` | **全局路由配置**，所有应用路由的汇总入口               |
| `entry/settings/` | **项目配置中心**，包含 UNFAZED_SETTINGS 和各项配置     |
| `conftest.py`     | **Pytest 配置**，定义测试夹具和测试环境配置            |
| `pyproject.toml`  | **项目配置**，包含依赖、工具配置（Ruff、MyPy、Pytest） |
| `Makefile`        | **快捷命令**，封装测试、格式化、运行等常用命令         |

## 启动项目

### 开发环境配置

Unfazed 支持多种开发环境配置方式，推荐使用虚拟环境进行开发：

**步骤 1：进入项目目录**

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
# 方式一：使用 Makefile（推荐）
make run

# 方式二：直接使用 uvicorn
uvicorn asgi:application --host 0.0.0.0 --port 9527 --reload

# 方式三：后台运行（生产环境）
uvicorn asgi:application --host 0.0.0.0 --port 9527
```

### 验证项目启动

启动成功后，你会在控制台看到类似以下输出：

```bash
INFO:     Uvicorn running on http://127.0.0.1:9527 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 项目管理命令

Unfazed 项目提供了丰富的管理命令，通过 Makefile 可以方便地执行：

```bash
# 运行项目
make run

# 运行测试（包含覆盖率）
make test

# 代码格式化和检查
make format

# 数据库初始化和迁移
make init-db

# 数据库升级
make upgrade

# 进入 Python Shell
make shell
```

### Docker 部署方式

如果你喜欢使用 Docker 进行开发，Unfazed 也提供了完整的 Docker 支持：

```bash
# 进入项目根目录
cd tutorial/src

# 使用 Docker Compose 启动
docker-compose up -d

# 查看运行状态
docker-compose ps
```

## 下一步

恭喜！你已经成功创建并启动了第一个 Unfazed 项目。在下一个教程中，我们将：

- 创建第一个应用（App）
- 编写 "Hello, World" API
- 了解 Unfazed 的文件组织形式

让我们继续前往 **第二部分：创建应用与 Hello World**！

---

## 🛠️ 故障排除

### 常见问题

**Q: 启动时出现端口占用错误**
```bash
# 查看端口占用
lsof -i :9527

# 更换端口启动
uvicorn entry.asgi:application --port 8000
```

**Q: 依赖安装失败**
```bash
# 清理缓存重新安装
pip cache purge
pip install --no-cache-dir unfazed
```

**Q: Python 版本不兼容**
```bash
# 检查 Python 版本
python --version

# 确保使用 Python 3.12+
# 如果版本过低，请升级 Python 或使用 pyenv 管理多版本
```

