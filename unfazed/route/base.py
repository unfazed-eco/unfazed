import inspect
import typing as t
from importlib import import_module

from unfazed.type import ASGIApp, CanBeImported, HttpMethod

from .registry import _flatten_patterns
from .routing import Mount, Route, Static


def include(route_path: str) -> t.List[Route]:
    """
    Convert a route module path to a list of Route.

    Raises:
        ValueError: If the route module does not have a 'patterns' list.
        ValueError: If the route module does not have a list of Route.

    Usage:

    ```python

    from unfazed.route import include, path

    patterns = [
        path("/foo", routes=include("module.routes")),
    ]


    ```

    """
    route_module = import_module(route_path)
    app_label = route_path.rsplit(".", 1)[0]

    if not hasattr(route_module, "patterns"):
        raise ValueError(f"{route_path} must have a 'patterns' list")

    patterns = _flatten_patterns(route_module.patterns)
    for route in patterns:
        route.update_label(app_label)

    return patterns


@t.overload
def path(
    path: str,
    *,
    endpoint: t.Callable,
    methods: t.List[HttpMethod] | None = None,
    name: str | None = None,
    app_label: str | None = None,
    middlewares: t.List[CanBeImported] | None = None,
    include_in_schema: bool = True,
    tags: t.List[str] | None = None,
    summary: str | None = None,
    description: str | None = None,
    externalDocs: t.Dict | None = None,
    deprecated: bool = False,
    operation_id: str | None = None,
) -> Route: ...


@t.overload
def path(
    path: str,
    *,
    routes: t.List[Route] | None = None,
    methods: t.List[HttpMethod] | None = None,
    name: str | None = None,
    app_label: str | None = None,
    middlewares: t.List[CanBeImported] | None = None,
    include_in_schema: bool = True,
    tags: t.List[str] | None = None,
    summary: str | None = None,
    description: str | None = None,
    externalDocs: t.Dict | None = None,
    deprecated: bool = False,
    operation_id: str | None = None,
) -> t.List[Route]: ...


def path(
    path: str,
    *,
    endpoint: t.Callable | None = None,
    routes: t.List[Route] | None = None,
    methods: t.List[HttpMethod] | None = None,
    name: str | None = None,
    app_label: str | None = None,
    middlewares: t.List[CanBeImported] | None = None,
    include_in_schema: bool = True,
    tags: t.List[str] | None = None,
    summary: str | None = None,
    description: str | None = None,
    externalDocs: t.Dict | None = None,
    deprecated: bool | None = None,
    operation_id: str | None = None,
) -> Route | t.List[Route]:
    """

    Create a Route or a list of Route.

    Raises:
        ValueError: If exactly one of 'endpoint' or 'routes' is not provided.
        ValueError: If 'endpoint' is not a function.

    Usage:

    ```python
    from unfazed.route import path, include

    routes = [
        path("/foo", endpoint=home),
        path("/bar", routes=subpaths),
        path("/foobar", routes=include("module.routes.routes")),
    ]
    ```
    """
    if not (bool(endpoint) ^ bool(routes)):
        raise ValueError(
            f"error for {path}: Exactly one of 'endpoint' or 'routes' be provided"
        )

    if endpoint:
        if inspect.isfunction(endpoint):
            return Route(
                path,
                endpoint,
                methods=methods,
                name=name,
                middlewares=middlewares,
                app_label=app_label,
                include_in_schema=include_in_schema,
                tags=tags,
                summary=summary,
                description=description,
                externalDocs=externalDocs,
                deprecated=deprecated,
                operation_id=operation_id,
            )

        else:
            raise ValueError(f"endpoint {endpoint} must be a function")

    elif routes:
        ret = []
        for route in routes:
            if not isinstance(route, Route):
                raise ValueError(f"error for {path}: routes should be a list of Route")

            route.update_path(path + route.path)
            if middlewares:
                route.load_middlewares(middlewares)

            if not route.app_label:
                route.app_label = app_label

            ret.append(route)

        return ret

    # comply with mypy check
    # never reach here
    else:
        return []  # pragma: no cover


def static(
    path: str,
    directory: str,
    *,
    name: str | None = None,
    app_label: str | None = None,
    html: bool = False,
) -> Static:
    return Static(
        path=path,
        directory=directory,
        name=name,
        html=html,
        app_label=app_label,
    )


def mount(
    path: str,
    app: ASGIApp | None = None,
    routes: t.List[Route] | None = None,
    *,
    name: str | None = None,
    app_label: str | None = None,
    middlewares: t.List[CanBeImported] | None = None,
) -> Mount:
    """
    Create a Mount.

    Usage:

    ```python
    from unfazed.route import mount

    app = Starlette()

    routes = [
        mount("/foo", app=app),
        mount("/bar", routes=subpaths),
    ]

    ```
    """
    return Mount(
        path,
        app,
        routes,
        name=name,
        app_label=app_label,
        middlewares=middlewares,
    )
