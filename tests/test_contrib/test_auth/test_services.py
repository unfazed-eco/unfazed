import typing as t

import pytest

from tests.apps.auth.common.models import User
from unfazed.contrib.auth.schema import LoginCtx, RegisterCtx
from unfazed.contrib.auth.services import AuthService, load_backends
from unfazed.contrib.auth.settings import AuthBackend, UnfazedContribAuthSettings


@pytest.fixture(autouse=True)
async def setup_auth_service_env() -> t.AsyncGenerator:
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

    oauth_login_ret = await service.oauth_login_redirect("default")
    assert oauth_login_ret == ""
    oauth_logout_ret = await service.oauth_logout_redirect("default")
    assert oauth_logout_ret == ""


async def test_failed_load() -> None:
    auth_settings = UnfazedContribAuthSettings(
        USER_MODEL="tests.apps.auth.models.User",
        BACKENDS={
            "wrongbkd": AuthBackend(
                BACKEND_CLS="unfazed.contrib.auth.backends.default.DefaultAuthBackend",
                OPTIONS={},
            )
        },
    )

    with pytest.raises(ValueError):
        load_backends(auth_settings)
