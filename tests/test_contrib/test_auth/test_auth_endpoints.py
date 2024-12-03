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
        resp = await request.post(
            "/api/contrib/auth/register", json={"account": "test", "password": "test"}
        )

        assert resp.status_code == 200

        resp = await request.post(
            "/api/contrib/auth/login", json={"account": "admin", "password": "admin"}
        )

        assert resp.status_code == 200
        assert "id" in resp.json()

        resp = await request.post(
            "/api/contrib/auth/logout", json={"platform": "default"}
        )
