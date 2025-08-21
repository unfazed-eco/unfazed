from unfazed.contrib.admin.schema.request import Action
from unfazed.contrib.admin.services import AdminModelService
from unfazed.contrib.auth import models as m
from unfazed.http import HttpRequest


class _SuperUser:
    is_superuser = True


def build_request() -> HttpRequest:
    request = HttpRequest(scope={"type": "http", "method": "GET", "user": _SuperUser()})
    return request


async def test_auth_admin() -> None:
    user_desc = await AdminModelService.model_desc("UserAdmin", build_request())
    group_desc = await AdminModelService.model_desc("GroupAdmin", build_request())
    role_desc = await AdminModelService.model_desc("RoleAdmin", build_request())
    permission_desc = await AdminModelService.model_desc(
        "PermissionAdmin", build_request()
    )

    assert user_desc is not None
    assert group_desc is not None
    assert role_desc is not None
    assert permission_desc is not None

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
    await AdminModelService.model_action(
        Action(
            name="PermissionAdmin",
            action="sync_permissions",
            search_condition=[],
            form_data={},
            input_data={},
        ),
        build_request(),
    )

    permission_list = await m.Permission.all()

    assert len(permission_list) == (4 * 4) + 1 + 1
