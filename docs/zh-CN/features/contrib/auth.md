Auth
====

`unfazed.contrib.auth` 是认证与授权模块。它提供可插拔的后端系统、RBAC（基于角色的访问控制）模型、填充 `request.user` 的 middleware，以及用于保护 endpoint 的装饰器。

## 快速开始

### 1. 安装 app 和 middleware

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

### 2. 创建 User 模型

auth 模块需要一个继承自 `AbstractUser` 的具体 `User` 模型：

```python
# apps/account/models.py
from unfazed.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Meta:
        table = "user"
```

### 3. 配置 auth 设置

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

### 4. 包含 auth 路由

```python
# entry/routes.py
from unfazed.route import path, include

patterns = [
    path("/auth", routes=include("unfazed.contrib.auth.routes")),
]
```

这会注册以下 endpoint：

| 方法 | 路径 | 描述 |
|--------|------|-------------|
| POST | `/auth/login` | 用户登录。 |
| POST | `/auth/logout` | 当前用户登出。 |
| POST | `/auth/register` | 注册新用户。 |
| GET | `/auth/oauth-login-redirect` | OAuth 登录重定向。 |
| GET | `/auth/oauth-logout-redirect` | OAuth 登出重定向。 |

## 配置

Auth 设置注册在 `UNFAZED_CONTRIB_AUTH_SETTINGS` 下：

| 键 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `USER_MODEL` | `str` | 必填 | 具体 `User` 模型类的点分路径。 |
| `BACKENDS` | `Dict[str, AuthBackend]` | `{}` | 命名的 auth 后端。建议至少配置 `"default"` 后端。 |
| `SESSION_KEY` | `str` | `"unfazed_auth_session"` | 在 `request.session` 中存储 auth session 数据的键。 |

每个 `AuthBackend` 条目包含：

| 键 | 类型 | 描述 |
|-----|------|-------------|
| `BACKEND_CLS` | `str` | 继承自 `BaseAuthBackend` 的类的点分路径。 |
| `OPTIONS` | `Dict` | 传递给后端构造函数的任意选项字典。 |

## AuthenticationMiddleware

`AuthenticationMiddleware` 读取 session 并填充 `scope["user"]`，使 `request.user` 返回当前用户（匿名请求时为 `None`）。

它必须放在 middleware 列表中 `SessionMiddleware` **之后**，因为它依赖 `request.session`。

## User 模型

`AbstractUser` 提供：

| 字段 | 类型 | 描述 |
|-------|------|-------------|
| `account` | `CharField(255)` | 唯一账号标识。 |
| `password` | `CharField(255)` | 密码（按原样存储 — 哈希由后端负责）。 |
| `email` | `CharField(255)` | 邮箱地址。 |
| `is_superuser` | `SmallIntField` | 超级用户为 `1`，否则为 `0`。 |

**方法：**

| 方法 | 描述 |
|--------|-------------|
| `async query_roles()` | 返回分配给该用户的所有角色（直接及通过组）。 |
| `async query_groups()` | 返回该用户所属的所有组。 |
| `async has_permission(access)` | 若用户是超级用户或拥有包含给定 `access` 字符串的角色，则返回 `True`。 |
| `UserCls()` | （类方法）从设置中返回具体的 User 模型类。 |
| `async from_session(session_dict)` | （类方法）从 session 数据加载用户（按 `id` 查找）。 |

## RBAC 模型

auth 模块提供完整的 RBAC 模型集：

- **User** — 继承自 `AbstractUser` 的具体模型。
- **Group** — 用户组。一个组有多个用户和多个角色。
- **Role** — 持有权限的角色。角色可分配给用户或组。
- **Permission** — 由 `access` 字符串标识的单个权限条目。

关联表（`UserGroup`、`UserRole`、`GroupRole`、`RolePermission`）会自动创建。

权限检查会遍历完整图：`User → Roles → Permissions` 和 `User → Groups → Roles → Permissions`。

## 装饰器

### @login_required

当 `request.user` 为 `None` 时抛出 `LoginRequired`：

```python
from unfazed.contrib.auth.decorators import login_required


@login_required
async def dashboard(request):
    return HttpResponse(f"Hello, {request.user.account}")
```

### @permission_required

当用户不具有指定权限时抛出 `PermissionDenied`：

```python
from unfazed.contrib.auth.decorators import permission_required


@permission_required("blog.publish")
async def publish_post(request):
    ...
```

## Auth 后端

### BaseAuthBackend

所有 auth 后端的抽象基类：

```python
class BaseAuthBackend(ABC):
    alias: str  # 必须与 BACKENDS 配置中的键匹配

    async def login(self, ctx: LoginCtx) -> Tuple[Dict, Any]: ...
    async def register(self, ctx: RegisterCtx) -> None: ...
    async def logout(self, session: Dict) -> Any: ...
    async def session_info(self, user, ctx: LoginCtx) -> Dict: ...
    async def oauth_login_redirect(self) -> str: ...
    async def oauth_logout_redirect(self) -> str: ...
```

### DefaultAuthBackend

内置默认后端执行账号/密码认证：

- **login**：按 `account` 查找用户，验证 `password`，并返回 session 信息。
- **register**：创建新用户。若账号已存在则抛出 `AccountExisted`。
- **logout**：清除 auth session 键。

### 编写自定义后端

```python
from unfazed.contrib.auth.backends import BaseAuthBackend
from unfazed.contrib.auth.schema import LoginCtx, RegisterCtx


class OAuthBackend(BaseAuthBackend):
    @property
    def alias(self) -> str:
        return "github"

    async def login(self, ctx: LoginCtx):
        code = ctx.extra.get("code")
        # 用 code 换取 token，获取用户信息...
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

在设置中注册：

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

`AuthMixin` 将 RBAC 系统与 admin 模块连接。它实现 `AdminAuthProtocol`，使 admin 模型视图可以自动检查权限：

```python
from unfazed.contrib.auth.mixin import AuthMixin


class MyModelAdmin(AuthMixin, ...):
    ...
```

该 mixin 会根据当前用户的角色和权限检查 `has_view_permission`、`has_change_permission`、`has_delete_permission`、`has_create_permission` 和 `has_action_permission`。
