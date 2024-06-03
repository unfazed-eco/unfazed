import typing as t

from starlette.types import ASGIApp, Receive, Scope, Send


class MiddleWareProtocol(t.Protocol):
    def __init__(self, app: ASGIApp) -> None: ...
    async def __call__(self, scope: Scope, receive: Receive, send: Send): ...
