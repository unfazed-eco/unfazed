import inspect
import typing as t
from importlib import import_module

from starlette.routing import compile_path

from unfazed.protocol import MiddleWare

from .registry import _flatten_patterns
from .routing import Route


def include(route_path: str) -> t.Sequence[Route]:
    route_module = import_module(route_path)
    app_label = route_path.rsplit(".", 1)[0]

    if not hasattr(route_module, "patterns"):
        raise ValueError(f"{route_path} must have a 'routes' list")

    patterns = _flatten_patterns(route_module.patterns)
    for route in patterns:
        if not isinstance(route, Route):
            raise ValueError("routes should be a list of Route")

        route.app_label = app_label

    return patterns


def path(
    path: str,
    *,
    endpoint: t.Coroutine | None = None,
    routes: t.Sequence[Route] | None = None,
    methods: t.Sequence[str] = None,
    name: str = None,
    app_label: str = None,
    middlewares: t.Sequence[t.Type[MiddleWare]] = None,
) -> Route | t.Sequence[Route]:
    """
    routes = [
        path("/foo", endpoint=home),
        path("/bar", routes=subpaths),
        path("/foobar", routes=include("module.routes.routes")),
    ]
    """
    if not (bool(endpoint) ^ bool(routes)):
        raise ValueError("Exactly one of 'endpoint' or 'routes' be provided")

    if endpoint:
        if inspect.iscoroutinefunction(endpoint):
            return Route(
                path,
                endpoint,
                methods=methods,
                name=name,
                middleware=middlewares,
                app_label=app_label,
            )
        else:
            raise ValueError(
                f"endpoint {endpoint.__name__} must be a coroutine function"
            )

    elif routes:
        ret = []
        for route in routes:
            if not isinstance(route, Route):
                raise ValueError("routes should be a list of Route")

            route.path = path + route.path
            route.path_regex, route.path_format, route.param_convertors = compile_path(
                route.path
            )
            route.load_middlewares(middlewares)

            if not route.app_label:
                route.app_label = app_label

            ret.append(route)

        return ret
