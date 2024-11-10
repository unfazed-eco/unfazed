import time
import typing as t
from functools import wraps

import orjson as json

from unfazed.http import HttpRequest, HttpResponse

from .models import LogEntry


def record(func: t.Callable) -> t.Callable:
    @wraps(func)
    async def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        request_json = await request.json()
        resp: HttpResponse = await func(request, *args, **kwargs)

        await LogEntry.create(
            created_at=int(time.time()),
            account=request.user.username or request.user.email,
            path=request.url.path,
            ip=request.client.host,
            request=json.dumps(request_json).decode(),
            response=resp.body.decode(),
        )

        return resp

    return wrapper
