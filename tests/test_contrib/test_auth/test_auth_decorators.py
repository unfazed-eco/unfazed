import httpx
import pytest

from tests.apps.auth.common.models import User
from unfazed.contrib.auth.models import Permission, Role
from unfazed.core import Unfazed
from unfazed.exception import LoginRequired, PermissionDenied
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
        yield request


@pytest.fixture
async def logged_with_permission_request(setup_auth_unfazed: Unfazed):
    u1 = await User.create(account="auth_decorator2", password="auth_decorator2")
    r1 = await Role.create(name="auth_decorator")
    p1 = await Permission.create(access="auth.async_permission_succeed.can_access")
    p2 = await Permission.create(access="auth.permission_succeed.can_access")

    await r1.permissions.add(p1)
    await r1.permissions.add(p2)
    await u1.roles.add(r1)

    async with Requestfactory(setup_auth_unfazed) as request:
        resp = await request.post(
            "/api/contrib/auth/login",
            json={"account": "auth_decorator2", "password": "auth_decorator2"},
        )
        request.headers.setdefault("Cookie", resp.headers.get("Set-Cookie"))
        yield request


async def test_logged_decorators(logged_request: httpx.AsyncClient) -> None:
    await logged_request.get("/api/tests/auth/async-login-succeed")
    await logged_request.get("/api/tests/auth/login-succeed")

    with pytest.raises(PermissionDenied):
        await logged_request.get("/api/tests/auth/async-permission-fail")

    with pytest.raises(PermissionDenied):
        await logged_request.get("/api/tests/auth/permission-fail")


async def test_logged_fail_decorators(setup_auth_unfazed: Unfazed) -> None:
    async with Requestfactory(setup_auth_unfazed) as request:
        with pytest.raises(LoginRequired):
            await request.get("/api/tests/auth/async-login-fail")

        with pytest.raises(LoginRequired):
            await request.get("/api/tests/auth/login-fail")


async def test_logged_with_permission_decorators(
    logged_with_permission_request: httpx.AsyncClient,
) -> None:
    request = logged_with_permission_request
    await request.get("/api/tests/auth/async-permission-succeed")
    await request.get("/api/tests/auth/permission-succeed")
