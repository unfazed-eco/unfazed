Session
====

Session is unfazed's session manager, used for managing user sessions


### Quick Start


1. Configure session middleware

```python

# settings.py

UNFAZED_SETTINGS = {
    "MIDDLEWARES": ["unfazed.contrib.session.middleware.SessionMiddleware"],
}

```

2. Configure session storage

```python

# settings.py

# Using default memory storage
UNFAZED_CONTRIB_SESSION_SETTINGS = {
    "SECRET": uuid.uuid4().hex,
    "COOKIE_DOMAIN": "unfazed.com",
    "COOKIE_SECURE": True,
}

# Using redis storage
UNFAZED_CONTRIB_SESSION_SETTINGS = {
    "SECRET": uuid.uuid4().hex,
    "COOKIE_DOMAIN": "unfazed.com",
    "COOKIE_SECURE": True,
    "CACHE_ALIAS": "default",
    "ENGINE": "unfazed.contrib.session.backends.cache.CacheSession",
}

```

3. Set session in view functions

```python

# endpoints.py

async def set_session(request: HttpRequest) -> HttpResponse:
    request.session["your_session_key"] = {"foo": "bar"}

    return HttpResponse("ok")

```


4. Get session in view functions

```python

# endpoints.py

async def get_session(request: HttpRequest) -> HttpResponse:
    session = request.session["your_session_key"]
    return HttpResponse("ok")

```


5. Other operations

```python

# endpoints.py

async def delete_session(request: HttpRequest) -> HttpResponse:
    # Delete specific session
    del request.session["your_session_key"]

    # Clear all sessions
    request.session.clear()

    return HttpResponse("ok")


async def update_session(request: HttpRequest) -> HttpResponse:
    # Update session
    request.session["your_session_key"] = {"foo2": "bar2"}

    return HttpResponse("ok")

```
