from pydantic import BaseModel

from unfazed.middleware import BaseMiddleware
from unfazed.type import Receive, Scope, Send


class User(BaseModel):
    name: str


class SetUserMiddleware(BaseMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        scope["user"] = User(name="unfazed")
        return await self.app(scope, receive, send)
