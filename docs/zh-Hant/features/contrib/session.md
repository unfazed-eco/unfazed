Session
====

Session 是 unfazed 的会话管理器，用于管理用户会话


### Quick Start


1、配置 session 中间件

```python

# settings.py

UNFAZED_SETTINGS = {
    "MIDDLEWARES": ["unfazed.contrib.session.middleware.SessionMiddleware"],
}

```

2、配置 session 存储

```python

# settings.py

# 使用默认的内存存储
UNFAZED_CONTRIB_SESSION_SETTINGS = {
    "SECRET": uuid.uuid4().hex,
    "COOKIE_DOMAIN": "unfazed.com",
    "COOKIE_SECURE": True,
}

# 使用 redis 存储
UNFAZED_CONTRIB_SESSION_SETTINGS = {
    "SECRET": uuid.uuid4().hex,
    "COOKIE_DOMAIN": "unfazed.com",
    "COOKIE_SECURE": True,
    "CACHE_ALIAS": "default",
    "ENGINE": "unfazed.contrib.session.backends.cache.CacheSession",
}

```

3、在视图函数中设置 session

```python

# endpoints.py

async def set_session(request: HttpRequest) -> HttpResponse:
    request.session["your_session_key"] = {"foo": "bar"}

    return HttpResponse("ok")

```


4、在视图函数中获取 session

```python

# endpoints.py

async def get_session(request: HttpRequest) -> HttpResponse:
    session = request.session["your_session_key"]
    return HttpResponse("ok")

```


5、其他操作

```python

# endpoints.py

async def delete_session(request: HttpRequest) -> HttpResponse:
    # 删除特定 session
    del request.session["your_session_key"]

    # 清空所有 session
    request.session.clear()

    return HttpResponse("ok")


async def update_session(request: HttpRequest) -> HttpResponse:
    # 更新 session
    request.session["your_session_key"] = {"foo2": "bar2"}

    return HttpResponse("ok")

```
