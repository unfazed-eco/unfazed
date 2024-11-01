import asyncio
import uuid

from unfazed.contrib.session.backends.default import SigningSession
from unfazed.contrib.session.settings import SessionSettings

SESSION_KEY1 = "unfazed_session_key1"
SESSION_KEY2 = "unfazed_session_key2"


async def test_default():
    # set session
    secret_key = uuid.uuid4().hex
    session_setting = SessionSettings(SECRET=secret_key, COOKIE_DOMAIN="garena.com")

    session = SigningSession(session_setting=session_setting, session_key=None)

    await session.load()

    assert bool(session) is False

    session[SESSION_KEY1] = {"foo": "bar"}

    assert session.modified is True
    await session.save()

    assert session.session_key is not None

    # get session
    session2 = SigningSession(
        session_setting=session_setting, session_key=session.session_key
    )

    await session2.load()

    assert bool(session2) is True

    assert SESSION_KEY1 in session2
    assert session2[SESSION_KEY1] == {"foo": "bar"}
    assert session2.modified is False

    assert session2.get_expiry_age() is None

    # update session
    del session2[SESSION_KEY1]
    session2[SESSION_KEY2] = {"bar": "foo"}
    assert session2.modified is True

    # delete session
    await session2.flush()
    assert session2.modified is True
    await session2.save()
    assert bool(session2) is False
    assert session2.modified is False
    assert session2.get_expiry_age() == "expires=Thu, 01 Jan 1970 00:00:00 GMT; "

    # failed case
    session3 = SigningSession(
        session_setting=session_setting, session_key="invalid_session_key"
    )

    await session3.load()

    assert bool(session3) is False
    assert session3._session == {}

    # ----- expire case

    session_setting.cookie_max_age = 1
    session4 = SigningSession(session_setting=session_setting, session_key=None)

    await session4.load()
    session4[SESSION_KEY1] = {"foo": "bar"}
    await session4.save()

    await asyncio.sleep(2)

    session4_key = session4.session_key

    session5 = SigningSession(session_setting=session_setting, session_key=session4_key)
    assert session5.get_max_age() == 1
    await session5.load()

    assert bool(session5) is False
    assert session5._session == {}
