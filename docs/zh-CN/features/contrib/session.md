Session
=======

`unfazed.contrib.session` 通过 cookie 提供服务端 session 管理。它内置两种后端：cookie 签名后端（默认）和基于缓存的后端（Redis 或任意已配置的缓存）。session 在 endpoint 中可通过 `request.session` 访问，在 middleware 中可通过 `scope["session"]` 访问。

## 快速开始

### 1. 添加 middleware

```python
# entry/settings/__init__.py

UNFAZED_SETTINGS = {
    ...
    "MIDDLEWARE": [
        "unfazed.middleware.internal.common.CommonMiddleware",
        "unfazed.contrib.session.middleware.SessionMiddleware",
    ],
}
```

### 2. 配置 session 设置

```python
# entry/settings/__init__.py

UNFAZED_CONTRIB_SESSION_SETTINGS = {
    "SECRET": "your-secret-key-here",
    "COOKIE_DOMAIN": ".example.com",
}
```

### 3. 使用 session

```python
from unfazed.http import HttpRequest, JsonResponse


async def login(request: HttpRequest) -> JsonResponse:
    request.session["user_id"] = 42
    return JsonResponse({"status": "ok"})


async def profile(request: HttpRequest) -> JsonResponse:
    user_id = request.session["user_id"]
    return JsonResponse({"user_id": user_id})


async def logout(request: HttpRequest) -> JsonResponse:
    del request.session["user_id"]
    return JsonResponse({"status": "logged out"})
```

session 行为类似 dict — `__getitem__`、`__setitem__`、`__delitem__` 和 `__contains__` 均按预期工作。任何修改都会设置 `session.modified = True`，从而在响应中触发 `Set-Cookie` 头。

## 配置

Session 设置注册在 `UNFAZED_CONTRIB_SESSION_SETTINGS` 下：

| 键 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `SECRET` | `str` | 必填 | 用于签名的密钥（SigningSession）或通用配置。 |
| `ENGINE` | `str` | `"unfazed.contrib.session.backends.default.SigningSession"` | session 后端类的点分路径。 |
| `COOKIE_NAME` | `str` | `"session_id"` | session cookie 名称。 |
| `COOKIE_DOMAIN` | `str \| None` | `None` | cookie 域名。设为 `.example.com` 可实现跨子域 session。 |
| `COOKIE_PATH` | `str` | `"/"` | cookie 路径。 |
| `COOKIE_SECURE` | `bool` | `False` | 仅通过 HTTPS 发送 cookie。 |
| `COOKIE_HTTPONLY` | `bool` | `True` | 禁止 JavaScript 访问 cookie。 |
| `COOKIE_SAMESITE` | `"lax" \| "strict" \| "none"` | `"lax"` | SameSite cookie 属性。 |
| `COOKIE_MAX_AGE` | `int` | `604800`（7 天） | cookie 生命周期（秒）。 |
| `CACHE_ALIAS` | `str` | `"default"` | 缓存后端别名（仅 `CacheSession` 使用）。 |

## 后端

### SigningSession（默认）

将所有 session 数据存储在 cookie 内部，使用 `itsdangerous.TimestampSigner` 签名。无需服务端存储。

```python
UNFAZED_CONTRIB_SESSION_SETTINGS = {
    "SECRET": "my-secret",
    "ENGINE": "unfazed.contrib.session.backends.default.SigningSession",
}
```

**工作原理：**

1. `load()` 时：对 cookie 值进行 base64 解码、签名验证并反序列化（orjson）。
2. `save()` 时：将 session 字典序列化、签名并 base64 编码。结果成为 cookie 值。
3. 若签名过期或无效，session 会静默重置为 `{}`。

**权衡：**

- 无服务端状态 — 易于部署。
- cookie 大小有限（约 4 KB）。仅存储小的可序列化值。
- 修改 `SECRET` 会使所有现有 session 失效。

### CacheSession

将 session 数据存储在已配置的缓存后端（如 Redis）中。cookie 仅保存唯一的 session 键。

```python
UNFAZED_CONTRIB_SESSION_SETTINGS = {
    "SECRET": "my-secret",
    "ENGINE": "unfazed.contrib.session.backends.cache.CacheSession",
    "CACHE_ALIAS": "default",
}
```

确保缓存别名存在于 `CACHE` 设置中：

```python
UNFAZED_SETTINGS = {
    ...
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.redis.serializedclient.SerializerBackend",
            "LOCATION": "redis://localhost:6379/0",
        }
    },
}
```

**工作原理：**

1. `load()` 时：使用 cookie 中的 session 键从缓存获取数据。
2. `save()` 时：生成新的 session 键（如需要）并将数据存入缓存，TTL 等于 `COOKIE_MAX_AGE`。
3. 若 save 时 session 为空，则删除缓存条目。

**权衡：**

- 支持更大的 session 负载（不受 cookie 大小限制）。
- 需要运行中的缓存后端。
- 缓存被清空时 session 数据会丢失。

## SessionMiddleware

`SessionMiddleware` 是将一切串联起来的 ASGI middleware：

1. **请求阶段**：读取 session cookie，实例化配置的后端并调用 `load()`。将 session 附加到 `scope["session"]`。
2. **响应阶段**：若 `session.modified` 为 `True`，则调用 `save()` 并设置带有更新后的 session 键和 cookie 属性的 `Set-Cookie` 头。

当 session 被清空（所有键被删除）时，middleware 会设置 `max-age=0` 和过期的 `Expires` 头，以指示浏览器删除 cookie。

## 编写自定义后端

继承 `SessionBase` 并实现三个方法：

```python
from unfazed.contrib.session.backends.base import SessionBase


class MyBackend(SessionBase):
    def generate_session_key(self) -> str:
        # 返回唯一的 session 标识符
        ...

    async def save(self) -> None:
        # 持久化 self._session 并更新 self.session_key
        ...

    async def load(self) -> None:
        # 从 self.session_key 填充 self._session
        ...
```

然后将 `ENGINE` 设置指向你的类。

## API 参考

### SessionBase

```python
class SessionBase(ABC)
```

session 后端的抽象基类。对内部 `_session` 字典实现类 dict 的访问（`[]`、`in`、`del`）。

| 方法 / 属性 | 描述 |
|-------------------|-------------|
| `__getitem__(key)` | 获取 session 值。设置 `accessed = True`。 |
| `__setitem__(key, value)` | 设置 session 值。设置 `modified = True`。 |
| `__delitem__(key)` | 删除 session 键。设置 `modified = True`。 |
| `__contains__(key)` | 检查键是否存在。 |
| `async delete()` | 清除所有 session 数据。 |
| `async flush()` | `delete()` 的别名。 |
| `get_max_age()` | 从设置中返回 `cookie_max_age`。 |
| `generate_session_key()` | （抽象）生成新的 session 键。 |
| `async save()` | （抽象）持久化 session 数据。 |
| `async load()` | （抽象）加载 session 数据。 |

### SessionMiddleware

```python
class SessionMiddleware
```

按请求管理 session 生命周期的 ASGI middleware。

| 参数 | 来源 | 描述 |
|-----------|--------|-------------|
| `setting` | `UNFAZED_CONTRIB_SESSION_SETTINGS` | 初始化时加载的 session 配置。 |
| `engine_cls` | `setting.engine` | session 后端类，初始化时导入。 |
