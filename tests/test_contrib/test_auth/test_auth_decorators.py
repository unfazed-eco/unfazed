import httpx
import pytest

from tests.apps.auth.common.models import User
from unfazed.core import Unfazed
from unfazed.test import Requestfactory


@pytest.fixture
async def logged_request(setup_auth_unfazed: Unfazed):
    await User.create(account="auth_decorator", password="auth_decorator")
    async with Requestfactory(setup_auth_unfazed) as request:
        resp = await request.post(
            "/api/contrib/auth/login",
            json={"account": "auth_decorator", "password": "auth_decorator"},
        )
        request.headers.setdefault("Cookie", resp.headers.get("Set-Cookie"))
        print(f"headers: {request.headers}")
        yield request


async def test_auth_decorators(logged_request: httpx.AsyncClient) -> None:
    await logged_request.get("/api/tests/auth/async-login-succeed")
