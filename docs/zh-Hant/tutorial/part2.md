创建应用 以及 hello，world
====

在上一节中，我们安装了 unfazed 并创建了一个项目。接下来，我们将在项目中创建一个 app，并在 app 中创建一个 hello，world 的接口。



### 创建 app

为了做演示，我们将在项目中以简单模式创建一个名为 enroll 的 app。在项目的 backend 目录下运行以下命令：

```bash

cd tutorial/src/backend

python manage.py startapp -n enroll -t simple


```

该命令会在当前目录下的 backend 目录中创建一个名为 enroll 的 app。其文件结构如下：

```bash

├── enroll
│   ├── admin.py
│   ├── app.py
│   ├── endpoints.py
│   ├── models.py
│   ├── routes.py
│   ├── schema.py
│   ├── serializers.py
│   ├── services.py
│   ├── settings.py
│   └── tests.py

```

解释一下各个文件的作用：

- admin.py: unfazed 的 admin 配置文件，配合 unfazed-admin 使用
- app.py: app 的入口配置文件
- endpoints.py: app 的接口定义文件
- models.py: app 的数据模型定义文件，unfazed 默认使用 tortoise-orm 作为 ORM
- routes.py: app 的路由定义文件
- schema.py: 接口的请求和响应数据模型定义文件
- serializers.py: 对 model 的序列化和反序列化定义文件
- services.py: 业务逻辑处理文件
- settings.py: 该 app 的配置文件
- tests.py: 该 app 的测试文件，unfazed 默认使用 pytest 来做测试


关于文件结构的设计，参考 [ddd-vs-mtv](../instruction/ddd-vs-mtv.md)。


### Hello, World

接下来，我们在 enroll 的 endpoints.py 文件中定义一个 hello，world 的接口。在 endpoints.py 文件中写入以下代码：


```python

# tutorial/src/backend/enroll/endpoints.py

from unfazed.http import HttpRequest, PlainTextResponse

async def hello(request: HttpRequest) -> PlainTextResponse:
    return PlainTextResponse("Hello, world!")


```

然后，在 routes.py 中引入 hello 接口，并配置路由。在 routes.py 文件中写入以下代码：

```python

# tutorial/src/backend/enroll/routes.py

import typing as t

from unfazed.route import Route, path

from .endpoints import hello

patterns: t.List[Route] = [path("/hello", endpoint=hello)]

```


然后，在 entry 入口文件夹中引入 enroll 的路由。在 entry/routes.py 文件中写入以下代码：

```python

# tutorial/src/backend/entry/routes.py

from unfazed.route import include, path

patterns = [
    path("/enroll", routes=include("enroll.routes")),
]


```

最后，在 entry/settings 中将 enroll 这个 app 加入到 INSTALLED_APPS 中。在 entry/settings/__init__.py 文件中写入以下代码：

```python

# tutorial/src/backend/entry/settings/__init__.py   

INSTALLED_APPS = [
    "enroll",
]

```


### 运行项目

在项目的 backend 目录下运行以下命令：

```bash

cd tutorial/src/backend

python manage.py runserver --host 127.0.0.1 --port 9527


```

然后在浏览器中访问 http://127.0.0.1:9527/enroll/hello，即可看到 Hello, world! 的输出。

