import typing as t
from io import StringIO
from unittest.mock import patch

import pytest

from unfazed.command.internal.create_superuser import Command
from unfazed.contrib.auth.models import AbstractUser
from unfazed.core import Unfazed


@pytest.fixture
async def setup_auth_models_env() -> t.AsyncGenerator[None, None]:
    UserCls = AbstractUser.UserCls()
    await UserCls.all().delete()
    yield
    await UserCls.all().delete()


async def test_create_superuser_success(
    setup_auth_models_env: t.AsyncGenerator[None, None],
) -> None:
    unfazed = Unfazed()

    email = "test@example.com"
    command = Command(unfazed, "create-superuser", "internal")

    captured_output = StringIO()
    with patch("unfazed.command.internal.create_superuser.sys.stdout", captured_output):
        await command.handle(email=email)

    output = captured_output.getvalue()
    assert f"Superuser created: {email} with password:" in output

    UserCls = AbstractUser.UserCls()
    user = await UserCls.filter(email=email).first()
    assert user is not None
    assert user.email == email
    assert user.account == email
    assert user.is_superuser == 1
    assert len(user.password) == 6

    assert all(
        c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        for c in user.password
    )


async def test_create_superuser_already_exists(
    setup_auth_models_env: t.AsyncGenerator[None, None],
) -> None:
    unfazed = Unfazed()

    email = "existing@example.com"
    UserCls = AbstractUser.UserCls()

    await UserCls.create(
        email=email,
        account=email,
        is_superuser=0,
        password="existing_password",
    )

    command = Command(unfazed, "create-superuser", "internal")

    captured_output = StringIO()
    with patch("unfazed.command.internal.create_superuser.sys.stdout", captured_output):
        await command.handle(email=email)

    output = captured_output.getvalue()
    assert f"Superuser already exists: {email}\n" == output

    user = await UserCls.filter(email=email).first()
    assert user is not None
    assert user.password == "existing_password"
    assert user.is_superuser == 0


async def test_create_superuser_multiple_calls(
    setup_auth_models_env: t.AsyncGenerator[None, None],
) -> None:
    unfazed = Unfazed()

    email1 = "user1@example.com"
    email2 = "user2@example.com"
    command = Command(unfazed, "create-superuser", "internal")

    captured_output1 = StringIO()
    with patch(
        "unfazed.command.internal.create_superuser.sys.stdout", captured_output1
    ):
        await command.handle(email=email1)

    captured_output2 = StringIO()
    with patch(
        "unfazed.command.internal.create_superuser.sys.stdout", captured_output2
    ):
        await command.handle(email=email2)

    UserCls = AbstractUser.UserCls()
    user1 = await UserCls.filter(email=email1).first()
    user2 = await UserCls.filter(email=email2).first()

    assert user1 is not None
    assert user2 is not None
    assert user1.is_superuser == 1
    assert user2.is_superuser == 1
    assert user1.password != user2.password
