import typing as t

import pytest
from starlette.types import Receive, Scope, Send

from unfazed.core import Unfazed
from unfazed.http import HttpRequest, HttpResponse
from unfazed.middleware import BaseMiddleware
from unfazed.route import Route, include, parse_urlconf, path


class TestInclude:
    patterns: t.List[Route] = []


class Middleware1(BaseMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        return await self.app(scope, receive, send)


def test_include() -> None:
    import_path = "tests.apps.route.include.nopatternroutes"

    with pytest.raises(ValueError):
        include(import_path)

    import_path = "tests.apps.route.include.invalidroutes"

    patterns = include(import_path)
    assert patterns == []

    import_path = "tests.test_route.entry.routes"

    patterns = include(import_path)

    assert len(patterns) == 4


async def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, World!")


def test_path_with_endpoints() -> None:
    route = path(
        "/foo",
        endpoint=view,
        methods=["GET", "POST"],
        name="foo",
        app_label="test_route",
        include_in_schema=False,
        tags=["foo", "bar"],
    )

    assert route.path == "/foo"
    assert route.endpoint == view
    assert route.methods == {"GET", "POST", "HEAD"}
    assert route.name == "foo"
    assert route.app_label == "test_route"
    assert route.include_in_schema is False
    assert route.tags == ["foo", "bar"]


def test_path_with_routes() -> None:
    routes = path(
        "/foo",
        routes=[path("/bar", endpoint=view)],
        middlewares=["tests.test_route.test_route_base.Middleware1"],
    )

    assert len(routes) == 1
    route = routes[0]
    assert route.path == "/foo/bar"
    assert route.app.__class__ == Middleware1


def test_failed_path() -> None:
    # test both endpoint and routes provided
    with pytest.raises(ValueError):
        subpaths = path("/bar", endpoint=view)
        path("/foo", endpoint=view, routes=[subpaths])  # type: ignore

    # test routes is not a list of Route
    with pytest.raises(ValueError):
        path("/foo", routes=[1, 2, 3])  # type: ignore

    # endpoint is not a function
    with pytest.raises(ValueError):
        path("/foo", endpoint="foo")  # type: ignore


def test_parse_urlconf(setup_route_unfazed: Unfazed) -> None:
    # normal case
    assert len(setup_route_unfazed.routes) == 4

    # failed case
    import_path = "tests.apps.route.include.nopatternroutes"
    app_center = {"not.existed.app": None}

    with pytest.raises(ValueError):
        parse_urlconf(import_path, app_center)  # type: ignore

    import_path = "tests.test_route.entry.routes"
    app_center = {"tests": None}

    with pytest.raises(ValueError):
        parse_urlconf(import_path, app_center)  # type: ignore


def test_route() -> None:
    with pytest.raises(ValueError):
        Route("foo", view)

    with pytest.raises(ValueError):
        Route("/foo", "foo")  # type: ignore

    route = Route(
        "/foo",
        view,
        middlewares=["tests.test_route.test_route_base.Middleware1"],
        methods=["GET", "POST"],
        tags=["foo", "bar"],
        name="foo",
        app_label="test_route",
    )

    assert route.path == "/foo"
    assert route.endpoint == view
    assert route.methods == {"GET", "POST", "HEAD"}
    assert route.name == "foo"
    assert route.app_label == "test_route"
    assert route.include_in_schema is True
    assert route.tags == ["foo", "bar"]
    assert route.path_format == "/foo"

    route.update_path("/foo/bar")

    assert route.path == "/foo/bar"
    assert route.path_format == "/foo/bar"

    route.update_label("test_route2")
    assert route.app_label == "test_route2"
