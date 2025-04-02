import typing as t

from unfazed.type import ASGIApp, Receive, Scope, Send


@t.runtime_checkable
class MiddleWare(t.Protocol):
    def __init__(self, app: ASGIApp) -> None: ...
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...
