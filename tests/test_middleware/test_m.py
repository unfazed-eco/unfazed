import typing as t

from tests.decorators import mock_unfazed_settings
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture

_Settings = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_launch",
    "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
    "ROOT_URLCONF": "tests.apps.middleware.routes",
    "MIDDLEWARE": [
        "tests.apps.middleware.middleware.set_session.SetSessionMiddleware",
        "tests.apps.middleware.middleware.set_user.SetUserMiddleware",
    ],
}


Settings = UnfazedSettings(**_Settings)


@mock_unfazed_settings(Settings)
async def test_middleware(mocker: "MockerFixture") -> None:
    unfazed = Unfazed()

    await unfazed.setup()
    assert len(unfazed.user_middleware) == 2

    # test middleware stack
    unfazed.build_middleware_stack()
