import typing as t

import pytest
import pytest_asyncio

from tests.apps.admin.account.models import Book, Group, Profile, User
from tests.apps.admin.article.models import Article
from unfazed.conf import UnfazedSettings, settings
from unfazed.contrib.admin.registry import (
    ActionKwargs,
    ModelAdmin,
    ModelInlineAdmin,
    ToolAdmin,
    action,
    admin_collector,
    fields,
    register,
)
from unfazed.contrib.admin.schema import Action
from unfazed.contrib.admin.services import AdminModelService
from unfazed.exception import PermissionDenied
from unfazed.http import HttpRequest
from unfazed.serializer import Serializer


@pytest.fixture(scope="module", autouse=True)
def setup_collector() -> t.Generator:
    # ===== relation test =======
    class UserSerializer(Serializer):
        class Meta:
            model = User

    class GroupSerializer(Serializer):
        class Meta:
            model = Group

    class BookSerializer(Serializer):
        class Meta:
            model = Book

    class ProfileSerializer(Serializer):
        class Meta:
            model = Profile

    # =============================

    # ===== common test =======

    class ArticleSerializer(Serializer):
        class Meta:
            model = Article

    admin_collector.clear()

    # ===== m2m bk test =======

    @register(UserSerializer)
    class InlineM2MUserAdmin(ModelInlineAdmin):
        pass

    @register(GroupSerializer)
    class M2MGroupAdmin(ModelAdmin):
        inlines = ["InlineM2MUserAdmin"]

    # ====== m2m test ======
    @register(GroupSerializer)
    class InlineM2MGroupAdmin(ModelInlineAdmin):
        pass

    @register(UserSerializer)
    class M2MUserAdmin(ModelAdmin):
        inlines = ["InlineM2MGroupAdmin"]

    # ====== o2o test ======

    @register(ProfileSerializer)
    class InlineO2OProfileAdmin(ModelInlineAdmin):
        pass

    @register(UserSerializer)
    class O2OUserAdmin(ModelAdmin):
        inlines = ["InlineO2OProfileAdmin"]

    # ====== o2o bk test ======
    @register(UserSerializer)
    class InlineBKO2OUserAdmin(ModelInlineAdmin):
        pass

    @register(ProfileSerializer)
    class BKO2OProfileAdmin(ModelAdmin):
        inlines = ["InlineBKO2OUserAdmin"]

    # ====== fk test ======
    @register(BookSerializer)
    class InlineFKBookAdmin(ModelInlineAdmin):
        pass

    @register(UserSerializer)
    class FKUserAdmin(ModelAdmin):
        inlines = ["InlineFKBookAdmin"]

    # ====== bk fk test ======
    @register(UserSerializer)
    class InlineBkFKUserAdmin(ModelInlineAdmin):
        pass

    @register(BookSerializer)
    class BkFKBookAdmin(ModelAdmin):
        inlines = ["InlineBkFKUserAdmin"]

    # ======= without relation test =======
    @register(ArticleSerializer)
    class WithOutArticleAdmin(ModelAdmin):
        pass

    @register(UserSerializer)
    class WithOutUserAdmin(ModelAdmin):
        inlines = ["WithOutArticleAdmin"]

    # =============================

    @register(ArticleSerializer)
    class ArticleAdmin(ModelAdmin):
        @action(name="sync_method")
        def sync_method(self, ctx: ActionKwargs) -> str:
            return "sync hello"

        @action(name="async_method")
        async def async_method(self, ctx: ActionKwargs) -> str:
            return "async hello"

    # ========= tool ==========

    @register()
    class ExportToolAdmin(ToolAdmin):
        fields_set = [
            fields.CharField(name="name"),
            fields.IntegerField(name="age"),
        ]

        output_field = "age"

    # ========= without permission ==========

    @register()
    class WithoutPermissionAdmin(ModelAdmin):
        async def has_view_perm(
            self, request: HttpRequest, *args: t.Any, **kw: t.Any
        ) -> bool:
            return False

    yield admin_collector


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_article() -> t.AsyncGenerator:
    await Article.all().delete()

    for i in range(20):
        await Article.create(title=f"test{i}", content=f"test{i}", author=f"test{i}")

    yield

    await Article.all().delete()


@pytest_asyncio.fixture()
async def setup_user() -> t.AsyncGenerator:
    await User.all().delete()
    await Group.all().delete()
    await Profile.all().delete()
    await Book.all().delete()

    yield

    await User.all().delete()
    await Group.all().delete()
    await Profile.all().delete()
    await Book.all().delete()


class _SuperUser:
    is_superuser = True


class _SuperRequest:
    user = _SuperUser()


def build_request() -> HttpRequest:
    request = HttpRequest(scope={"type": "http", "method": "GET", "user": _SuperUser()})
    return request


async def test_without_relation() -> None:
    # create article
    article = {"title": "test", "content": "test", "author": "test", "id": -1}
    request = t.cast(HttpRequest, build_request())
    ret = await AdminModelService.model_save("ArticleAdmin", article, request)

    assert ret.title == "test"

    # update article
    article = {"title": "test2", "content": "test2", "author": "test2", "id": ret.id}

    ret = await AdminModelService.model_save("ArticleAdmin", article, request)
    assert ret.title == "test2"

    # delete article

    await AdminModelService.model_delete("ArticleAdmin", {"id": ret.id}, request)

    assert await Article.get_or_none(pk=ret.id) is None

    # delete without id
    with pytest.raises(ValueError):
        await AdminModelService.model_delete("ArticleAdmin", {"id": -1}, request)

    # list article
    ret = await AdminModelService.model_data("ArticleAdmin", [], 1, 10, request)

    assert ret["count"] == 20
    assert len(ret["data"]) == 10

    # sync action
    ret = await AdminModelService.model_action(
        Action(
            name="ArticleAdmin",
            action="sync_method",
            search_condition=[],
            form_data={},
            input_data={},
        ),
        request,
    )

    assert ret == "sync hello"

    # async action
    ret = await AdminModelService.model_action(
        Action(
            name="ArticleAdmin",
            action="async_method",
            search_condition=[],
            form_data={},
            input_data={},
        ),
        request,
    )
    assert ret == "async hello"


async def test_model_data_with_relation(setup_user: t.Generator) -> None:
    """
    model_data will not fetch relation data

    """
    request = t.cast(HttpRequest, build_request())

    u1 = await User.create(name="test1", age=1)

    g1 = await Group.create(name="test1")
    g2 = await Group.create(name="test2")

    await u1.groups.add(g1)
    await u1.groups.add(g2)

    ret = await AdminModelService.model_data("M2MUserAdmin", [], 1, 10, request)

    assert ret["count"] == 1
    assert len(ret["data"]) == 1

    u1_dict = ret["data"][0]
    assert "groups" not in u1_dict


class _WithoutSuperUser:
    is_superuser = False


class WithoutSuperRequest:
    user = _WithoutSuperUser()


def build_request_without_super() -> HttpRequest:
    request = HttpRequest(
        scope={"type": "http", "method": "GET", "user": _WithoutSuperUser()}
    )
    return request


async def test_permission_denied() -> None:
    request = t.cast(HttpRequest, build_request_without_super())

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_desc("ArticleAdmin", request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_inlines("ArticleAdmin", {}, request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_data("ArticleAdmin", [], 1, 10, request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_save("ArticleAdmin", {}, request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_delete("ArticleAdmin", {}, request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_action(
            Action(
                name="ArticleAdmin",
                action="sync_method",
                search_condition=[],
                form_data={},
                input_data={},
            ),
            request,
        )


async def test_failed() -> None:
    request = t.cast(HttpRequest, build_request())

    with pytest.raises(KeyError):
        await AdminModelService.model_action(
            Action(
                name="ArticleAdmin",
                action="unknownaction",
                search_condition=[],
                form_data={},
                input_data={},
            ),
            request,
        )


async def test_routes() -> None:
    request = t.cast(HttpRequest, build_request())

    ret = await AdminModelService.list_route(request)

    # TODO
    # need further test when connect to unfazed-admin
    models_ret = [i for i in ret if i.name == "Models"][0]
    tools_ret = [i for i in ret if i.name == "Tools"][0]

    assert "O2OUserAdmin" in [i.name for i in models_ret.routes]
    assert "ExportToolAdmin" in [i.name for i in tools_ret.routes]
    assert "WithoutPermissionAdmin" not in [i.name for i in tools_ret.routes]


def test_settings() -> None:
    settings["UNFAZED_SETTINGS"] = UnfazedSettings(
        PROJECT_NAME="test_admin", VERSION="0.1"
    )

    ret = AdminModelService.site_settings()

    assert ret.title == "Unfazed Admin"


async def test_model_desc() -> None:
    request = t.cast(HttpRequest, build_request())

    ret = await AdminModelService.model_desc("ArticleAdmin", request)

    assert ret.fields
    assert ret.actions
    assert ret.attrs

    # assert "sync_method" in [i["name"] for i in ret["actions"]]
    # assert "async_method" in [i["name"] for i in ret["actions"]]

    # assert "InlineM2MGroupAdmin" in [i["name"] for i in ret["inlines"]]


async def test_model_inlines() -> None:
    request = t.cast(HttpRequest, build_request())

    ret = await AdminModelService.model_inlines("M2MUserAdmin", {}, request)

    assert "InlineM2MGroupAdmin" in ret
