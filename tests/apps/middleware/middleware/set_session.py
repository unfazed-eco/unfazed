from unfazed.middleware import BaseMiddleware
from unfazed.type import Receive, Scope, Send


class SetSessionMiddleware(BaseMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        scope["session"] = "session.test"

        await self.app(scope, receive, send)
