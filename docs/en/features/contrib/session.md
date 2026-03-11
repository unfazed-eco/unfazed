Session
=======

`unfazed.contrib.session` provides server-side session management via cookies. It ships with two backends: a cookie-signing backend (default) and a cache-backed backend (Redis or any configured cache). The session is accessible as `request.session` in endpoints and `scope["session"]` in middleware.

## Quick Start

### 1. Add the middleware

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

### 2. Configure session settings

```python
# entry/settings/__init__.py

UNFAZED_CONTRIB_SESSION_SETTINGS = {
    "SECRET": "your-secret-key-here",
    "COOKIE_DOMAIN": ".example.com",
}
```

### 3. Use the session

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

The session behaves like a dict — `__getitem__`, `__setitem__`, `__delitem__`, and `__contains__` all work as expected. Any mutation sets `session.modified = True`, which triggers a `Set-Cookie` header in the response.

## Configuration

Session settings are registered under `UNFAZED_CONTRIB_SESSION_SETTINGS`:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `SECRET` | `str` | required | Secret key used for signing (SigningSession) or general configuration. |
| `ENGINE` | `str` | `"unfazed.contrib.session.backends.default.SigningSession"` | Dotted path to the session backend class. |
| `COOKIE_NAME` | `str` | `"session_id"` | Name of the session cookie. |
| `COOKIE_DOMAIN` | `str \| None` | `None` | Domain for the cookie. Set to `.example.com` for cross-subdomain sessions. |
| `COOKIE_PATH` | `str` | `"/"` | Cookie path. |
| `COOKIE_SECURE` | `bool` | `False` | Send cookie only over HTTPS. |
| `COOKIE_HTTPONLY` | `bool` | `True` | Prevent JavaScript access to the cookie. |
| `COOKIE_SAMESITE` | `"lax" \| "strict" \| "none"` | `"lax"` | SameSite cookie attribute. |
| `COOKIE_MAX_AGE` | `int` | `604800` (7 days) | Cookie lifetime in seconds. |
| `CACHE_ALIAS` | `str` | `"default"` | Cache backend alias (only used by `CacheSession`). |

## Backends

### SigningSession (default)

Stores all session data inside the cookie itself, signed with `itsdangerous.TimestampSigner`. No server-side storage is needed.

```python
UNFAZED_CONTRIB_SESSION_SETTINGS = {
    "SECRET": "my-secret",
    "ENGINE": "unfazed.contrib.session.backends.default.SigningSession",
}
```

**How it works:**

1. On `load()`: the cookie value is base64-decoded, signature-verified, and deserialized (orjson).
2. On `save()`: the session dict is serialized, signed, and base64-encoded. The result becomes the cookie value.
3. If the signature is expired or invalid, the session is silently reset to `{}`.

**Trade-offs:**

- No server-side state — easy to deploy.
- Cookie size is limited (~4 KB). Store only small, serialisable values.
- Changing the `SECRET` invalidates all existing sessions.

### CacheSession

Stores session data in a configured cache backend (e.g. Redis). The cookie only holds a unique session key.

```python
UNFAZED_CONTRIB_SESSION_SETTINGS = {
    "SECRET": "my-secret",
    "ENGINE": "unfazed.contrib.session.backends.cache.CacheSession",
    "CACHE_ALIAS": "default",
}
```

Make sure the cache alias exists in your `CACHE` setting:

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

**How it works:**

1. On `load()`: the session key from the cookie is used to fetch data from the cache.
2. On `save()`: a new session key is generated (if needed) and data is stored in the cache with TTL equal to `COOKIE_MAX_AGE`.
3. If the session is empty on save, the cache entry is deleted.

**Trade-offs:**

- Supports larger session payloads (not limited by cookie size).
- Requires a running cache backend.
- Session data is lost if the cache is flushed.

## SessionMiddleware

`SessionMiddleware` is the ASGI middleware that wires everything together:

1. **Request phase**: Reads the session cookie, instantiates the configured backend, and calls `load()`. Attaches the session to `scope["session"]`.
2. **Response phase**: If `session.modified` is `True`, calls `save()` and sets the `Set-Cookie` header with the updated session key and cookie attributes.

When the session is emptied (all keys deleted), the middleware sets `max-age=0` and an expired `Expires` header to instruct the browser to remove the cookie.

## Writing a Custom Backend

Subclass `SessionBase` and implement three methods:

```python
from unfazed.contrib.session.backends.base import SessionBase


class MyBackend(SessionBase):
    def generate_session_key(self) -> str:
        # Return a unique session identifier
        ...

    async def save(self) -> None:
        # Persist self._session and update self.session_key
        ...

    async def load(self) -> None:
        # Populate self._session from self.session_key
        ...
```

Then point the `ENGINE` setting to your class.

## API Reference

### SessionBase

```python
class SessionBase(ABC)
```

Abstract base class for session backends. Implements dict-like access (`[]`, `in`, `del`) on the internal `_session` dict.

| Method / Property | Description |
|-------------------|-------------|
| `__getitem__(key)` | Get a session value. Sets `accessed = True`. |
| `__setitem__(key, value)` | Set a session value. Sets `modified = True`. |
| `__delitem__(key)` | Delete a session key. Sets `modified = True`. |
| `__contains__(key)` | Check if a key exists. |
| `async delete()` | Clear all session data. |
| `async flush()` | Alias for `delete()`. |
| `get_max_age()` | Return `cookie_max_age` from settings. |
| `generate_session_key()` | (abstract) Generate a new session key. |
| `async save()` | (abstract) Persist session data. |
| `async load()` | (abstract) Load session data. |

### SessionMiddleware

```python
class SessionMiddleware
```

ASGI middleware that manages session lifecycle per request.

| Parameter | Source | Description |
|-----------|--------|-------------|
| `setting` | `UNFAZED_CONTRIB_SESSION_SETTINGS` | Session configuration loaded on init. |
| `engine_cls` | `setting.engine` | The session backend class, imported on init. |
