Tortoise ORM Integration
========================

Unfazed uses [Tortoise ORM](https://tortoise.github.io/) as its database layer and [Aerich](https://github.com/tortoise/aerich) for schema migrations. Database setup is fully automatic — provide a `DATABASE` configuration in settings and Unfazed initialises the ORM, discovers models from installed apps, and registers migration commands. If no `DATABASE` is configured, the ORM layer is skipped entirely.

## Quick Start

### 1. Configure the database

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

### 2. Define models in an installed app

Create a `models.py` in your app package. Unfazed discovers it automatically:

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

### 3. Run migrations

```bash
# Initialise the migration directory (first time only)
unfazed-cli init-db

# Generate a migration after model changes
unfazed-cli migrate --name add_post

# Apply pending migrations
unfazed-cli upgrade
```

## Database Configuration

The `DATABASE` setting is a dict validated by the `Database` Pydantic model:

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
        "DRIVER": "unfazed.db.tortoise.Driver",  # optional, this is the default
        "USE_TZ": True,                          # optional
        "TIMEZONE": "Asia/Singapore",            # optional
    },
}
```

**Top-level fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `CONNECTIONS` | `Dict[str, Connection]` | required | Named database connections. |
| `DRIVER` | `str` | `"unfazed.db.tortoise.Driver"` | Dotted path to the driver class. |
| `APPS` | `Dict[str, AppModels]` | `None` | Explicit model grouping. Auto-built from installed apps if omitted. |
| `ROUTERS` | `List[str]` | `None` | Database router classes for multi-database setups. |
| `USE_TZ` | `bool` | `None` | Enable timezone-aware datetimes. |
| `TIMEZONE` | `str` | `None` | Default timezone string (e.g. `"UTC"`, `"Asia/Singapore"`). |

### Connection Engines

Each connection requires an `ENGINE` and `CREDENTIALS`:

| Engine | Database | Async driver |
|--------|----------|-------------|
| `tortoise.backends.mysql` | MySQL / MariaDB | asyncmy |
| `tortoise.backends.sqlite` | SQLite | aiosqlite |

### MySQL Credentials

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

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `HOST` | `str` | yes | Database host. |
| `PORT` | `int` | yes | Database port. |
| `USER` | `str` | yes | Username. |
| `PASSWORD` | `str` | yes | Password. |
| `DATABASE` | `str` | yes | Database name. |
| `MIN_SIZE` | `int` | no | Minimum connection pool size. |
| `MAX_SIZE` | `int` | no | Maximum connection pool size. |
| `SSL` | `bool` | no | Enable SSL. |
| `CONNECT_TIMEOUT` | `int` | no | Connection timeout in seconds. |
| `ECHO` | `bool` | no | Echo SQL statements. |
| `CHARSET` | `str` | no | Character set (e.g. `"utf8mb4"`). |

### SQLite Credentials

```python
"CREDENTIALS": {
    "FILE_PATH": "./db.sqlite3",
    # optional
    "JOURNAL_MODE": "wal",
    "JOURNAL_SIZE_LIMIT": 16384,
    "FOREIGN_KEYS": "ON",
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `FILE_PATH` | `str` | yes | Path to the SQLite file. Use `":memory:"` for in-memory databases. |
| `JOURNAL_MODE` | `str` | no | SQLite journal mode. |
| `JOURNAL_SIZE_LIMIT` | `int` | no | Journal size limit in bytes. |
| `FOREIGN_KEYS` | `str` | no | Enable foreign key enforcement (`"ON"` / `"OFF"`). |

## Automatic Model Discovery

When `DATABASE.APPS` is **not** provided (the default), Unfazed automatically scans all installed apps at startup. Any app whose package contains a `models.py` module is registered:

```python
UNFAZED_SETTINGS = {
    ...
    "INSTALLED_APPS": [
        "apps.account",  # has models.py → models collected
        "apps.blog",     # has models.py → models collected
        "apps.utils",    # no models.py  → skipped
    ],
}
```

The auto-generated configuration is equivalent to:

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

`aerich.models` is always included to support Aerich's internal migration tracking table.

If you need fine-grained control — for example, routing different apps to different databases — provide `APPS` explicitly. See [Multiple Databases](#multiple-databases) below.

## Migration Commands

When a `DATABASE` is configured, Unfazed automatically registers Aerich-based migration commands. All commands accept `--location / -l` (default `./migrations`) to specify the migration directory.

| Command | Description | Extra flags |
|---------|-------------|-------------|
| `init-db` | Create the migration directory and generate the initial schema. | `--safe / -s` (default `True`) |
| `migrate` | Generate a new migration file from model changes. | `--name / -n` (default `"update"`), `--app / -a` (default `"models"`) |
| `upgrade` | Apply pending migrations. | `--transaction / -t` (default `True`) |
| `downgrade` | Revert to a specific migration version. | `--version / -v` (default `-1`), `--delete / -d` (default `True`) |
| `history` | List all applied migrations. | — |
| `heads` | Show available migration heads. | — |
| `inspectdb` | Reverse-engineer model definitions from existing database tables. | `--tables / -t` (specific tables to inspect) |

### Typical workflow

```bash
# 1. Initialise the migration directory (once per project)
unfazed-cli init-db

# 2. After changing models, generate a migration
unfazed-cli migrate --name add_published_field

# 3. Apply the migration
unfazed-cli upgrade

# 4. Check migration history
unfazed-cli history

# 5. Rollback the last migration if needed
unfazed-cli downgrade --version -1
```

### Inspecting an existing database

To generate model code from tables that already exist:

```bash
# Inspect all tables
unfazed-cli inspectdb

# Inspect specific tables
unfazed-cli inspectdb --tables user --tables order
```

## Multiple Databases

To route different models to different database connections, provide `APPS` explicitly with `DEFAULT_CONNECTION` pointing to the appropriate connection alias.

### 1. Configure connections and app groups

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

### 2. Set `app` in each model's `Meta`

Each model must declare which app group it belongs to via `app = "<group_key>"` in `class Meta`. The value must match the key you defined in `APPS`:

```python
# apps/account/models.py
from tortoise import Model, fields


class User(Model):
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)

    class Meta:
        table = "user"
        app = "models"  # matches the "models" key in APPS → uses "default" connection
```

```python
# apps/analytics/models.py
from tortoise import Model, fields


class EventLog(Model):
    event = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "event_log"
        app = "analytics_models"  # matches the "analytics_models" key in APPS → uses "analytics" connection
```

With this setup, `User` queries go to the `default` connection (primary-db) and `EventLog` queries go to the `analytics` connection (analytics-db).

When `APPS` is provided, automatic model discovery is skipped. You must list all model modules (including `aerich.models`) yourself.

## API Reference

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

Top-level database configuration model.

### Connection

```python
class Connection(BaseModel):
    engine: str = Field(..., alias="ENGINE")
    credentials: SqliteCredential | MysqlCredential = Field(..., alias="CREDENTIALS")
```

A single named database connection.

### AppModels

```python
class AppModels(BaseModel):
    models: List[str] = Field(..., alias="MODELS")
    default_connection: str = Field(default="default", alias="DEFAULT_CONNECTION")
```

Groups model modules and maps them to a connection alias.

### Driver

```python
class Driver(DataBaseDriver):
    def __init__(self, unfazed: Unfazed, conf: Database) -> None
```

Default Tortoise ORM driver (`unfazed.db.tortoise.Driver`).

- `async setup() -> None`: Build apps config (if not provided), call `Tortoise.init()`, and load Aerich commands.
- `async migrate() -> None`: Call `Tortoise.generate_schemas()` to create tables from models.
- `build_apps() -> Dict[str, AppModels]`: Auto-discover models from installed apps and return the Tortoise apps dict.
- `list_aerich_command() -> List[Command]`: Return `Command` objects for all Aerich CLI commands.

### ModelCenter

```python
class ModelCenter:
    def __init__(self, unfazed: Unfazed, conf: Database | None) -> None
```

Internal registry that manages the database driver lifecycle.

- `async setup() -> None`: Import the driver class, instantiate it, and call `driver.setup()`. No-op if `DATABASE` is not configured.
- `async migrate() -> None`: Call `driver.migrate()`. Raises `ValueError` if the driver has not been set up.

### DataBaseDriver (Protocol)

```python
class DataBaseDriver(Protocol):
    async def setup(self) -> None: ...
    async def migrate(self) -> None: ...
```

Protocol that custom database drivers must satisfy.
