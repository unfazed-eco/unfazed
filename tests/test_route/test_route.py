import pytest

from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed
from unfazed.route import Route, include, parse_urlconf, path

SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_setup_routes",
}


async def test_setup_routes():
    unfazed = Unfazed(settings=UnfazedSettings(**SETTINGS))

    unfazed.settings.ROOT_URLCONF = "tests.apps.route.routes"
    unfazed.settings.INSTALLED_APPS = ["tests.apps.route.common"]
    await unfazed.setup()

    assert len(unfazed.routes) == 4


class TestInclude:
    patterns = []


def test_include():
    import_path = "tests.apps.route.include.nopatternroutes"

    with pytest.raises(ValueError):
        include(import_path)

    import_path = "tests.apps.route.include.invalidroutes"

    with pytest.raises(ValueError):
        include(import_path)


def test_path():
    # test both endpoint and routes provided
    async def view(request):
        pass

    with pytest.raises(ValueError):
        subpaths = [path("/bar", endpoint=view)]
        path("/foo", endpoint=view, routes=subpaths)

    # test routes is not a list of Route
    with pytest.raises(ValueError):
        path("/foo", routes=[1, 2, 3])


def test_parse_urlconf():
    import_path = "tests.apps.route.include.nopatternroutes"
    app_center = {"not.existed.app": None}

    with pytest.raises(ValueError):
        parse_urlconf(import_path, app_center)

    import_path = "tests.apps.route.routes"
    app_center = {"tests": None}

    with pytest.raises(ValueError):
        parse_urlconf(import_path, app_center)


def test_raises():
    with pytest.raises(ValueError):
        Route("foo", endpoint=int)

    class Foo:
        pass

    with pytest.raises(ValueError):
        Route("/foo", endpoint=Foo)
