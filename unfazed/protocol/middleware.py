import typing as t

from asgiref import typing as at


@t.runtime_checkable
class MiddleWare(t.Protocol):
    def __init__(self, app: at.ASGIApplication) -> None: ...
    async def __call__(
        self, scope: at.HTTPScope, receive: at.ASGIReceiveEvent, send: at.ASGISendEvent
    ): ...
