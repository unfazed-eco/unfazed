import typing as t
import uuid

import pytest_asyncio

from tests.apps.auth.models import User
from unfazed.conf import settings
from unfazed.contrib.auth.settings import UnfazedContribAuthSettings
from unfazed.contrib.session.settings import SessionSettings
from unfazed.core import Unfazed
from unfazed.test import Requestfactory


@pytest_asyncio.fixture(loop_scope="session")
async def setup_auth_endpoints_env():
    await User.all().delete()
    await User.create(account="admin", password="admin")
    yield
    await User.all().delete()


async def test_endpoints(
    setup_auth_endpoints_env: t.Generator, prepare_unfazed: Unfazed
):
    settings["UNFAZED_CONTRIB_AUTH_SETTINGS"] = UnfazedContribAuthSettings(
        **{
            "USER_MODEL": "tests.apps.auth.models.User",
            "BACKENDS": {
                "default": {
                    "BACKEND_CLS": "unfazed.contrib.auth.backends.default.DefaultAuthBackend",
                    "OPTIONS": {},
                }
            },
        }
    )

    settings["SESSION_SETTINGS"] = SessionSettings(
        SECRET=uuid.uuid4().hex, COOKIE_DOMAIN="garena.com", COOKIE_SECURE=True
    )

    async with Requestfactory(prepare_unfazed) as request:
        resp = await request.post(
            "/api/contrib/auth/register", json={"account": "test", "password": "test"}
        )
        assert resp.status_code == 200

        resp = await request.post(
            "/api/contrib/auth/login", json={"account": "admin", "password": "admin"}
        )

        assert resp.status_code == 200

        resp = await request.post(
            "/api/contrib/auth/logout", json={"platform": "default"}
        )
