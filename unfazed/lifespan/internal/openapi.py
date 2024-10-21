import typing as t

from unfazed.protocol import BaseLifeSpan

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed


from unfazed.openapi.routes import patterns


class OpenApiLifeSpan(BaseLifeSpan):
    def __init__(self, unfazed: "Unfazed") -> None:
        self.unfazed = unfazed

    async def on_startup(self):
        settings = self.unfazed.settings
        if not settings.OPENAPI:
            return

        for pattern in patterns:
            self.unfazed.router.add_route(pattern)

    async def on_shutdown(self):
        pass

    @property
    def state(self) -> t.Dict[str, t.Any]:
        return {}
