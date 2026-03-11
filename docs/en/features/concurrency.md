Unfazed Concurrency
===================

Unfazed provides two async helper functions — `run_in_threadpool` and `run_in_processpool` — that let you offload synchronous work from your async handlers without blocking the event loop. They wrap [anyio](https://anyio.readthedocs.io/en/stable/) primitives with a friendlier interface that accepts `*args` and `**kwargs` directly.

## Quick Start

```python
from unfazed.concurrecy import run_in_threadpool

def blocking_io() -> str:
    import urllib.request
    response = urllib.request.urlopen("https://example.com")
    return response.read().decode()

async def homepage(request):
    html = await run_in_threadpool(blocking_io)
    return html
```

## Usage Guide

### Threadpool — for blocking I/O

Use `run_in_threadpool` when you need to call a synchronous function that performs blocking I/O (file access, legacy HTTP clients, database drivers without async support, etc.). The function runs in a separate thread, so the event loop stays responsive.

```python
from unfazed.concurrecy import run_in_threadpool

def read_large_file(path: str) -> str:
    with open(path) as f:
        return f.read()

content = await run_in_threadpool(read_large_file, "/data/report.csv")
```

### Processpool — for CPU-bound work

Use `run_in_processpool` when the synchronous function is CPU-intensive (image processing, data crunching, cryptographic hashing, etc.). The function runs in a separate process, bypassing Python's GIL.

```python
from unfazed.concurrecy import run_in_processpool

def compute_hash(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()

digest = await run_in_processpool(compute_hash, b"some large payload")
```

### Passing arguments

Both functions accept positional and keyword arguments, which are forwarded to the target function:

```python
from unfazed.concurrecy import run_in_threadpool

def greet(name: str, *, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

result = await run_in_threadpool(greet, "Alice", greeting="Hi")
# "Hi, Alice!"
```

### Exception propagation

If the target function raises an exception, it is re-raised in the calling coroutine. Handle it with standard `try`/`except`:

```python
from unfazed.concurrecy import run_in_threadpool

def might_fail() -> None:
    raise ValueError("something went wrong")

try:
    await run_in_threadpool(might_fail)
except ValueError as e:
    print(f"Caught: {e}")
```

## Examples

### Offloading a blocking API call in a view

When integrating with a third-party SDK that only offers synchronous methods, wrap the call with `run_in_threadpool` so other requests are not blocked:

```python
# myapp/endpoints.py
from unfazed.concurrecy import run_in_threadpool
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

### CPU-bound image thumbnail generation

Heavy computation like image resizing benefits from a process pool to avoid blocking the event loop and to bypass the GIL:

```python
# myapp/endpoints.py
from unfazed.concurrecy import run_in_processpool

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

## Gotchas / Tips

- **Pickling requirement for processpool**: `run_in_processpool` sends the function and arguments to a child process via pickling. Lambdas, closures, and locally-defined functions cannot be pickled and will raise an error. Always use module-level functions.

- **Threadpool works with lambdas**: Unlike `run_in_processpool`, `run_in_threadpool` can accept lambdas and closures since no pickling is involved.

- **Choosing the right pool**: As a rule of thumb — if your function waits on external resources (network, disk), use **threadpool**. If it crunches numbers or processes data in pure Python, use **processpool**.

- **No pool size configuration**: The underlying pool sizes are managed by [anyio](https://anyio.readthedocs.io/en/stable/). Thread pool size defaults to 40 threads. Process pool size defaults to the number of CPU cores. Refer to the anyio documentation for tuning options.

## API Reference

### run_in_threadpool

```python
async def run_in_threadpool(
    func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T
```

Run a synchronous function in a thread pool and return its result. The function is wrapped with `functools.partial` and delegated to `anyio.to_thread.run_sync`.

- `func` — the synchronous callable to execute.
- `*args` — positional arguments forwarded to `func`.
- `**kwargs` — keyword arguments forwarded to `func`.
- **Returns**: the return value of `func`.
- **Raises**: any exception raised by `func` is re-raised in the caller.

### run_in_processpool

```python
async def run_in_processpool(
    func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T
```

Run a synchronous function in a process pool and return its result. The function is wrapped with `functools.partial` and delegated to `anyio.to_process.run_sync`.

- `func` — the synchronous callable to execute. Must be picklable (module-level function).
- `*args` — positional arguments forwarded to `func`. Must be picklable.
- `**kwargs` — keyword arguments forwarded to `func`. Must be picklable.
- **Returns**: the return value of `func`. Must be picklable.
- **Raises**: any exception raised by `func` is re-raised in the caller.
