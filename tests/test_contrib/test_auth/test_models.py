import typing as t

import pytest

from unfazed.contrib.auth import models as m


@pytest.fixture
async def setup_auth_models_env() -> t.AsyncGenerator:
    UserCls = m.AbstractUser.UserCls()
    await UserCls.all().delete()
    await m.Group.all().delete()
    await m.Role.all().delete()
    await m.Permission.all().delete()
    await m.UserGroup.all().delete()
    await m.UserRole.all().delete()
    await m.GroupRole.all().delete()
    await m.RolePermission.all().delete()

    # create two users

    u1 = await UserCls.create(account="u1")
    u2 = await UserCls.create(account="u2")
    u3 = await UserCls.create(account="u3")

    # create two groups
    g1 = await m.Group.create(name="g1")
    g2 = await m.Group.create(name="g2")
    g3 = await m.Group.create(name="g3")

    # create two roles
    r1 = await m.Role.create(name="r1")
    r2 = await m.Role.create(name="r2")
    r3 = await m.Role.create(name="r3")
    r4 = await m.Role.create(name="r4")

    # create two permissions
    p1 = await m.Permission.create(access="p1")
    p2 = await m.Permission.create(access="p2")

    await u1.groups.add(g1)
    await u1.groups.add(g2)
    await u1.roles.add(r1)
    await u1.roles.add(r2)

    await g2.roles.add(r3)

    await g3.roles.add(r3)
    await g3.roles.add(r4)

    await r3.permissions.add(p1)
    await r3.permissions.add(p2)

    await r3.users.add(u2)
    await r3.users.add(u3)

    yield

    await UserCls.all().delete()
    await m.Group.all().delete()
    await m.Role.all().delete()
    await m.Permission.all().delete()
    await m.UserGroup.all().delete()
    await m.UserRole.all().delete()
    await m.GroupRole.all().delete()
    await m.RolePermission.all().delete()


async def test_auth_models_methods(setup_auth_models_env: t.AsyncGenerator) -> None:
    UserCls = m.AbstractUser.UserCls()

    u1 = await UserCls.get(account="u1")
    g3 = await m.Group.get(name="g3")
    g2 = await m.Group.get(name="g2")
    r3 = await m.Role.get(name="r3")

    # query from user

    groups_from_user = await u1.query_groups()
    assert len(groups_from_user) == 2

    roles_from_user = await u1.query_roles()
    assert len(roles_from_user) == 3

    # query from group
    roles_from_group = await g3.query_roles()
    assert len(roles_from_group) == 2

    users_from_group = await g2.query_users()
    assert len(users_from_group) == 1

    # query from role
    users_from_role = await r3.query_users()
    assert len(users_from_role) == 3

    groups_from_role = await r3.query_groups()
    assert len(groups_from_role) == 2

    permissions_from_role = await r3.query_permissions()
    assert len(permissions_from_role) == 2
