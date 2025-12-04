import typing as t

import pytest

from tests.apps.auth.common.models import User
from unfazed.core import Unfazed
from unfazed.test import Requestfactory


@pytest.fixture(autouse=True)
async def setup_auth_endpoints_env() -> t.AsyncGenerator[None, None]:
    await User.all().delete()
    await User.create(account="admin", password="admin")
    yield
    await User.all().delete()


async def test_endpoints(setup_auth_unfazed: Unfazed) -> None:
    unfazed = setup_auth_unfazed
    async with Requestfactory(unfazed) as request:
        resp_register = await request.post(
            "/api/contrib/auth/register", json={"account": "test", "password": "test"}
        )

        assert resp_register.status_code == 200

        resp_login = await request.post(
            "/api/contrib/auth/login", json={"account": "admin", "password": "admin"}
        )

        assert resp_login.status_code == 200
        res = resp_login.json()
        assert res["code"] == 0
        assert res["message"] == "success"
        assert res["data"]["account"] == "admin"
        assert res["data"]["email"] == ""
        assert res["data"]["is_superuser"] == 0
        assert res["data"]["platform"] == "default"

        request.headers.setdefault("Cookie", resp_login.headers.get("Set-Cookie"))

        resp_logout = await request.post(
            "/api/contrib/auth/logout", json={"platform": "default"}
        )

        assert resp_logout.status_code == 200
        res = resp_logout.json()
        assert res["code"] == 0
        assert res["message"] == "success"
        assert res["data"] == {}

        with pytest.raises(ValueError):
            await request.get(
                "/api/contrib/auth/oauth-login-redirect",
                params={"platform": "default"},
            )

        with pytest.raises(ValueError):
            await request.get(
                "/api/contrib/auth/oauth-logout-redirect",
                params={"platform": "default"},
            )

    async with Requestfactory(unfazed) as request2:
        resp_logout2 = await request2.post(
            "/api/contrib/auth/logout", json={"platform": "default"}
        )

        assert resp_logout2.status_code == 200
