import typing as t

from starlette.middleware import Middleware
from starlette.routing import Route as StartletteRoute

from unfazed.protocol import MiddleWare as MiddleWareProtocol


class Route(StartletteRoute):
    def __init__(
        self,
        path: str,
        endpoint: t.Callable[..., t.Any],
        *,
        methods: list[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
        middleware: t.Sequence[Middleware] | None = None,
        app_label: str | None = None,
    ) -> None:
        super().__init__(
            path,
            endpoint,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
            middleware=middleware,
        )

        self.app_label = app_label

    def load_middlewares(
        self, middlewares: t.Sequence[t.Type[MiddleWareProtocol]]
    ) -> None:
        if middlewares is not None:
            for cls, args, kwargs in reversed(middlewares):
                self.app = cls(app=self.app, *args, **kwargs)
