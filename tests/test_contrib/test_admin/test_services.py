import pytest

from tests.apps.admin.account.models import Group, Role, User
from tests.apps.admin.article.models import Article
from unfazed.contrib.admin.registry import ModelAdmin, admin_collector, register
from unfazed.contrib.admin.registry.collector import AdminCollector
from unfazed.contrib.admin.services import AdminModelService
from unfazed.db.tortoise.serializer import TSerializer

# add tests/apps/admin to sys.path

# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "apps", "admin"))


class UserSerializer(TSerializer):
    class Meta:
        model = User


class GroupSerializer(TSerializer):
    class Meta:
        model = Group


class RoleSerializer(TSerializer):
    class Meta:
        model = Role


class ArticleSerializer(TSerializer):
    class Meta:
        model = Article


@pytest.fixture(scope="session")
def collector():
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
        superuser = True

    class Request:
        user = User()

    return Request()


async def test_without_relation(collector: AdminCollector):
    # model-save
    article = {"title": "test", "content": "test", "author": "test", "id": -1}
    request = build_request()
    ret = await AdminModelService.model_save("ArticleAdmin", article, {}, request)

    assert ret.title == "test"
