import typing as t

import pytest
from starlette.types import Receive, Scope, Send

from unfazed.http import HttpRequest, HttpResponse
from unfazed.middleware import BaseMiddleware
from unfazed.route import Route, include, parse_urlconf, path


class TestInclude:
    patterns: t.List[Route] = []


def test_include() -> None:
    import_path = "tests.apps.route.include.nopatternroutes"

    with pytest.raises(ValueError):
        include(import_path)

    import_path = "tests.apps.route.include.invalidroutes"

    # with pytest.raises(ValueError):
    #     include(import_path)
    patterns = include(import_path)
    assert patterns == []

    import_path = "tests.apps.route.routes"

    patterns = include(import_path)

    assert len(patterns) == 4


async def view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, World!")


def test_path() -> None:
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


def test_parse_urlconf() -> None:
    import_path = "tests.apps.route.include.nopatternroutes"
    app_center = {"not.existed.app": None}

    with pytest.raises(ValueError):
        parse_urlconf(import_path, app_center)  # type: ignore

    import_path = "tests.apps.route.routes"
    app_center = {"tests": None}

    with pytest.raises(ValueError):
        parse_urlconf(import_path, app_center)  # type: ignore


class Middleware1(BaseMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        return await self.app(scope, receive, send)


def test_route() -> None:
    with pytest.raises(ValueError):
        Route("foo", view)

    with pytest.raises(ValueError):
        Route("/foo", "foo")  # type: ignore

    route = Route("/foo", view, middlewares=[Middleware1])

    assert route.app.__class__ == Middleware1
