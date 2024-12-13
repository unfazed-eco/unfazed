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
        assert "id" in resp_login.json()

        request.headers.setdefault("Cookie", resp_login.headers.get("Set-Cookie"))

        resp_logout = await request.post(
            "/api/contrib/auth/logout", json={"platform": "default"}
        )

        assert resp_logout.status_code == 200
        assert resp_logout.json() == {}

    async with Requestfactory(unfazed) as request2:
        resp_logout2 = await request2.post(
            "/api/contrib/auth/logout", json={"platform": "default"}
        )

        assert resp_logout2.status_code == 200
