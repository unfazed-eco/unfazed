import pytest

from tests.apps.auth.models import User
from unfazed.conf import settings
from unfazed.contrib.auth.schema import LoginCtx, RegisterCtx
from unfazed.contrib.auth.services import AuthService, load_backends
from unfazed.contrib.auth.settings import UnfazedContribAuthSettings


@pytest.fixture(autouse=True)
async def setup_auth_service_env():
    await User.all().delete()
    await User.create(account="admin", password="admin")
    yield
    await User.all().delete()


async def test_authservice() -> None:
    service = AuthService()

    await service.register(RegisterCtx(account="test", password="test"))
    assert await User.get_or_none(account="test")

    await service.login(LoginCtx(account="admin", password="admin"))
    await service.logout({"paltform": "default"})

    await service.login(
        LoginCtx(account="admin", password="admin", platform="notexisted")
    )


# async def test_failed_load():
#     settings["UNFAZED_CONTRIB_AUTH_SETTINGS"] = UnfazedContribAuthSettings(
#         USER_MODEL="tests.apps.auth.models.User",
#         BACKENDS={
#             "wrongbkd": {
#                 "BACKEND_CLS": "unfazed.contrib.auth.backends.default.DefaultAuthBackend",
#                 "OPTIONS  ": {},
#             }
#         },
#     )

#     load_backends.cache_clear()

#     with pytest.raises(ValueError):
#         AuthService()
