Error handling
===============

Unfazed 错误处理与大多数 web 框架不同，Unfazed 提倡在业务逻辑中只关注最正常的情况，而将错误处理交给框架来处理。
unfazed 提供一个通用的错误处理中间件，可以捕获所有未处理的异常，并返回一个标准的错误响应。如果标准的错误响应不满足需求，可以自定义错误处理函数。


### 使用

1、将错误处理中间件添加到配置中


```python

UNFAZED_SETTINGS = {
    "MIDDLEWARES": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
}


2、在视图函数中只有关注正常情况

假设以下接口的功能是读取一个文件，并返回其文件大小


```python

import os

async def endpoint1(request: HttpRequest, file_path: str) -> HttpResponse:
    file_size = os.path.getsize(file_path)
    
    return HttpResponse(text=f"size = {file_size}")

```

在 unfazed 中，开发者不必到处使用 `try...except` 来捕获异常，只需要关注最正常的情况即可。在以上例子中，开发者无需关注文件是否存在等异常情况，只用直接调用接口即可，框架会自动捕获异常并返回一个标准的错误响应。

3、主动抛出异常

在 unfazed 推荐的开发模式中，鼓励开发者主动抛出异常，而不使用 `if...else` 来处理异常情况。

假设以下接口同样实现读取一个文件，并返回其文件大小，但希望遇到任何报错都返回定义好的参数错误类型

```python

import os

class ParamError(Exception):
    pass

async def endpoint1(request: HttpRequest, file_path: str) -> HttpResponse:

    try:
        file_size = os.path.getsize(file_path)
    except Exception as e:
        raise ParamError(f"file_path: {file_path} not found")

    return HttpResponse(text=f"size = {file_size}")

```

在此情况下，所有异常的错误都会被捕获重新变成 `ParamError` 类型，此类型被中间件捕获后，会返回一个标准的错误响应。


