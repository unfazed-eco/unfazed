from uuid import uuid4

import pytest
from pydantic import BaseModel

from unfazed.contrib.session.backends.default import SigningSession
from unfazed.contrib.session.settings import SessionSettings
from unfazed.core import Unfazed
from unfazed.http import HttpRequest


class User(BaseModel):
    id: int
    account: str


session_settings = SessionSettings(SECRET=uuid4().hex)

RAMDOM_KEY = uuid4().hex


async def test_http_request() -> None:
    http_scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/api",
        "query_string": b"",
        "headers": [
            (b"host", b"localhost"),
            (b"user-agent", b"Mozilla/5.0"),
        ],
        "user": User(id=1, account="tom"),
        "session": SigningSession(session_settings, session_key=RAMDOM_KEY),
        "app": Unfazed(),
    }

    request = HttpRequest(http_scope)
    request._body = b'{"a": 1}'

    assert request.scheme == "http"
    assert request.path == "/api"
    assert request.user.id == 1
    assert request.user.account == "tom"

    assert request.session.session_key == RAMDOM_KEY

    assert request.unfazed is not None

    assert await request.json() == {"a": 1}


async def test_http_failed() -> None:
    http_scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/api",
        "query_string": b"",
        "headers": [
            (b"host", b"localhost"),
            (b"user-agent", b"Mozilla/5.0"),
        ],
    }

    request = HttpRequest(http_scope)

    with pytest.raises(ValueError):
        _ = request.session

    with pytest.raises(ValueError):
        _ = request.user
