import os
import typing as t

import pytest
from tortoise import Tortoise

from tests.apps.admin.registry.models import (
    T1Book,
    T1Profile,
    T1Role,
    T1User,
    T1UserRole,
    T2Book,
    T2Profile,
    T2Role,
    T2User,
    T2UserRole,
)
from unfazed.conf import settings
from unfazed.contrib.admin.registry import (
    AdminRelation,
    AdminThrough,
    ModelAdmin,
    ModelInlineAdmin,
    admin_collector,
    register,
)
from unfazed.core import Unfazed
from unfazed.serializer import Serializer


@pytest.fixture(scope="package", autouse=True)
async def setup_admin_unfazed() -> t.AsyncGenerator[Unfazed, None]:
    # clear Tortoise apps
    Tortoise.apps = {}
    Tortoise._inited = False
    os.environ["UNFAZED_SETTINGS_MODULE"] = (
        "tests.test_contrib.test_admin.entry.settings"
    )

    settings.clear()

    unfazed = Unfazed()

    await unfazed.setup()

    await unfazed.migrate()

    yield unfazed


@pytest.fixture
def setup_inline() -> None:
    admin_collector.clear()

    # with relation fields
    class T1UserSerializer(Serializer):
        class Meta:
            model = T1User

    class T1RoleSerializer(Serializer):
        class Meta:
            model = T1Role

    class T1UserRoleSerializer(Serializer):
        class Meta:
            model = T1UserRole

    class T1ProfileSerializer(Serializer):
        class Meta:
            model = T1Profile

    class T1BookSerializer(Serializer):
        class Meta:
            model = T1Book

    @register(T1UserSerializer)
    class T1UserAdmin(ModelAdmin):
        inlines = [
            AdminRelation(target="T1BookAdmin"),
            AdminRelation(target="T1ProfileAdmin"),
            AdminRelation(
                target="T1RoleAdmin",
                through=AdminThrough(
                    through="T1UserRoleAdmin",
                    source_field="id",
                    source_to_through_field="user_id",
                    target_field="id",
                    target_to_through_field="role_id",
                ),
            ),
        ]

    @register(T1RoleSerializer)
    class T1RoleAdmin(ModelInlineAdmin):
        pass

    @register(T1UserRoleSerializer)
    class T1UserRoleAdmin(ModelInlineAdmin):
        pass

    @register(T1ProfileSerializer)
    class T1ProfileAdmin(ModelInlineAdmin):
        pass

    @register(T1BookSerializer)
    class T1BookAdmin(ModelInlineAdmin):
        pass

    # with relation fields

    class T2UserSerializer(Serializer):
        class Meta:
            model = T2User

    class T2RoleSerializer(Serializer):
        class Meta:
            model = T2Role

    class T2UserRoleSerializer(Serializer):
        class Meta:
            model = T2UserRole

    class T2ProfileSerializer(Serializer):
        class Meta:
            model = T2Profile

    class T2BookSerializer(Serializer):
        class Meta:
            model = T2Book

    @register(T2UserSerializer)
    class T2UserAdmin(ModelAdmin):
        inlines = [
            AdminRelation(
                target="T2BookAdmin",
                source_field="id",
                target_field="owner_id",
                relation="bk_fk",
            ),
            AdminRelation(
                target="T2ProfileAdmin",
                source_field="id",
                target_field="user_id",
                relation="bk_o2o",
            ),
            AdminRelation(
                target="T2RoleAdmin",
                relation="m2m",
                through=AdminThrough(
                    through="T2UserRoleAdmin",
                    source_field="id",
                    source_to_through_field="user_id",
                    target_field="id",
                    target_to_through_field="role_id",
                ),
            ),
        ]

    @register(T2RoleSerializer)
    class T2RoleAdmin(ModelInlineAdmin):
        pass

    @register(T2UserRoleSerializer)
    class T2UserRoleAdmin(ModelInlineAdmin):
        pass

    @register(T2ProfileSerializer)
    class T2ProfileAdmin(ModelInlineAdmin):
        pass

    @register(T2BookSerializer)
    class T2BookAdmin(ModelInlineAdmin):
        pass
