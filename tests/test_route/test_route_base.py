import os
import typing as t

import pytest
from starlette.routing import Match

from unfazed.core import Unfazed
from unfazed.http import HttpRequest, HttpResponse
from unfazed.middleware import BaseMiddleware
from unfazed.route import (
    Convertor,
    Route,
    include,
    parse_urlconf,
    path,
    register_url_convertor,
    static,
)
from unfazed.test import Requestfactory
from unfazed.type import Receive, Scope, Send


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

    assert len(patterns) == 5


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
    assert route.app.__class__.__name__ == "Middleware1"


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
    assert len(setup_route_unfazed.routes) == 5

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
        operation_id="foo_operation",
    )

    assert route.path == "/foo"
    assert route.endpoint == view
    assert route.methods == {"GET", "POST", "HEAD"}
    assert route.name == "foo"
    assert route.app_label == "test_route"
    assert route.include_in_schema is True
    assert route.tags == ["foo", "bar"]
    assert route.path_format == "/foo"
    assert route.operation_id == "foo_operation"
    route.update_path("/foo/bar")

    assert route.path == "/foo/bar"
    assert route.path_format == "/foo/bar"

    route.update_label("test_route2")
    assert route.app_label == "test_route2"

    # test route match

    route2 = Route("/foo/{id}", view)

    scope1 = {
        "type": "http",
        "path": "/foo/1",
        "root_path": "",
        "method": "GET",
    }

    scope2 = {
        "type": "http",
        "path": "/foo/abc",
        "root_path": "",
        "method": "GET",
    }

    match, _ = route2.matches(scope1)
    assert match == Match.FULL

    match, _ = route2.matches(scope2)
    assert match == Match.FULL

    route3 = Route("/foo/{id:int}", view)
    match, _ = route3.matches(scope1)
    assert match == Match.FULL

    match, _ = route3.matches(scope2)
    assert match == Match.NONE


class LangConvertor(Convertor):
    regex = r"[-_a-zA-Z]+"

    def convert(self, value: str) -> str:
        return value

    def to_string(self, value: str) -> str:
        return value


def test_route_converter() -> None:
    register_url_convertor("lang", LangConvertor())

    route = Route("/foo/{lang:lang}", view)

    scope = {
        "type": "http",
        "path": "/foo/en",
        "root_path": "",
        "method": "GET",
    }

    match, _ = route.matches(scope)

    assert match == Match.FULL


async def test_staticfiles(setup_route_unfazed: Unfazed) -> None:
    async with Requestfactory(setup_route_unfazed) as request:
        response = await request.get("/static/js/foo.js")
        assert response.status_code == 200

        response = await request.get("/static/css/bar.css")
        assert response.status_code == 200

        response = await request.get("/static/nested/top/sub/bar.js")
        assert response.status_code == 200

        response = await request.get("/static/index.html")
        assert response.status_code == 200

        with pytest.raises(FileNotFoundError):
            await request.get("/static/not_found.html")


async def test_static() -> None:
    abs_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../staticfiles")
    )

    with pytest.raises(ValueError):
        static("static", abs_path)

    route = static("/static", abs_path)

    with pytest.raises(NotImplementedError):
        route.url_path_for("static")

    assert route.routes == []

    ret = route.matches(
        {"type": "unknown", "path": "/static/js/foo.js", "method": "GET"}
    )
    assert ret == (Match.NONE, {})

    route2 = static("/static", abs_path, app_label="test_route")
    assert route2.app_label == "test_route"

    route3 = static("/static", abs_path, tags=["foo", "bar"])
    assert route3.tags == ["foo", "bar"]
