import typing as t

import pytest

from tests.apps.auth.common.models import Phone, User
from unfazed.contrib.admin.registry import (
    BaseModelAdmin,
    action,
    admin_collector,
    register,
)
from unfazed.contrib.auth.mixin import AuthMixin
from unfazed.http import HttpRequest
from unfazed.serializer import Serializer


@pytest.fixture(autouse=True)
async def setup_auth_mixin_env() -> t.AsyncGenerator:
    await Phone.all().delete()
    admin_collector.clear()

    class PhoneSerializer(Serializer):
        class Meta:
            model = Phone

    @register(PhoneSerializer)
    class PhoneAdmin(BaseModelAdmin, AuthMixin):
        @action(name="action1")
        def action1(self) -> None:
            pass

        @action(name="action2")
        def action2(self) -> None:
            pass

    yield

    await Phone.all().delete()


async def test_admin_mixin() -> None:
    phone_ins: AuthMixin = admin_collector["PhoneAdmin"]

    assert phone_ins.view_permission == "models.unfazed_auth_phone.can_view"
    assert phone_ins.create_permission == "models.unfazed_auth_phone.can_create"
    assert phone_ins.change_permission == "models.unfazed_auth_phone.can_change"
    assert phone_ins.delete_permission == "models.unfazed_auth_phone.can_delete"

    assert sorted(phone_ins.get_all_permissions()) == sorted(
        [
            "models.unfazed_auth_phone.can_view",
            "models.unfazed_auth_phone.can_create",
            "models.unfazed_auth_phone.can_change",
            "models.unfazed_auth_phone.can_delete",
            "models.unfazed_auth_phone.can_exec_action1",
            "models.unfazed_auth_phone.can_exec_action2",
        ]
    )

    class Request:
        user = User(is_superuser=True)

    request = t.cast(HttpRequest, Request())

    assert await phone_ins.has_view_permission(request) is True
    assert await phone_ins.has_create_permission(request) is True
    assert await phone_ins.has_change_permission(request) is True
    assert await phone_ins.has_delete_permission(request) is True
    assert await phone_ins.has_action_permission(request, "action1") is True
