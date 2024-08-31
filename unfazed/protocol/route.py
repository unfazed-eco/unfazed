import typing as t

from asgiref import typing as at
from starlette.datastructures import URLPath
from starlette.routing import Match


@t.runtime_checkable
class Route(t.Protocol):
    def matches(self, scope: at.HTTPScope) -> tuple[Match, at.HTTPScope]: ...

    def url_path_for(self, name: str, /, **path_params: t.Any) -> URLPath: ...

    async def handle(
        self, scope: at.HTTPScope, receive: at.ASGIReceiveEvent, send: at.ASGISendEvent
    ) -> None: ...

    async def __call__(
        self, scope: at.HTTPScope, receive: at.ASGIReceiveEvent, send: at.ASGISendEvent
    ) -> None: ...
