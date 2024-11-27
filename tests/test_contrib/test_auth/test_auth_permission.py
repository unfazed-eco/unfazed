import pytest

from tests.apps.auth.models import User
from unfazed.contrib.auth.models import Group, Permission, Role


@pytest.fixture(autouse=True)
async def setup_auth_permission_env():
    await User.all().delete()
    await Group.all().delete()
    await Role.all().delete()
    await Permission.all().delete()

    yield

    await User.all().delete()
    await Group.all().delete()
    await Role.all().delete()
    await Permission.all().delete()


async def test_permission():
    """

    # test user query_roles
    ----------------
    u1 -> g1,g2
    u1 -> r1
    g2 -> r2
    ----------------

    # test user has_permission
    ----------------
    r1 -> p1
    r2 -> p2
    ----------------


    # test role query_user
    ----------------

    r3 -> u2
    g3 -> u3
    r3 -> g3

    ----------------


    """

    u1 = await User.create(account="u1")
    u2 = await User.create(account="u2")
    u3 = await User.create(account="u3")

    g1 = await Group.create(name="g1")
    g2 = await Group.create(name="g2")
    g3 = await Group.create(name="g3")

    r1 = await Role.create(name="r1")
    r2 = await Role.create(name="r2")
    r3 = await Role.create(name="r3")

    p1 = await Permission.create(access="p1")
    p2 = await Permission.create(access="p2")
    p3 = await Permission.create(access="p3")

    await u1.groups.add(g1, g2)
    await u1.roles.add(r1)
    await g2.roles.add(r2)

    # test user query_roles
    assert await u1.query_roles() == [r1, r2]

    await r1.permissions.add(p1)
    await r2.permissions.add(p2)

    assert await u1.has_permission("p1") is True
    assert await u1.has_permission("p2") is True
    assert await u1.has_permission("p3") is False

    await r3.users.add(u2)
    await g3.users.add(u3)
    await r3.groups.add(g3)

    assert await r3.query_users() == [u2, u3]
