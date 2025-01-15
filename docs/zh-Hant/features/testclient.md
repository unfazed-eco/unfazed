Unfazed 测试
=====

unfazed 提供 `RequestFactory` 用于测试。


## 快速开始

使用 `RequestFactory` 创建一个请求对象，然后请求 unfazed 的路由。

```python

from unfazed.http.request import RequestFactory
from unfazed.core import Unfazed


async def test_request():

    unfazed = Unfazed()
    await unfazed.setup()

    request = RequestFactory(app=unfazed)

    resp = await request.get('/')

    assert resp.status == 200

```


RequestFactory 也支持对 lifespan 的测试。

```python

from unfazed.http.request import RequestFactory
from unfazed.core import Unfazed

async def test_request():

    unfazed = Unfazed()
    await unfazed.setup()

    async with RequestFactory(app=unfazed) as request:

        resp = await request.get('/')

        assert resp.status == 200


```

使用 async with 语法，可以测试 lifespan 的功能。

