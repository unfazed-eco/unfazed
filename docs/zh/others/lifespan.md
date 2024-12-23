Unfazed Lifespan
=====

lifespan 协议是一种与 ASGI 服务器通信的方式，用于启动和停止应用程序。在 unfazed 中，可以通过编写 `on_startup` 和 `on_shutdown` 方法来实现在应用程序的启动和停止的过程中做一些额外的工作。比如初始化数据库连接、关闭数据库连接等。


## 快速开始

编写一个简单的 lifespan 类。

1、创建一个新 lifespan 类

```python

from unfazed.lifespan import BaseLifespan

class YourLifespan(BaseLifespan):

    async def on_startup(self):
        print("on_startup")

    async def on_shutdown(self):
        print("on_shutdown")

```


2、在 unfazed 中使用

```python

# settings.py

UNFAZED_SETTINGS = {
    "LIFESPAN": ["yourmodule.YourLifespan"]
}

```

3、启动 unfazed

```shell

>>> python manage.py runserver
# on_startup

```



## 高级

lifespan 除了可以在启动和停止时做一些工作外，还可以携带信息到每个 request 中。

```python

from unfazed.lifespan import BaseLifespan

class YourLifespan(BaseLifespan):

    def __init__(self):
        super().__init__()
        self.conn = None

    async def on_startup(self):
        self.conn = await db_connect()

    async def on_shutdown(self):
        await self.conn.close()

    @property
    def state(self):
        return {"db_conn": self.conn}

```

在 settings.py 中配置完成之后，便可以在 endpoints 中的视图函数获取到这个信息。

```python

from unfazed.http import HttpRequest, HttpResponse

async def your_view(request: HttpRequest) -> HttpResponse:
    
    db_conn = request.state.db_conn

    # do something with db_conn
    return HttpResponse("ok")

```
