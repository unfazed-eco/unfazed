Auth
====

`unfazed.contrib.auth` is an authentication and authorisation module. It provides a pluggable backend system, RBAC (Role-Based Access Control) models, middleware that populates `request.user`, and decorators for guarding endpoints.

## Quick Start

### 1. Install the app and middleware

```python
# entry/settings/__init__.py

UNFAZED_SETTINGS = {
    ...
    "INSTALLED_APPS": [
        "unfazed.contrib.auth",
    ],
    "MIDDLEWARE": [
        "unfazed.middleware.internal.common.CommonMiddleware",
        "unfazed.contrib.session.middleware.SessionMiddleware",
        "unfazed.contrib.auth.middleware.AuthenticationMiddleware",
    ],
}
```

### 2. Create a User model

The auth module requires a concrete `User` model that inherits from `AbstractUser`:

```python
# apps/account/models.py
from unfazed.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Meta:
        table = "user"
```

### 3. Configure auth settings

```python
# entry/settings/__init__.py

UNFAZED_CONTRIB_AUTH_SETTINGS = {
    "USER_MODEL": "apps.account.models.User",
    "BACKENDS": {
        "default": {
            "BACKEND_CLS": "unfazed.contrib.auth.backends.default.DefaultAuthBackend",
            "OPTIONS": {},
        }
    },
}
```

### 4. Include auth routes

```python
# entry/routes.py
from unfazed.route import path, include

patterns = [
    path("/auth", routes=include("unfazed.contrib.auth.routes")),
]
```

This registers the following endpoints:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Log in a user. |
| POST | `/auth/logout` | Log out the current user. |
| POST | `/auth/register` | Register a new user. |
| GET | `/auth/oauth-login-redirect` | OAuth login redirect. |
| GET | `/auth/oauth-logout-redirect` | OAuth logout redirect. |

## Configuration

Auth settings are registered under the key `UNFAZED_CONTRIB_AUTH_SETTINGS`:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `USER_MODEL` | `str` | required | Dotted path to your concrete `User` model class. |
| `BACKENDS` | `Dict[str, AuthBackend]` | `{}` | Named auth backends. At least a `"default"` backend is recommended. |
| `SESSION_KEY` | `str` | `"unfazed_auth_session"` | Key used to store auth session data inside `request.session`. |

Each `AuthBackend` entry has:

| Key | Type | Description |
|-----|------|-------------|
| `BACKEND_CLS` | `str` | Dotted path to a class inheriting from `BaseAuthBackend`. |
| `OPTIONS` | `Dict` | Arbitrary options dict passed to the backend constructor. |

## AuthenticationMiddleware

`AuthenticationMiddleware` reads the session and populates `scope["user"]` so that `request.user` returns the current user (or `None` for anonymous requests).

It must be placed **after** `SessionMiddleware` in the middleware list, since it depends on `request.session`.

## The User Model

`AbstractUser` provides:

| Field | Type | Description |
|-------|------|-------------|
| `account` | `CharField(255)` | Unique account identifier. |
| `password` | `CharField(255)` | Password (stored as provided — hashing is the backend's responsibility). |
| `email` | `CharField(255)` | Email address. |
| `is_superuser` | `SmallIntField` | `1` for superuser, `0` otherwise. |

**Methods:**

| Method | Description |
|--------|-------------|
| `async query_roles()` | Return all roles assigned to this user (directly and through groups). |
| `async query_groups()` | Return all groups this user belongs to. |
| `async has_permission(access)` | Return `True` if the user is a superuser or has a role with the given `access` string. |
| `UserCls()` | (classmethod) Return the concrete User model class from settings. |
| `async from_session(session_dict)` | (classmethod) Load a user from session data (looks up by `id`). |

## RBAC Models

The auth module ships with a full RBAC model set:

- **User** — your concrete model inheriting from `AbstractUser`.
- **Group** — groups of users. A group has many users and many roles.
- **Role** — roles that hold permissions. A role can be assigned to users or groups.
- **Permission** — individual permission entries identified by an `access` string.

Join tables (`UserGroup`, `UserRole`, `GroupRole`, `RolePermission`) are created automatically.

Permission checking traverses the full graph: `User → Roles → Permissions` and `User → Groups → Roles → Permissions`.

## Decorators

### @login_required

Raises `LoginRequired` if `request.user` is `None`:

```python
from unfazed.contrib.auth.decorators import login_required


@login_required
async def dashboard(request):
    return HttpResponse(f"Hello, {request.user.account}")
```

### @permission_required

Raises `PermissionDenied` if the user does not have the specified permission:

```python
from unfazed.contrib.auth.decorators import permission_required


@permission_required("blog.publish")
async def publish_post(request):
    ...
```

## Auth Backends

### BaseAuthBackend

Abstract base class for all auth backends:

```python
class BaseAuthBackend(ABC):
    alias: str  # must match the key in BACKENDS config

    async def login(self, ctx: LoginCtx) -> Tuple[Dict, Any]: ...
    async def register(self, ctx: RegisterCtx) -> None: ...
    async def logout(self, session: Dict) -> Any: ...
    async def session_info(self, user, ctx: LoginCtx) -> Dict: ...
    async def oauth_login_redirect(self) -> str: ...
    async def oauth_logout_redirect(self) -> str: ...
```

### DefaultAuthBackend

The built-in default backend performs account/password authentication:

- **login**: Looks up the user by `account`, verifies the `password`, and returns session info.
- **register**: Creates a new user. Raises `AccountExisted` if the account already exists.
- **logout**: Clears the auth session key.

### Writing a Custom Backend

```python
from unfazed.contrib.auth.backends import BaseAuthBackend
from unfazed.contrib.auth.schema import LoginCtx, RegisterCtx


class OAuthBackend(BaseAuthBackend):
    @property
    def alias(self) -> str:
        return "github"

    async def login(self, ctx: LoginCtx):
        code = ctx.extra.get("code")
        # exchange code for token, fetch user info...
        session_info = {"id": user.id, "platform": "github"}
        return session_info, session_info

    async def register(self, ctx: RegisterCtx):
        ...

    async def logout(self, session):
        return {}

    async def session_info(self, user, ctx):
        return {"id": user.id, "account": user.account, "platform": ctx.platform}

    async def oauth_login_redirect(self) -> str:
        return "https://github.com/login/oauth/authorize?client_id=..."

    async def oauth_logout_redirect(self) -> str:
        return ""
```

Register it in settings:

```python
UNFAZED_CONTRIB_AUTH_SETTINGS = {
    "USER_MODEL": "apps.account.models.User",
    "BACKENDS": {
        "default": {
            "BACKEND_CLS": "unfazed.contrib.auth.backends.default.DefaultAuthBackend",
        },
        "github": {
            "BACKEND_CLS": "apps.account.backends.OAuthBackend",
        },
    },
}
```

## AuthMixin

`AuthMixin` connects the RBAC system with the admin module. It implements `AdminAuthProtocol` so admin model views can check permissions automatically:

```python
from unfazed.contrib.auth.mixin import AuthMixin


class MyModelAdmin(AuthMixin, ...):
    ...
```

The mixin checks `has_view_permission`, `has_change_permission`, `has_delete_permission`, `has_create_permission`, and `has_action_permission` against the current user's roles and permissions.
