import pytest

from tests.apps.auth.common.models import User
from unfazed.contrib.auth.backends import DefaultAuthBackend
from unfazed.contrib.auth.schema import LoginCtx, RegisterCtx
from unfazed.exception import AccountExisted, AccountNotFound, WrongPassword


@pytest.fixture(autouse=True)
async def setup_auth_backend_env():
    await User.all().delete()

    yield

    await User.all().delete()


async def test_default_backend() -> None:
    bkd = DefaultAuthBackend()

    assert bkd.alias == "default"

    u1 = await User.create(account="admin", password="admin")

    ctx = LoginCtx(account="admin", password="admin")

    session_info, resp = await bkd.login(ctx)

    assert session_info == {
        "id": u1.id,
        "account": u1.account,
        "email": u1.email,
        "is_superuser": u1.is_superuser,
        "platform": ctx.platform,
    }

    assert resp == session_info

    with pytest.raises(AccountNotFound):
        bkd1 = DefaultAuthBackend()
        await bkd1.login(LoginCtx(account="notexisted", password="admin"))

    with pytest.raises(WrongPassword):
        bkd2 = DefaultAuthBackend()
        await bkd2.login(LoginCtx(account="admin", password="wrongpassword"))

    # register
    ret = await bkd.register(
        RegisterCtx(account="test", password="test", extra={"email": "u@unfazed.com"})
    )

    assert ret == {}

    u2 = await User.get(account="test")

    assert u2.account == "test"
    assert u2.email == "u@unfazed.com"

    with pytest.raises(AccountExisted):
        bkd3 = DefaultAuthBackend()
        await bkd3.register(RegisterCtx(account="test", password="test"))

    with pytest.raises(WrongPassword):
        bkd4 = DefaultAuthBackend()
        await bkd4.register(RegisterCtx(account="test1", password=""))
