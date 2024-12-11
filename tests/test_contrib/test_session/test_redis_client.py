import asyncio
import os
import uuid

import pytest

from unfazed.cache import caches
from unfazed.cache.backends.redis import SerializerBackend
from unfazed.contrib.session.backends.cache import CacheSession
from unfazed.contrib.session.settings import SessionSettings

SESSION_KEY1 = "unfazed_session_key1"
SESSION_KEY2 = "unfazed_session_key2"
HOST = os.getenv("REDIS_HOST", "redis")


async def test_redis_client() -> None:
    caches["default"] = SerializerBackend(
        location=f"redis://{HOST}:6379",
        options={"PREFIX": "test_redis_client"},
    )

    session_setting = SessionSettings(CACHE_ALIAS="default", SECRET=uuid.uuid4().hex)
    session = CacheSession(session_setting=session_setting, session_key=None)

    # set session

    await session.load()
    session[SESSION_KEY1] = {"foo": "bar"}

    assert session.modified is True

    await session.save()
    assert bool(session) is True
    assert session.session_key is not None

    # get session

    session2 = CacheSession(
        session_setting=session_setting, session_key=session.session_key
    )

    await session2.load()
    assert session[SESSION_KEY1] == {"foo": "bar"}

    assert session2.modified is False
    assert session2.get_expiry_age() is None

    # update session
    del session2[SESSION_KEY1]
    session2[SESSION_KEY2] = {"foo2": "bar2"}

    assert session2.modified is True

    await session2.save()

    # get session
    session3 = CacheSession(
        session_setting=session_setting, session_key=session.session_key
    )

    await session3.load()
    assert session3[SESSION_KEY2] == {"foo2": "bar2"}

    # delete session
    await session3.flush()

    assert session3.modified is True
    await session3.save()

    assert bool(session3) is False

    # expired case
    session_setting.cookie_max_age = 1
    session4 = CacheSession(session_setting=session_setting, session_key=None)
    await session4.load()
    session4[SESSION_KEY1] = {"foo": "bar"}
    await session4.save()

    await asyncio.sleep(1.5)

    await session4.load()
    assert bool(session4) is False
    assert session4._session == {}

    # failed to init
    with pytest.raises(ValueError):
        session_setting.cache_alias = ""
        CacheSession(session_setting=session_setting, session_key=None)

    with pytest.raises(ValueError):
        session_setting.cache_alias = "invalid"
        CacheSession(session_setting=session_setting, session_key=None)

    await caches["default"].close()
