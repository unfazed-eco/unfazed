import typing as t
from contextlib import asynccontextmanager

from asgiref.typing import ASGIApplication

from unfazed.protocol import BaseLifeSpan

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class State(t.Dict):
    pass


class LifeSpanHandler:
    def __init__(self):
        self.lifespan: t.Dict[str, BaseLifeSpan] = {}

        self.unfazed: "Unfazed" | None = None

    def register(self, name: str, lifespan: BaseLifeSpan) -> None:
        if name in self.lifespan:
            raise ValueError(f"lifespan {name} already registered")
        self.lifespan[name] = lifespan

    def get(self, name: str) -> BaseLifeSpan:
        return self.lifespan.get(name)

    async def on_startup(self) -> None:
        for _, lifespan in self.lifespan.items():
            await lifespan.on_startup()

    async def on_shutdown(self) -> None:
        for _, lifespan in self.lifespan.items():
            await lifespan.on_shutdown()

    @property
    def state(self) -> State:
        ret = State()
        for _, lifespan in self.lifespan.items():
            ret.update(lifespan.state)

        return ret

    def clear(self):
        self.lifespan = {}


handler = LifeSpanHandler()


@asynccontextmanager
async def lifespan(app: "ASGIApplication") -> t.AsyncIterator[State] | None:
    await handler.on_startup()
    if handler.state:
        yield handler.state
    else:
        yield

    await handler.on_shutdown()
