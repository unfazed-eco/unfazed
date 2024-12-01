import pytest

from tests.apps.auth.common.models import User
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
    await service.logout({"platform": "default"})
    await service.logout({})

    await service.login(
        LoginCtx(account="admin", password="admin", platform="notexisted")
    )


async def test_failed_load():
    auth_settings = UnfazedContribAuthSettings(
        USER_MODEL="tests.apps.auth.models.User",
        BACKENDS={
            "wrongbkd": {
                "BACKEND_CLS": "unfazed.contrib.auth.backends.default.DefaultAuthBackend",
                "OPTIONS  ": {},
            }
        },
    )

    with pytest.raises(ValueError):
        load_backends(auth_settings)
