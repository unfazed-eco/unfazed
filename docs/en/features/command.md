Unfazed Command System
=====================

Unfazed provides a powerful command-line tool system, similar to Django's management commands, supporting both synchronous and asynchronous command execution.

## System Architecture

### Core Components

Unfazed's command system is built on the Click framework, providing the following core components:

- **BaseCommand**: Base class for all commands, supporting both synchronous and asynchronous execution
- **CommandCenter**: Command management center, responsible for loading and managing commands
- **CliCommandCenter**: CLI-specific command center for handling project-level commands

## Quick Start

### Creating Custom Commands

Create a command in an app:

1. Create a `commands` folder under the app directory

```shell
mkdir app/commands
```

2. Create a command file in the `commands` folder

```shell
touch app/commands/hello.py
```

3. Write the command in the `hello.py` file

```python
# app/commands/hello.py
from unfazed.command import BaseCommand
from click import Option
import typing as t


class Command(BaseCommand):
    help_text = "Greeting command - say hello to specified person"

    def add_arguments(self) -> t.List[Option]:
        return [
            Option(
                ["--name", "-n"], 
                help="Your name", 
                required=True,
                type=str
            ),
            Option(
                ["--greeting", "-g"], 
                help="Greeting message", 
                default="Hello",
                type=str
            )
        ]

    def handle(self, **options: t.Any) -> None:
        name = options["name"]
        greeting = options["greeting"]
        print(f"{greeting}, {name}!")
```

### Async Command Example

```python
# app/commands/async_hello.py
from unfazed.command import BaseCommand
from click import Option
import typing as t
import asyncio


class Command(BaseCommand):
    help_text = "Async greeting command"

    def add_arguments(self) -> t.List[Option]:
        return [
            Option(["--name", "-n"], help="Your name", required=True),
            Option(["--delay", "-d"], help="Delay in seconds", default=1, type=int)
        ]

    async def handle(self, **options: t.Any) -> None:
        name = options["name"]
        delay = options["delay"]
        
        print(f"Preparing to greet {name}...")
        await asyncio.sleep(delay)
        print(f"Hello, {name}! (delayed {delay} seconds)")
```

4. Run the command

```shell
# Run synchronous command
unfazed-cli hello --name unfazed --greeting "Hi"
# Hi, unfazed!

# Run asynchronous command
unfazed-cli async-hello --name unfazed --delay 2
# Preparing to greet unfazed...
# Hello, unfazed! (delayed 2 seconds)
```

## Built-in Commands

Unfazed provides rich built-in commands covering project creation, app management, database migration, and more.

### Project Management Commands

#### startproject - Create New Project

Create a new Unfazed project skeleton.

```shell
# Create project
unfazed-cli startproject -n myproject

# Specify creation location
unfazed-cli startproject -n myproject -l /path/to/location
```

**Parameter Description:**
- `--project_name, -n`: Project name (required)
- `--location, -l`: Project creation location (default: current directory)

#### startapp - Create New App

Create a new app module in an existing project.

```shell
# Create standard app (recommended)
unfazed-cli startapp -n myapp

# Create simple app
unfazed-cli startapp -n myapp -t simple

# Specify creation location
unfazed-cli startapp -n myapp -l /path/to/apps
```

**Parameter Description:**
- `--app_name, -n`: App name (required)
- `--location, -l`: App creation location (default: current directory)
- `--template, -t`: Template type (`simple` or `standard`, default: `standard`)

**Template Types:**
- **simple**: Basic template with minimal files
- **standard**: Standard template with complete app structure

### Development Tool Commands

#### shell - Interactive Shell

Launch an interactive Python shell with Unfazed app context.

```shell
unfazed-cli shell
```

**Features:**
- Auto-import Unfazed app instance
- IPython support (if installed)
- Built-in asyncio support, can use `await` directly
- Preset variable: `unfazed` - current app instance

#### export-openapi - Export OpenAPI Documentation

Export the app's OpenAPI specification as a YAML file.

```shell
# Export to current directory
unfazed-cli export-openapi

# Specify export location
unfazed-cli export-openapi -l /path/to/export
```

**Parameter Description:**
- `--location, -l`: Export file location (default: current directory)

**Note:** Requires `pyyaml` dependency.

### Database Migration Commands (Aerich)

Unfazed integrates Aerich as the database migration tool for Tortoise ORM, providing complete database version management functionality.

#### init-db - Initialize Database

Initialize migration environment and create initial migration configuration.

```shell
# Initialize database migration
unfazed-cli init-db

# Specify migration file location
unfazed-cli init-db -l ./custom_migrations
```

**Parameter Description:**
- `--location, -l`: Migration files storage location (default: `./migrations`)
- `--safe, -s`: Safe mode (default: `True`)

#### migrate - Generate Migration Files

Detect model changes and generate migration files.

```shell
# Generate migration file
unfazed-cli migrate

# Specify migration name
unfazed-cli migrate -n "add_user_model"

# Specify migration file location
unfazed-cli migrate -l ./custom_migrations
```

**Parameter Description:**
- `--location, -l`: Migration files storage location (default: `./migrations`)
- `--name, -n`: Migration file name (default: `update`)

#### upgrade - Execute Migrations

Apply pending migrations to the database.

```shell
# Execute all pending migrations
unfazed-cli upgrade

# Specify migration file location
unfazed-cli upgrade -l ./custom_migrations

# Disable transaction mode
unfazed-cli upgrade -t False
```

**Parameter Description:**
- `--location, -l`: Migration files storage location (default: `./migrations`)
- `--transaction, -t`: Whether to run in transaction (default: `True`)

#### downgrade - Rollback Migrations

Rollback database to specified version.

```shell
# Rollback to previous version
unfazed-cli downgrade

# Rollback to specified version
unfazed-cli downgrade -v 20231201_01

# Delete migration files when rolling back
unfazed-cli downgrade -d True
```

**Parameter Description:**
- `--location, -l`: Migration files storage location (default: `./migrations`)
- `--version, -v`: Version to rollback to (default: `-1`, previous version)
- `--delete, -d`: Whether to delete migration files (default: `True`)

#### history - View Migration History

Display all migration history records.

```shell
# View migration history
unfazed-cli history

# Specify migration file location
unfazed-cli history -l ./custom_migrations
```

#### heads - View Migration Heads

Display current available migration head information.

```shell
# View migration heads
unfazed-cli heads

# Specify migration file location
unfazed-cli heads -l ./custom_migrations
```

#### inspectdb - Inspect Database

Generate model code from existing database.

```shell
# Inspect all tables
unfazed-cli inspectdb

# Inspect specified tables
unfazed-cli inspectdb -t users -t orders

# Specify migration file location
unfazed-cli inspectdb -l ./custom_migrations
```

**Parameter Description:**
- `--location, -l`: Migration files storage location (default: `./migrations`)
- `--tables, -t`: Table names to inspect (can specify multiple times)

### Starting Development Server

Unfazed recommends using Uvicorn as the ASGI server to run applications:

```shell
# Start development server
uvicorn asgi:application --host 0.0.0.0 --port 9527

# Enable hot reload
uvicorn asgi:application --host 0.0.0.0 --port 9527 --reload

# Or use Makefile (if project includes one)
make run
```

## Command Extensions

### Accessing Unfazed App Instance

In custom commands, you can access the app instance via `self.unfazed`:

```python
class Command(BaseCommand):
    help_text = "Display app information"

    async def handle(self, **options: t.Any) -> None:
        # Access app configuration
        print(f"App name: {self.unfazed.settings.APP_NAME}")
        
        # Access database
        if self.unfazed.settings.DATABASE:
            print(f"Database config: {self.unfazed.settings.DATABASE}")
        
        # Access app registry
        print(f"Registered apps count: {len(list(self.unfazed.app_center))}")
```

### Error Handling

The command system automatically handles exceptions. It's recommended to use appropriate error handling in commands:

```python
class Command(BaseCommand):
    help_text = "Command with error handling"

    async def handle(self, **options: t.Any) -> None:
        try:
            # Command logic
            await some_async_operation()
        except ValueError as e:
            print(f"Parameter error: {e}")
            raise  # Re-raise exception for proper exit
        except Exception as e:
            print(f"Execution failed: {e}")
            raise
```

## Advanced Usage

### Command Parameter Types

Click supports various parameter types. Here are common parameter configurations:

```python
from click import Option, Choice, Path as ClickPath, IntRange
import typing as t

class Command(BaseCommand):
    help_text = "Advanced parameter example"

    def add_arguments(self) -> t.List[Option]:
        return [
            # String choice
            Option(
                ["--mode", "-m"],
                type=Choice(["dev", "prod", "test"]),
                default="dev",
                help="Run mode"
            ),
            # File path
            Option(
                ["--config", "-c"],
                type=ClickPath(exists=True, file_okay=True, dir_okay=False),
                help="Configuration file path"
            ),
            # Number range
            Option(
                ["--workers", "-w"],
                type=IntRange(1, 20),
                default=4,
                help="Number of worker processes (1-20)"
            ),
            # Multiple values
            Option(
                ["--apps", "-a"],
                multiple=True,
                help="List of apps to process"
            ),
            # Boolean flag
            Option(
                ["--verbose", "-v"],
                is_flag=True,
                help="Verbose output"
            )
        ]
```
