import typing as t

from unfazed.contrib.admin.registry import (
    ActionKwargs,
    AdminRelation,
    AdminThrough,
    CustomAdmin,
    ModelAdmin,
    ModelInlineAdmin,
    action,
    admin_collector,
    register,
)

from . import models as m
from . import serializers as s
from .mixin import AuthMixin

# User Admin


@register(s.UserSerializer)
class UserAdmin(ModelAdmin, AuthMixin):
    list_display = ["id", "account", "email", "is_superuser"]
    detail_display = ["id", "account", "email", "is_superuser", "password"]

    search_fields = ["account", "email"]
    can_search = True

    inlines = [
        AdminRelation(
            target="InlineGroupUnderUserAdmin",
            relation="m2m",
            through=AdminThrough(
                through="InlineGroupUnderUserAdmin",
                source_field="id",
                source_to_through_field="user_id",
                target_to_through_field="group_id",
                target_field="id",
            ),
        ),
        AdminRelation(
            target="InlineUserRoleUnderUserAdmin",
            relation="m2m",
            through=AdminThrough(
                through="InlineUserRoleUnderUserAdmin",
                source_field="id",
                source_to_through_field="user_id",
                target_to_through_field="role_id",
                target_field="id",
            ),
        ),
    ]


@register(s.GroupSerializer)
class InlineGroupUnderUserAdmin(ModelInlineAdmin):
    pass


@register(s.UserGroupSerializer)
class InlineUserGroupUnderUserAdmin(ModelInlineAdmin):
    pass


@register(s.RoleSerializer)
class InlineRoleUnderUserAdmin(ModelInlineAdmin):
    pass


@register(s.UserRoleSerializer)
class InlineUserRoleUnderUserAdmin(ModelInlineAdmin):
    pass


# Group Admin


@register(s.GroupSerializer)
class GroupAdmin(ModelAdmin, AuthMixin):
    search_fields = ["name"]
    can_search = True

    inlines = [
        AdminRelation(
            target="InlineRoleUnderGroupAdmin",
            relation="m2m",
            through=AdminThrough(
                through="InlineGroupRoleUnderGroupAdmin",
                source_field="id",
                source_to_through_field="group_id",
                target_to_through_field="role_id",
                target_field="id",
            ),
        ),
        AdminRelation(
            target="InlineUserUnderGroupAdmin",
            relation="m2m",
            through=AdminThrough(
                through="InlineUserGroupUnderGroupAdmin",
                source_field="id",
                source_to_through_field="group_id",
                target_to_through_field="user_id",
                target_field="id",
            ),
        ),
    ]


@register(s.UserSerializer)
class InlineUserUnderGroupAdmin(ModelInlineAdmin):
    pass


@register(s.RoleSerializer)
class InlineRoleUnderGroupAdmin(ModelInlineAdmin):
    pass


@register(s.UserGroupSerializer)
class InlineUserGroupUnderGroupAdmin(ModelInlineAdmin):
    pass


@register(s.GroupRoleSerializer)
class InlineGroupRoleUnderGroupAdmin(ModelInlineAdmin):
    pass


# Role Admin


@register(s.RoleSerializer)
class RoleAdmin(ModelAdmin, AuthMixin):
    search_fields = ["name"]
    can_search = True

    inlines = [
        AdminRelation(
            target="InlinePermissionUnderRoleAdmin",
            relation="m2m",
            through=AdminThrough(
                through="InlineRolePermissionUnderRoleAdmin",
                source_field="id",
                source_to_through_field="role_id",
                target_to_through_field="permission_id",
                target_field="id",
            ),
        ),
    ]


@register(s.PermissionSerializer)
class InlinePermissionUnderRoleAdmin(ModelInlineAdmin):
    pass


@register(s.RolePermissionSerializer)
class InlineRolePermissionUnderRoleAdmin(ModelInlineAdmin):
    pass


# Permission Admin


@register(s.PermissionSerializer)
class PermissionAdmin(ModelAdmin, AuthMixin):
    search_fields = ["access"]
    can_search = True

    @action(
        name="sync_permission",
        label="Sync Permissions",
        description="Init or Update permissions to all admin models",
        batch=True,
        confirm=True,
    )
    async def sync_permissions(
        self,
        ctx: ActionKwargs,
    ) -> str:
        """
        Init or Update permissions to all admin models.

        This action will init or update permissions to all admin models.

        If the permission is not exist, it will be created.
        If the permission is exist, it will be updated.

        The permission is a string like "admin.view_user", "admin.change_user", "admin.delete_user".
        """

        admin_instance: t.Union[ModelAdmin, CustomAdmin]
        for _, admin_instance in admin_collector:
            if isinstance(admin_instance, ModelInlineAdmin):
                continue

            permissions = admin_instance.get_all_permissions()
            for permission in permissions:
                await m.Permission.get_or_create(access=permission)

        return "Permissions synced successfully"
