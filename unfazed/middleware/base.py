from unfazed.protocol import MiddleWareProtocol
from unfazed.types import ASGIApp, Receive, Scope, Send

from unfazed.http import Request


class BaseMiddleWare(MiddleWareProtocol):
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> ASGIApp:
        if scope["type"] == "http":
            return await self.app(scope, receive, send)

        await self.app(scope, receive, send)
