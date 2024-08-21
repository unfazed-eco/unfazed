import typing as t

import pytest

from unfazed import utils
from unfazed.core import Unfazed
from unfazed.route import include, parse_urlconf, path

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture  # pragma: no cover


def test_setup_routes(mocker: "MockerFixture"):
    return_value = {
        "UNFAZED_SETTINGS": {
            "DEBUG": True,
            "PROJECT_NAME": "test_setup_routes",
            "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
        }
    }
    with mocker.patch.object(utils, "import_setting", return_value=return_value):
        unfazed = Unfazed()

        unfazed.settings.ROOT_URLCONF = "tests.test_application.routeapp.routes"
        unfazed.settings.INSTALLED_APPS = ["tests.test_application.success"]
        unfazed.setup()

        assert len(unfazed.routes) == 4


class TestInclude:
    patterns = []


def test_include():
    import_path = "tests.test_application.mainapp.nopatternroutes"

    with pytest.raises(ValueError):
        include(import_path)

    import_path = "tests.test_application.mainapp.invalidroutes"

    with pytest.raises(ValueError):
        include(import_path)


def test_path():
    # test both endpoint and routes provided
    async def view(request):
        pass

    with pytest.raises(ValueError):
        subpaths = [path("/bar", endpoint=view)]
        path("/foo", endpoint=view, routes=subpaths)

    # test endpoint is not a coroutine
    with pytest.raises(ValueError):
        path("/foo", endpoint=int)

    # test routes is not a list of Route
    with pytest.raises(ValueError):
        path("/foo", routes=[1, 2, 3])


def test_parse_urlconf():
    import_path = "tests.test_application.mainapp.nopatternroutes"
    app_center = {"tests.test_application.success": None}

    with pytest.raises(ValueError):
        parse_urlconf(import_path, app_center)

    import_path = "tests.test_application.routeapp.routes"
    app_center = {"tests": None}

    with pytest.raises(ValueError):
        parse_urlconf(import_path, app_center)


