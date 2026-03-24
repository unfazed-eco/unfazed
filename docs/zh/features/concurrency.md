Unfazed 并发
=============

Unfazed 提供了两个异步辅助函数 — `run_in_threadpool` 和 `run_in_processpool` — 让你可以在异步处理函数中执行同步任务而不阻塞事件循环。它们封装了 [anyio](https://anyio.readthedocs.io/en/stable/) 的底层原语，提供了更友好的接口，可以直接传递 `*args` 和 `**kwargs`。

## 快速开始

```python
from unfazed.concurrency import run_in_threadpool

def blocking_io() -> str:
    import urllib.request
    response = urllib.request.urlopen("https://example.com")
    return response.read().decode()

async def homepage(request):
    html = await run_in_threadpool(blocking_io)
    return html
```

## 使用指南

### 线程池 — 适用于阻塞 I/O

当你需要调用执行阻塞 I/O 的同步函数时（文件访问、传统 HTTP 客户端、不支持异步的数据库驱动等），使用 `run_in_threadpool`。函数会在单独的线程中运行，保持事件循环的响应能力。

```python
from unfazed.concurrency import run_in_threadpool

def read_large_file(path: str) -> str:
    with open(path) as f:
        return f.read()

content = await run_in_threadpool(read_large_file, "/data/report.csv")
```

### 进程池 — 适用于 CPU 密集型任务

当同步函数是 CPU 密集型的（图像处理、数据计算、加密哈希等），使用 `run_in_processpool`。函数会在单独的进程中运行，绕过 Python 的 GIL。

```python
from unfazed.concurrency import run_in_processpool

def compute_hash(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()

digest = await run_in_processpool(compute_hash, b"some large payload")
```

### 传递参数

两个函数都支持位置参数和关键字参数，参数会被转发给目标函数：

```python
from unfazed.concurrency import run_in_threadpool

def greet(name: str, *, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

result = await run_in_threadpool(greet, "Alice", greeting="Hi")
# "Hi, Alice!"
```

### 异常传播

如果目标函数抛出异常，该异常会在调用协程中重新抛出。使用标准的 `try`/`except` 进行处理：

```python
from unfazed.concurrency import run_in_threadpool

def might_fail() -> None:
    raise ValueError("something went wrong")

try:
    await run_in_threadpool(might_fail)
except ValueError as e:
    print(f"Caught: {e}")
```

## 示例

### 在视图中执行阻塞 API 调用

当集成只提供同步方法的第三方 SDK 时，用 `run_in_threadpool` 包装调用，避免阻塞其他请求：

```python
# myapp/endpoints.py
from unfazed.concurrency import run_in_threadpool
from unfazed.http import JsonResponse

def fetch_exchange_rate(base: str, target: str) -> float:
    import urllib.request, json
    url = f"https://api.exchangerate.host/latest?base={base}&symbols={target}"
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read())
    return data["rates"][target]

async def exchange_rate_endpoint(request):
    rate = await run_in_threadpool(fetch_exchange_rate, "USD", "EUR")
    return JsonResponse({"rate": rate})
```

### CPU 密集型图片缩略图生成

图像缩放等重计算适合使用进程池，避免阻塞事件循环并绕过 GIL：

```python
# myapp/endpoints.py
from unfazed.concurrency import run_in_processpool

def generate_thumbnail(image_bytes: bytes, size: tuple) -> bytes:
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(image_bytes))
    img.thumbnail(size)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

async def thumbnail_endpoint(request):
    body = await request.body()
    thumb = await run_in_processpool(generate_thumbnail, body, (128, 128))
    ...
```

## 注意事项

- **进程池的序列化要求**：`run_in_processpool` 通过 pickle 将函数和参数发送到子进程。Lambda 表达式、闭包和局部定义的函数无法被 pickle 序列化，会引发错误。请始终使用模块级别的函数。

- **线程池支持 lambda**：与 `run_in_processpool` 不同，`run_in_threadpool` 可以接受 lambda 和闭包，因为不涉及 pickle 序列化。

- **选择合适的池**：经验法则 — 如果函数等待外部资源（网络、磁盘），使用**线程池**。如果函数进行纯 Python 的数字计算或数据处理，使用**进程池**。

- **无池大小配置**：底层池大小由 [anyio](https://anyio.readthedocs.io/en/stable/) 管理。线程池默认大小为 40 个线程，进程池默认大小为 CPU 核心数。调整选项请参阅 anyio 文档。

## API 参考

### run_in_threadpool

```python
async def run_in_threadpool(
    func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T
```

在线程池中运行同步函数并返回其结果。函数通过 `functools.partial` 包装后委托给 `anyio.to_thread.run_sync`。

- `func` — 要执行的同步可调用对象。
- `*args` — 转发给 `func` 的位置参数。
- `**kwargs` — 转发给 `func` 的关键字参数。
- **返回值**：`func` 的返回值。
- **异常**：`func` 抛出的任何异常都会在调用者中重新抛出。

### run_in_processpool

```python
async def run_in_processpool(
    func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T
```

在进程池中运行同步函数并返回其结果。函数通过 `functools.partial` 包装后委托给 `anyio.to_process.run_sync`。

- `func` — 要执行的同步可调用对象。必须可被 pickle 序列化（模块级别函数）。
- `*args` — 转发给 `func` 的位置参数。必须可被 pickle 序列化。
- `**kwargs` — 转发给 `func` 的关键字参数。必须可被 pickle 序列化。
- **返回值**：`func` 的返回值。必须可被 pickle 序列化。
- **异常**：`func` 抛出的任何异常都会在调用者中重新抛出。
