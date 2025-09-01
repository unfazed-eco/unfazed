# Part 1: Installation and Project Creation

Welcome to the Unfazed tutorial! In this tutorial series, we will comprehensively learn the core features of the Unfazed framework by building a student course enrollment system. This tutorial will cover the complete development process including project creation, data model design, API development, testing, and more.

## Environment Setup

### System Requirements

- **Python**: 3.12 or higher
- **Operating System**: Windows, macOS or Linux
- **Recommended Tool**: uv package manager (faster dependency installation)

### Installing Unfazed

Installing Unfazed is very simple, we recommend using the following methods:

**Method 1: Install with pip (standard method)**

```bash
pip install unfazed
```

**Method 2: Install with uv (recommended)**

```bash
# First install uv package manager
pip install uv

# Install unfazed with uv
uv add unfazed
```

> 💡 **Tip**: [uv](https://docs.astral.sh/uv/) is a high-performance Python package manager that is 10-100 times faster than pip.

## Creating a Project

### Using CLI Tool to Create Project

Unfazed provides a powerful command-line tool `unfazed-cli` that can quickly create project scaffolding:

```bash
unfazed-cli startproject -n tutorial
```

This command will create a complete project structure named `tutorial` in the current directory.

### Detailed Project Structure

After creation, you will see the following project structure:

```
tutorial/
├── README.md                    # Project documentation
├── changelog.md                 # Version changelog
├── deploy/                      # Deployment configuration directory
├── docs/                        # Project documentation directory
│   └── index.md                 # Documentation homepage
├── mkdocs.yml                   # MkDocs documentation configuration
└── src/                         # Source code directory
    ├── Dockerfile               # Docker image build file
    ├── docker-compose.yml       # Docker Compose configuration
    └── backend/                 # Backend application directory
        ├── asgi.py              # ASGI application entry file
        ├── conftest.py          # Pytest configuration file
        ├── entry/               # Project entry configuration
        │   ├── __init__.py      # Entry module initialization
        │   ├── routes.py        # Global route configuration
        │   └── settings/        # Project configuration directory
        │       └── __init__.py  # Configuration module (contains UNFAZED_SETTINGS)
        ├── logs/                # Log files directory
        ├── Makefile             # Project management commands
        ├── pyproject.toml       # Project dependencies and tool configuration
        └── static/              # Static files directory
```

### Core Files Description

| File/Directory    | Description                                                                               |
| ----------------- | ----------------------------------------------------------------------------------------- |
| `asgi.py`         | **ASGI application entry**, defines Unfazed app instance and startup logic                |
| `entry/routes.py` | **Global route configuration**, entry point for all app routes                            |
| `entry/settings/` | **Project configuration center**, contains UNFAZED_SETTINGS and various configurations    |
| `conftest.py`     | **Pytest configuration**, defines test fixtures and test environment configuration        |
| `pyproject.toml`  | **Project configuration**, includes dependencies, tool configuration (Ruff, MyPy, Pytest) |
| `Makefile`        | **Quick commands**, encapsulates common commands like testing, formatting, running        |

## Starting the Project

### Development Environment Configuration

Unfazed supports multiple development environment configuration methods. We recommend using virtual environments for development:

**Step 1: Enter project directory**

```bash
cd tutorial/src/backend
```

**Step 2: Install project dependencies**

```bash
# Using uv (recommended)
uv sync

```

**Step 3: Start development server**

```bash
# Method 1: Using Makefile (recommended)
make run

# Method 2: Direct use of uvicorn
uvicorn asgi:application --host 0.0.0.0 --port 9527 --reload

# Method 3: Background running (production environment)
uvicorn asgi:application --host 0.0.0.0 --port 9527
```

### Verifying Project Startup

After successful startup, you will see output similar to the following in the console:

```bash
INFO:     Uvicorn running on http://127.0.0.1:9527 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Project Management Commands

Unfazed projects provide rich management commands that can be conveniently executed through Makefile:

```bash
# Run project
make run

# Run tests (including coverage)
make test

# Code formatting and checking
make format

# Database initialization and migration
make init-db

# Database upgrade
make upgrade

# Enter Python Shell
make shell
```

### Docker Deployment Method

If you prefer to use Docker for development, Unfazed also provides complete Docker support:

```bash
# Enter project root directory
cd tutorial/src

# Start using Docker Compose
docker-compose up -d

# Check running status
docker-compose ps
```

## Next Steps

Congratulations! You have successfully created and started your first Unfazed project. In the next tutorial, we will:

- Create the first application (App)
- Write "Hello, World" API
- Understand Unfazed's file organization

Let's continue to **Part 2: Creating Applications and Hello World**!

---

## 🛠️ Troubleshooting

### Common Issues

**Q: Port occupation error during startup**
```bash
# Check port occupation
lsof -i :9527

# Start with different port
uvicorn entry.asgi:application --port 8000
```

**Q: Dependency installation failed**
```bash
# Clean cache and reinstall
pip cache purge
pip install --no-cache-dir unfazed
```

**Q: Python version incompatible**
```bash
# Check Python version
python --version

# Ensure Python 3.12+
# If version is too low, please upgrade Python or use pyenv to manage multiple versions
```
