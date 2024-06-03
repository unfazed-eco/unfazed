import typing as t
import warnings

from starlette.routing import BaseRoute, Mount, Route, WebSocketRoute


def path(
    path: str,
    endpoint: t.Callable | t.Sequence[Route] | t.Sequence[WebSocketRoute],
    *,
    methods: t.Sequence[str] = None,
    name: str = None,
    websocket: bool = False,
) -> BaseRoute:
    if isinstance(endpoint, t.Callable):
        if websocket:
            return WebSocketRoute(path, endpoint, methods=methods, name=name)
        else:
            return Route(path, endpoint, methods=methods, name=name)

    if methods is not None:
        warnings.warn("methods will be ignored when endpoint is a list of routes")

    return Mount(path, routes=endpoint, name=name)
