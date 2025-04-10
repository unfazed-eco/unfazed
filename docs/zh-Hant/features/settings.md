Unfazed 配置
----------------

Unfazed 的配置文件是一个 Python 模块，其中包含了一系列配置项。你可以通过 `settings.py` 文件来配置你的 Unfazed 项目。



### 设计思路


Unfazed 配置文件借鉴了 Django 的思路，他们的区别如下


`django` 的使用方式

```python


# settings.py
FOO = 'bar'


# app/views.py

from django.conf import settings

print(settings.FOO)  # bar


```


`unfazed` 的使用方式

```python


# settings.py

APP_SETTINGS = {
    'FOO': 'bar'
}


# app/settings.py

from pydantic import BaseModel
from unfazed.conf import register_settings

@register_settings("APP_SETTINGS")
class AppSettings(BaseModel):
    FOO: str


# app/endpoints.py

from unfazed.conf import settings
from .settings import AppSettings


app_settings: AppSettings = settings["APP_SETTINGS"]
print(app_settings.FOO)  # bar


```

配置部分，unfazed 区别 django 的是将同一个 app 的配置项统一放在一个 `dict` 中，并且使用 pydantic 做校验，这样开发者在获取配置的时候，能够清晰的知道这个配置项的各种信息。并且在 `settings.py` 中，即使配置项很多，也清楚的知道这个配置项是属于哪个 app 的，而且随着项目的迭代，开发者能够方便地管理配置项。


### UnfazedSettings

UnfazedSettings 是 unfazed 拉起服务所需要的配置, [source code](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/conf/__init__.py)



#### DEBUG


`DEBUG: bool` 用于控制是否开启调试模式。在调试模式下，Unfazed 在遇到报错时会返回详细的报错信息和当前配置信息。


#### PROJECT_NAME


`PROJECT_NAME: str` 项目名称，用于在日志中标识当前项目, 默认为 `Unfazed`。


#### ROOT_URLCONF


`ROOT_URLCONF: str` 路由配置根节点，unfazed 会从该地址开始加载路由配置，使用 unfazed-cli 初始化项目后，该项默认为 `entry.routes`。


#### VERSION

`VERSION: str` 项目版本号，用于在日志中标识当前项目版本，默认为 `0.0.1`。


#### MIDDLEWARE

`MIDDLEWARE: List[str]` 中间件配置，用于在请求处理前后进行一些操作。

例子：

```python


MIDDLEWARE = [
    "unfazed.middleware.internal.cors.CORSMiddleware",
    "unfazed.middleware.internal.gzip.GZipMiddleware",
    "unfazed.middleware.internal.trustedhost.TrustedHostMiddleware",
]

```


#### INSTALLED_APPS

`INSTALLED_APPS: List[str]` 安装的 app 引入路径，用于在启动服务时加载 app。

例子：

```python

INSTALLED_APPS = [
    "unfazed.contrib.admin",
    "unfazed.contrib.auth",
]

```

关于 app 的详细信息，请参考 [app](app.md)。


#### DATABASE

`DATABASE: Dict` 数据库配置，用于配置数据库连接信息。

unfazed 使用 tortoise-orm 作为默认的 ORM 框架。

例子：

```python


DATABASE = {
    "CONNECTIONS": {
        "default": {
            "ENGINE": "tortoise.backends.mysql",
            "CREDENTIALS": {
                "host": "localhost",
                "port": "5432",
                "user": "app",
                "password": "app",
                "database": "app",
            },
        }
    }
}

```

关于数据库的详细配置信息，请参考 [database](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/schema/orm.py)。


### CACHE

`CACHE: Dict` 缓存配置，用于配置缓存信息。当前 unfazed 提供 local memory 和 redis 两个 client。

例子：

```python

CACHE = {
    "default": {
        "backend": "unfazed.cache.backends.locmem.LocMemCache",
        "options": {
            "max_size": 1000,
            "ttl": 60,
        },
    },
    "redis": {
        "backend": "unfazed.cache.backends.redis.defaultclient.DefaultBackend",
        "location": "redis://localhost:6379/0",
        "options": {
            "max_connections": 1000,
            "decode_responses": True,
        },
    },
}

```

关于缓存的详细配置信息，请参考 [cache](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/schema/cache.py)。


#### LOGGING

`LOGGING: Dict` 日志配置，用于配置日志信息。配置项参考 [python logging](https://docs.python.org/3/library/logging.config.html#configuration-dictionary-schema)。


例子：

```python


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "unfazed": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}

```

关于日志的详细配置信息，请参考 [logging](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/schema/logging.py)。

#### LIFESPAN

`LIFESPAN: List[str]` 生命周期配置，相关 asgi 文档可见 [lifespan](https://asgi.readthedocs.io/en/latest/specs/lifespan.html#)。


例子：

```python

LIFESPAN = [
    "unfazed.cache.lifespan.CacheClear",
]

```

关于生命周期的详细信息，请参考 [生命周期](./lifespan.md)。


#### OPENAPI

`OPENAPI: Dict` openapi 配置，unfazed 内置 openapi 支持，按 unfazed 推荐的方式完成 `endpoints` 中接口的编写，即可自动生成 openapi 文档，包括 `swagger` 和 `redoc`。


例子：

```python

OPENAPI = {
    "servers": [
        {
            "url": "http://localhost:9527",
            "description": "development server",
        }
    ],
}

```

详细配置见 [schema.openapi](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/schema/openapi.py)


#### CORS

`CORS: Dict` 跨域配置，unfazed 内置跨域支持，需要配合 `unfazed.middleware.internal.cors.CORSMiddleware` 使用。

详细配置见 [cors](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/schema/middleware.py)

#### TRUSTED_HOST


`TRUSTED_HOST: Dict` 可信主机配置，用于配置可信主机，需要配合 `unfazed.middleware.internal.trustedhost.TrustedHostMiddleware` 使用。

详细配置见 [trustedhost](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/schema/middleware.py)

#### GZIP

`GZIP: Dict` GZIP 配置，用于配置 GZIP 压缩，需要配合 `unfazed.middleware.internal.gzip.GZipMiddleware` 使用。


详细配置见 [gzip](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/schema/middleware.py)


### SessionSettings

SessionSettings 是 unfazed session 配置, 配合 `unfazed.contrib.session.middleware.SessionMiddleware` 使用, [source code](

[source code](https://github.com/unfazed-eco/unfazed/blob/main/unfazed/contrib/session/settings.py)


关于 cookie 的详细信息，请参考 [cookie.md](https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/Cookies))


#### alias

unfazed session 默认提供了 signing 和 redis 两种 session 引擎。其中如果使用 redis 引擎，可以配置 alias 表明使用哪个 cache client, 默认为 `default`。

