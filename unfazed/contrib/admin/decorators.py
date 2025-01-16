import time
import typing as t
from functools import wraps

import orjson as json

from unfazed.http import HttpRequest, HttpResponse

from .models import LogEntry


def record(func: t.Callable) -> t.Callable:
    @wraps(func)
    async def wrapper(
        request: HttpRequest, *args: t.Any, **kwargs: t.Any
    ) -> HttpResponse:
        request_json = await request.json()
        resp: HttpResponse = await func(request, *args, **kwargs)

        if request.user:
            account = request.user.account or request.user.email
        else:
            # for mypy check
            # this line will never be executed
            account = "anonymous"  # pragma: no cover

        if request.client:
            ip = request.client.host
        else:
            ip = "unknown"

        await LogEntry.create(
            created_at=int(time.time()),
            account=account,
            path=request.url.path,
            ip=ip,
            request=json.dumps(request_json).decode(),
            response=t.cast(bytes, resp.body).decode(),
        )

        return resp

    return wrapper
