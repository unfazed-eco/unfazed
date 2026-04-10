import typing as t

from unfazed.contrib.admin.registry.schema import AdminBaseAttrs
from unfazed.contrib.admin.schema.request import Action
from unfazed.contrib.admin.services import AdminModelService
from unfazed.contrib.auth import models as m
from unfazed.contrib.common.schema import BaseResponse
from unfazed.http import HttpRequest


class _SuperUser:
    is_superuser = True


def build_request() -> HttpRequest:
    request = HttpRequest(scope={"type": "http", "method": "GET", "user": _SuperUser()})
    return request


def as_admin_attrs(desc: t.Any) -> AdminBaseAttrs:
    return t.cast(AdminBaseAttrs, desc.attrs)


async def test_auth_admin() -> None:
    user_desc = await AdminModelService.model_desc("UserAdmin", build_request())
    group_desc = await AdminModelService.model_desc("GroupAdmin", build_request())
    role_desc = await AdminModelService.model_desc("RoleAdmin", build_request())
    permission_desc = await AdminModelService.model_desc(
        "PermissionAdmin", build_request()
    )
    inline_group_under_user_desc = await AdminModelService.model_desc(
        "InlineGroupUnderUserAdmin", build_request()
    )
    inline_role_under_user_desc = await AdminModelService.model_desc(
        "InlineRoleUnderUserAdmin", build_request()
    )
    inline_user_under_group_desc = await AdminModelService.model_desc(
        "InlineUserUnderGroupAdmin", build_request()
    )
    inline_role_under_group_desc = await AdminModelService.model_desc(
        "InlineRoleUnderGroupAdmin", build_request()
    )
    inline_permission_under_role_desc = await AdminModelService.model_desc(
        "InlinePermissionUnderRoleAdmin", build_request()
    )

    assert user_desc is not None
    assert group_desc is not None
    assert role_desc is not None
    assert permission_desc is not None
    assert inline_group_under_user_desc is not None
    assert inline_role_under_user_desc is not None
    assert inline_user_under_group_desc is not None
    assert inline_role_under_group_desc is not None
    assert inline_permission_under_role_desc is not None

    user_attrs = as_admin_attrs(user_desc)
    group_attrs = as_admin_attrs(group_desc)
    role_attrs = as_admin_attrs(role_desc)
    permission_attrs = as_admin_attrs(permission_desc)
    inline_group_under_user_attrs = as_admin_attrs(inline_group_under_user_desc)
    inline_role_under_user_attrs = as_admin_attrs(inline_role_under_user_desc)
    inline_user_under_group_attrs = as_admin_attrs(inline_user_under_group_desc)
    inline_role_under_group_attrs = as_admin_attrs(inline_role_under_group_desc)
    inline_permission_under_role_attrs = as_admin_attrs(
        inline_permission_under_role_desc
    )

    assert user_attrs.search_fields == ["account", "email"]
    assert user_attrs.search_range_fields == ["created_at", "updated_at"]
    assert user_attrs.list_editable == ["account"]

    assert group_attrs.search_fields == ["name"]
    assert group_attrs.list_editable == ["name"]

    assert role_attrs.list_search == ["id", "name"]
    assert role_attrs.search_fields == ["name"]
    assert role_attrs.list_editable == ["name"]

    assert permission_attrs.search_fields == ["access"]
    assert permission_attrs.list_editable == ["access", "remark"]
    assert "sync_permissions" in permission_desc.actions
    assert "sync_permission" not in permission_desc.actions

    assert inline_group_under_user_attrs.search_fields == ["name"]
    assert inline_role_under_user_attrs.search_fields == ["name"]
    assert inline_user_under_group_attrs.search_fields == ["account", "email"]
    assert inline_role_under_group_attrs.search_fields == ["name"]
    assert inline_permission_under_role_attrs.search_fields == ["access"]

    # save data
    user_save = await AdminModelService.model_save(
        "UserAdmin",
        {
            "account": "admin",
            "email": "admin@unfazed.com",
            "id": -1,
            "password": "password",
            "is_superuser": False,
        },
        build_request(),
    )

    user_id = user_save.id

    # save group
    group_save = await AdminModelService.model_save(
        "GroupAdmin",
        {"name": "group1", "id": -1},
        build_request(),
    )

    group_id = group_save.id

    # save role
    role_save = await AdminModelService.model_save(
        "RoleAdmin",
        {"name": "role1", "id": -1},
        build_request(),
    )

    role_id = role_save.id

    # save permission
    permission_save = await AdminModelService.model_save(
        "PermissionAdmin",
        {"access": "permission1", "id": -1},
        build_request(),
    )

    permission_id = permission_save.id

    # bind user to group
    await AdminModelService.model_save(
        "InlineUserGroupUnderUserAdmin",
        {"user_id": user_id, "group_id": group_id, "id": -1},
        build_request(),
    )

    UserCls = m.AbstractUser.UserCls()
    u1 = await UserCls.get(id=user_id)

    groups_from_user = await u1.query_groups()
    assert len(groups_from_user) == 1

    # bind user to role
    await AdminModelService.model_save(
        "InlineUserRoleUnderUserAdmin",
        {"user_id": user_id, "role_id": role_id, "id": -1},
        build_request(),
    )

    roles_from_user = await u1.query_roles()
    assert len(roles_from_user) == 1

    # create user2

    u2 = await UserCls.create(account="user2")
    # bind user2 to group
    await AdminModelService.model_save(
        "InlineUserGroupUnderGroupAdmin",
        {"user_id": u2.id, "group_id": group_id, "id": -1},
        build_request(),
    )
    g1 = await m.Group.get(id=group_id)
    users_from_group = await g1.query_users()

    assert len(users_from_group) == 2

    # create r2
    r2 = await m.Role.create(name="role2")
    # bind r2 to group
    await AdminModelService.model_save(
        "InlineGroupRoleUnderGroupAdmin",
        {"group_id": group_id, "role_id": r2.id, "id": -1},
        build_request(),
    )

    roles_from_group = await g1.query_roles()
    assert len(roles_from_group) == 1

    # bind permission to role
    await AdminModelService.model_save(
        "InlineRolePermissionUnderRoleAdmin",
        {"role_id": r2.id, "permission_id": permission_id, "id": -1},
        build_request(),
    )

    permissions_from_role = await r2.query_permissions()
    assert len(permissions_from_role) == 1

    # sync permission
    sync_permissions_ret = await AdminModelService.model_action(
        Action(
            name="PermissionAdmin",
            action="sync_permissions",
            search_condition=[],
            form_data={},
            input_data={},
        ),
        build_request(),
    )
    assert isinstance(sync_permissions_ret, BaseResponse)
    assert sync_permissions_ret.data == {"message": "Permissions synced successfully"}

    permission_list = await m.Permission.all()

    assert len(permission_list) == (4 * 4) + 1 + 1
