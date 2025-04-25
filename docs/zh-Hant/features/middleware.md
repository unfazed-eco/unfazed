Unfazed 中间件
======

中间件是网络框架中的重要组成部分，用于处理请求和响应。Unfazed 继承了 starlette 的中间件调用设计，提供

- 全局中间件
- 路由中间件


## 快速开始

unfazed 中间件仅提供一种编写方式。

```python

from unfazed.middleware import BaseMiddleware


class MyMiddleware(BaseMiddleware):
    
    async def __call__(self, scope, receive, send):
        # do something before request
        async def send_wrapper(message):
            # do something before response
            await send(message)
        await self.app(scope, receive, send_wrapper)


```


将其作为全局中间件

```python


# settings.py

UNFAZED_SETTINGS = {
    "MIDDLEWARE": [
        "app.middleware.MyMiddleware"
    ]
}


```


将其作为路由中间件

```python

# routes.py

from unfazed.route import path


patterns = [
    path("/api", endpoint=api, middleware=["app.middleware.MyMiddleware"])
]

```

中间件所需要的配置全部通过 `settings` 传递，这样可以方便进行管理。


```python


from unfazed.middleware import BaseMiddleware
from unfazed.conf import settings


class MyMiddleware(BaseMiddleware):

    def __init__(self):
        super().__init__()
        config = settings["APP_SETTINGS"]
        self.foo = config.FOO
    
    async def __call__(self, scope, receive, send):
        print(self.foo)
        # do something before request
        async def send_wrapper(message):
            # do something before response
            await send(message)
        await self.app(scope, receive, send_wrapper)


```


## 内置中间件

Unfazed 内置了一些中间件，用于处理请求和响应。


### CommonMiddleware


> 引入方式: "unfazed.middleware.internal.common.CommonMiddleware"


功能待扩展，当前提供对于报错的处理，当 DEBUG 为 True 时，返回详细的错误页面，为 False 时，返回 Internal Server Error。


### CORSMiddleware

> 引入方式: "unfazed.middleware.internal.cors.CORSMiddleware"


跨域请求处理中间件，继承 [starlette.corsmiddleware](https://github.com/encode/starlette/blob/master/starlette/middleware/cors.py)。
引入之后需要进行配置 `CORS` 项，具体配置信息可见 [cors settings](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/schema/middleware.py)


例子：

```python

UNFAZED_SETTINGS = {
    "CORS": {
        "ALLOW_ORIGINS": ["*"],
    }
}

```


### GZipMiddleware

> 引入方式: "unfazed.middleware.internal.gzip.GZipMiddleware"

gzip 压缩中间件，继承 [starlette.gzipmiddleware](https://github.com/encode/starlette/blob/master/starlette/middleware/gzip.py)

引入之后需要进行配置 `GZIP` 项，具体配置信息可见 [gzip settings](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/schema/middleware.py)


例子：

```python

UNFAZED_SETTINGS = {
    "GZIP": {
        "MINIMUM_SIZE": 1024,
    }
}

```


### TrustedHostMiddleware

> 引入方式: "unfazed.middleware.internal.trustedhost.TrustedHostMiddleware"

TrustedHostMiddleware 用于检查请求的 host 是否在 ALLOWED_HOSTS 中，如果不在，则返回 400 错误，继承 [starlette.TrustedHostMiddleware](https://github.com/encode/starlette/blob/master/starlette/middleware/trustedhost.py)。

引入之后需要进行配置 `TRUSTED_HOSTS` 项，具体配置信息可见 [trustedhost settings](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/schema/middleware.py)


例子：

```python

UNFAZED_SETTINGS = {
    "ALLOWED_HOSTS": ["*"],
}

```




### SessionMiddleware

> 引入方式: "unfazed.contrib.session.middleware.SessionMiddleware"

SessionMiddleware 用于处理 session，当前支持 siging 和 redis 两种 engine。配置信息可见 [session settings](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/contrib/session/settings.py)



例子：

```python

UNFAZED_CONTRIB_SESSION_SETTINGS = {
    "SECRET": "secret",
}

```