# Part 1: Installation and Project Creation

Welcome to the Unfazed tutorial! In this series, we will build a **student course enrollment system** step by step, covering the complete development process: project creation, data model design, API development, testing, and more.

By the end of this tutorial, you will have a working application that demonstrates all major features of the Unfazed framework.

## Environment Setup

### System Requirements

- **Python**: 3.12 or higher
- **Operating System**: Windows, macOS or Linux
- **Recommended Tool**: [uv](https://docs.astral.sh/uv/) package manager (faster dependency installation)

### Installing Unfazed

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

> **Tip**: uv is a high-performance Python package manager that is 10-100 times faster than pip.

## Creating a Project

### Using CLI Tool to Create Project

Unfazed provides a command-line tool `unfazed-cli` that can quickly create project scaffolding. See [Command](../features/command.md) for the full CLI reference.

```bash
unfazed-cli startproject -n tutorial
```

This command creates a complete project structure named `tutorial` in the current directory.

### Project Structure

After creation, you will see the following structure:

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
        ├── asgi.py                # ASGI application entry file
        ├── conftest.py            # Pytest configuration file
        ├── entry/
        │   ├── __init__.py
        │   ├── routes.py          # Root URL configuration
        │   └── settings/
        │       └── __init__.py    # Project settings (UNFAZED_SETTINGS)
        ├── logs/
        ├── Makefile
        ├── pyproject.toml
        └── static/
```

### Core Files

| File/Directory    | Description                                                                   |
| ----------------- | ----------------------------------------------------------------------------- |
| `asgi.py`         | ASGI application entry — creates the `Unfazed` instance and sets the settings module. See [Settings](../features/settings.md). |
| `entry/routes.py` | Root URL configuration — the `patterns` list that maps URL prefixes to app routes. See [Routing](../features/route.md). |
| `entry/settings/` | Project settings — contains `UNFAZED_SETTINGS` dict with all configuration. See [Settings](../features/settings.md). |
| `conftest.py`     | Pytest configuration — defines the `unfazed` fixture for testing. See [Test Client](../features/testclient.md). |
| `pyproject.toml`  | Project dependencies and tool configuration (Ruff, MyPy, Pytest).             |
| `Makefile`        | Quick commands for common tasks (run, test, format, migrate).                 |

## Starting the Project

### Install Dependencies and Run

**Step 1: Enter the backend directory**

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

# Method 2: Using uvicorn directly
uvicorn asgi:application --host 0.0.0.0 --port 9527 --reload
```

### Verifying Startup

After successful startup, you should see output similar to:

```
INFO:     Uvicorn running on http://127.0.0.1:9527 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Common Makefile Commands

The generated Makefile includes several useful shortcuts:

```bash
make run          # Start development server
make test         # Run tests with coverage
make format       # Code formatting and linting
make init-db      # Initialize database migrations
make upgrade      # Apply database migrations
make shell        # Launch interactive IPython shell
```

### Docker Deployment

For Docker-based development, use the included Docker Compose configuration:

```bash
cd tutorial/src
docker-compose up -d
docker-compose ps
```

## Next Steps

You have successfully created and started your first Unfazed project. In the next part, we will:

- Create the first application (App)
- Write a "Hello, World" API endpoint
- Understand Unfazed's route configuration

Continue to **[Part 2: Creating Applications and Hello World](part2.md)**.

---

## Troubleshooting

**Q: Port occupation error during startup**
```bash
# Check port usage
lsof -i :9527

# Start with a different port
uvicorn asgi:application --port 8000
```

**Q: Dependency installation failed**
```bash
# Clean cache and reinstall
pip cache purge
pip install --no-cache-dir unfazed
```

**Q: Python version incompatible**
```bash
# Check Python version (3.12+ required)
python --version

# Use pyenv to manage multiple Python versions if needed
```
