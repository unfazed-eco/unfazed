import typing as t

import pytest

from tests.apps.admin.account.models import Group, Role, User
from tests.apps.admin.article.models import Article
from unfazed.contrib.admin.registry import ModelAdmin, admin_collector, register
from unfazed.contrib.admin.registry.collector import AdminCollector
from unfazed.contrib.admin.services import AdminModelService
from unfazed.db.tortoise.serializer import TSerializer

# add tests/apps/admin to sys.path

# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "apps", "admin"))


@pytest.fixture(scope="session")
def collector():
    class UserSerializer(TSerializer):
        class Meta:
            model = User

    class RoleSerializer(TSerializer):
        class Meta:
            model = Role

    class GroupSerializer(TSerializer):
        class Meta:
            model = Group

    class ArticleSerializer(TSerializer):
        class Meta:
            model = Article

    admin_collector.clear()

    @register(GroupSerializer)
    class GroupAdmin(ModelAdmin):
        inlines = []

    @register(RoleSerializer)
    class RoleAdmin(ModelAdmin):
        inlines = []

    @register(UserSerializer)
    class UserAdmin(ModelAdmin):
        inlines = []

    @register(ArticleSerializer)
    class ArticleAdmin(ModelAdmin):
        pass

    yield admin_collector


def build_request():
    class User:
        is_superuser = True

    class Request:
        user = User()

    return Request()


@pytest.fixture
async def setup_article():
    await Article.all().delete()

    for i in range(20):
        await Article.create(title=f"test{i}", content=f"test{i}", author=f"test{i}")

    yield

    await Article.all().delete()


@pytest.fixture
async def setup_user():
    await User.all().delete()
    await Group.all().delete()
    await Role.all().delete()

    # create 2 users

    user1 = await User.create(name="test1", age=1)
    user2 = await User.create(name="test2", age=2)

    # create 2 groups
    group1 = await Group.create(name="group1")
    group2 = await Group.create(name="group2")

    # create 2 roles
    role1 = await Role.create(name="role1")
    role2 = await Role.create(name="role2")

    # add user1 to group1
    await group1.users.add(user1)
    await group2.users.add(user1)
    await role1.groups.add(group1)

    # add user2 to group2
    await group2.users.add(user2)
    await role2.groups.add(group2)

    yield

    await User.all().delete()
    await Group.all().delete()
    await Role.all().delete()


async def test_without_relation(
    collector: AdminCollector,
    setup_article: t.Generator,
) -> None:
    # create article
    article = {"title": "test", "content": "test", "author": "test", "id": -1}
    request = build_request()
    ret = await AdminModelService.model_save("ArticleAdmin", article, {}, request)

    assert ret.title == "test"

    # update article
    article = {"title": "test2", "content": "test2", "author": "test2", "id": ret.id}

    ret = await AdminModelService.model_save("ArticleAdmin", article, {}, request)
    assert ret.title == "test2"

    # delete article

    await AdminModelService.model_delete("ArticleAdmin", {"id": ret.id}, request)

    assert await Article.get_or_none(pk=ret.id) is None

    # list article
    ret = await AdminModelService.model_data("ArticleAdmin", [], 1, 10, request)

    assert ret["count"] == 20
    assert len(ret["data"]) == 10


async def test_relations(collector: AdminCollector, setup_user: t.Generator) -> None:
    # create
    pass
