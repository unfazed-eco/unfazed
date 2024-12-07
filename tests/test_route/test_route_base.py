import pytest

from unfazed.http import HttpRequest, HttpResponse
from unfazed.middleware import BaseHttpMiddleware
from unfazed.route import Route, include, parse_urlconf, path


class TestInclude:
    patterns = []


def test_include():
    import_path = "tests.apps.route.include.nopatternroutes"

    with pytest.raises(ValueError):
        include(import_path)

    import_path = "tests.apps.route.include.invalidroutes"

    with pytest.raises(ValueError):
        include(import_path)

    import_path = "tests.apps.route.routes"

    patterns = include(import_path)

    assert len(patterns) == 4


async def view(request: HttpRequest) -> HttpResponse:
    return "Hello, World!"


def test_path():
    # test both endpoint and routes provided
    with pytest.raises(ValueError):
        subpaths = path("/bar", endpoint=view)
        path("/foo", endpoint=view, routes=[subpaths])

    # test routes is not a list of Route
    with pytest.raises(ValueError):
        path("/foo", routes=[1, 2, 3])

    # endpoint is not a function
    with pytest.raises(ValueError):
        path("/foo", endpoint="foo")


def test_parse_urlconf():
    import_path = "tests.apps.route.include.nopatternroutes"
    app_center = {"not.existed.app": None}

    with pytest.raises(ValueError):
        parse_urlconf(import_path, app_center)

    import_path = "tests.apps.route.routes"
    app_center = {"tests": None}

    with pytest.raises(ValueError):
        parse_urlconf(import_path, app_center)


class Middleware1(BaseHttpMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        return response


def test_route():
    with pytest.raises(ValueError):
        Route("foo", view)

    with pytest.raises(ValueError):
        Route("/foo", "foo")

    route = Route("/foo", view, middleware=[Middleware1])

    assert route.app.__class__ == Middleware1
