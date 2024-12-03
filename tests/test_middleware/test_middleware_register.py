from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

_Settings = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_launch",
    "ROOT_URLCONF": "tests.apps.middleware.routes",
    "MIDDLEWARE": [
        "tests.apps.middleware.middleware.set_session.SetSessionMiddleware",
        "tests.apps.middleware.middleware.set_user.SetUserMiddleware",
    ],
}


async def test_middleware() -> None:
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(_Settings))

    await unfazed.setup()
    assert len(unfazed.user_middleware) == 2

    # test middleware stack
    unfazed.build_middleware_stack()
