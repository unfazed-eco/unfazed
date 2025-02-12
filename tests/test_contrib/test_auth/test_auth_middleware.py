import typing as t
import uuid

import pytest

from unfazed.conf import settings
from unfazed.contrib.auth.middleware import AuthenticationMiddleware
from unfazed.contrib.auth.settings import AuthBackend, UnfazedContribAuthSettings
from unfazed.contrib.session.backends.default import SigningSession
from unfazed.contrib.session.settings import SessionSettings
from unfazed.core import Unfazed
from unfazed.http import HttpRequest, HttpResponse
from unfazed.route.routing import Route


async def receive(*args: t.Any, **kwargs: t.Any) -> t.Any:
    pass


async def send(*args: t.Any, **kwargs: t.Any) -> t.Any:
    pass


async def endpoint(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world!")


DEFAULT_SESSION_SETTINGS = {
    "SECRET": uuid.uuid4().hex,
    "COOKIE_DOMAIN": "unfazed.com",
    "COOKIE_SECURE": True,
}


@pytest.fixture(autouse=True)
def setup_middle_env() -> t.Generator:
    raw_auth_settings = None
    if "UNFAZED_CONTRIB_AUTH_SETTINGS" not in settings:
        raw_auth_settings = settings["UNFAZED_CONTRIB_AUTH_SETTINGS"]

    settings["UNFAZED_CONTRIB_AUTH_SETTINGS"] = UnfazedContribAuthSettings(
        BACKENDS={
            "default": AuthBackend(
                BACKEND_CLS="unfazed.contrib.auth.backends.DefaultAuthBackend",
                OPTIONS={},
            )
        },
        USER_MODEL="tests.apps.auth.common.models.User",
    )
    yield

    if raw_auth_settings is not None:
        settings["UNFAZED_CONTRIB_AUTH_SETTINGS"] = raw_auth_settings


async def test_auth_middleware() -> None:
    unfazed = Unfazed(routes=[Route("/", endpoint)])
    await unfazed.setup()

    m = AuthenticationMiddleware(unfazed)

    scope: t.Dict[str, t.Any] = {
        "type": "http",
        "http_version": "1.1",
        "user": None,
        "path": "/",
        "method": "GET",
        "headers": [],
    }

    await m(scope, receive, send)

    assert scope["user"] is None

    session = SigningSession(
        SessionSettings.model_validate(DEFAULT_SESSION_SETTINGS), "session_key"
    )

    await session.load()
    scope: t.Dict[str, t.Any] = {
        "type": "http",
        "http_version": "1.1",
        "session": session,
        "path": "/",
        "method": "GET",
        "headers": [],
    }

    await m(scope, receive, send)
    assert scope["user"] is None
