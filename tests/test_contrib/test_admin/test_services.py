import typing as t

import pytest

from tests.apps.admin.account.models import Book, Group, Profile, User
from tests.apps.admin.article.models import Article
from unfazed.contrib.admin.registry import ModelAdmin, action, admin_collector, register
from unfazed.contrib.admin.registry.collector import AdminCollector
from unfazed.contrib.admin.services import AdminModelService
from unfazed.db.tortoise.serializer import TSerializer
from unfazed.exception import PermissionDenied
from unfazed.http import HttpRequest


@pytest.fixture(scope="session")
def collector():
    # ===== relation test =======
    class UserSerializer(TSerializer):
        class Meta:
            model = User

    class GroupSerializer(TSerializer):
        class Meta:
            model = Group

    class BookSerializer(TSerializer):
        class Meta:
            model = Book

    class ProfileSerializer(TSerializer):
        class Meta:
            model = Profile

    # =============================

    # ===== common test =======

    class ArticleSerializer(TSerializer):
        class Meta:
            model = Article

    admin_collector.clear()

    # ===== m2m bk test =======

    @register(UserSerializer)
    class InlineM2MUserAdmin(ModelAdmin):
        pass

    @register(GroupSerializer)
    class M2MGroupAdmin(ModelAdmin):
        inlines = [InlineM2MUserAdmin]

    # ====== m2m test ======
    @register(GroupSerializer)
    class InlineM2MGroupAdmin(ModelAdmin):
        pass

    @register(UserSerializer)
    class M2MUserAdmin(ModelAdmin):
        inlines = [InlineM2MGroupAdmin]

    # ====== o2o test ======

    @register(ProfileSerializer)
    class InlineO2OProfileAdmin(ModelAdmin):
        pass

    @register(UserSerializer)
    class O2OUserAdmin(ModelAdmin):
        inlines = [InlineO2OProfileAdmin]

    # ====== o2o bk test ======
    @register(UserSerializer)
    class InlineBKO2OUserAdmin(ModelAdmin):
        pass

    @register(ProfileSerializer)
    class BKO2OProfileAdmin(ModelAdmin):
        inlines = [InlineBKO2OUserAdmin]

    # ====== fk test ======
    @register(BookSerializer)
    class InlineFKBookAdmin(ModelAdmin):
        pass

    @register(UserSerializer)
    class FKUserAdmin(ModelAdmin):
        inlines = [InlineFKBookAdmin]

    # ====== bk fk test ======
    @register(UserSerializer)
    class InlineBkFKUserAdmin(ModelAdmin):
        pass

    @register(BookSerializer)
    class BkFKBookAdmin(ModelAdmin):
        inlines = [InlineBkFKUserAdmin]

    # ======= without relation test =======
    @register(ArticleSerializer)
    class WithOutArticleAdmin(ModelAdmin):
        pass

    @register(UserSerializer)
    class WithOutUserAdmin(ModelAdmin):
        inlines = [WithOutArticleAdmin]

    # =============================

    @register(ArticleSerializer)
    class ArticleAdmin(ModelAdmin):
        @action(name="sync_method")
        def sync_method(self, data: t.Dict, request: HttpRequest) -> str:
            return "sync hello"

        @action(name="async_method")
        async def async_method(self, data: t.Dict, request: HttpRequest) -> str:
            return "async hello"

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
    await Profile.all().delete()
    await Book.all().delete()

    yield

    await User.all().delete()
    await Group.all().delete()
    await Profile.all().delete()
    await Book.all().delete()


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

    # delete without id
    with pytest.raises(ValueError):
        await AdminModelService.model_delete("ArticleAdmin", {"id": -1}, request)

    # list article
    ret = await AdminModelService.model_data("ArticleAdmin", [], 1, 10, request)

    assert ret["count"] == 20
    assert len(ret["data"]) == 10

    # sync action
    ret = await AdminModelService.model_action(
        "ArticleAdmin", "sync_method", {}, request
    )

    assert ret == "sync hello"

    # async action
    ret = await AdminModelService.model_action(
        "ArticleAdmin", "async_method", {}, request
    )
    assert ret == "async hello"


async def test_model_data_with_relation(collector: AdminCollector) -> None:
    """
    model_data will not fetch relation data

    """
    request = build_request()

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


async def test_m2m(collector: AdminCollector, setup_user: t.Generator) -> None:
    # create
    user = {"name": "test", "age": 10, "id": -1}
    group_list = [
        {"name": "test", "id": -1, "__status": "create"},
        {"name": "test2", "id": -1, "__status": "create"},
    ]

    request = build_request()

    ret = await AdminModelService.model_save(
        "M2MUserAdmin", user, {"InlineM2MGroupAdmin": group_list}, request
    )

    assert ret.name == "test"
    assert await Group.all().count() == 2

    # update
    user = {"name": "testupdate", "age": 10, "id": ret.id}
    group1 = await Group.get(name="test")
    group2 = await Group.get(name="test2")

    group_list = [
        {"name": "test_update", "id": group1.id, "__status": "update"},
        {"name": "test2", "id": group2.id, "__status": "do_nothing"},
    ]
    ret = await AdminModelService.model_save(
        "M2MUserAdmin", user, {"InlineM2MGroupAdmin": group_list}, request
    )

    assert ret.name == "testupdate"
    assert await Group.filter(name="test_update").count() == 1

    # delete
    user = {"name": "testupdate", "age": 10, "id": ret.id}
    group_list = [
        {"name": "test_update", "id": group1.id, "__status": "update"},
        {"name": "test2", "id": group2.id, "__status": "delete"},
    ]
    ret = await AdminModelService.model_save(
        "M2MUserAdmin", user, {"InlineM2MGroupAdmin": group_list}, request
    )
    assert ret.name == "testupdate"

    theuser = await User.get(pk=ret.id)
    await theuser.fetch_related("groups")

    assert len(theuser.groups) == 1


async def test_bk_m2m(collector: AdminCollector, setup_user: t.Generator) -> None:
    # create
    request = build_request()

    group = {"name": "test", "id": -1}
    user_list = [
        {"name": "test", "age": 10, "id": -1, "__status": "create"},
        {"name": "test2", "age": 10, "id": -1, "__status": "create"},
    ]

    ret = await AdminModelService.model_save(
        "M2MGroupAdmin", group, {"InlineM2MUserAdmin": user_list}, request
    )

    assert ret.name == "test"
    assert await User.all().count() == 2

    # update
    group = {"name": "testupdate", "id": ret.id}
    user1 = await User.get(name="test")
    user2 = await User.get(name="test2")

    user_list = [
        {"name": "test_update", "age": 10, "id": user1.id, "__status": "update"},
        {"name": "test2", "age": 10, "id": user2.id, "__status": "do_nothing"},
    ]

    ret = await AdminModelService.model_save(
        "M2MGroupAdmin", group, {"InlineM2MUserAdmin": user_list}, request
    )

    assert ret.name == "testupdate"
    assert await User.filter(name="test_update").count() == 1

    # delete
    group = {"name": "testupdate", "id": ret.id}
    user_list = [
        {"name": "test_update", "age": 10, "id": user1.id, "__status": "update"},
        {"name": "test2", "age": 10, "id": user2.id, "__status": "delete"},
    ]

    ret = await AdminModelService.model_save(
        "M2MGroupAdmin", group, {"InlineM2MUserAdmin": user_list}, request
    )

    assert ret.name == "testupdate"
    thegroup = await Group.get(pk=ret.id)
    await thegroup.fetch_related("users")
    assert len(thegroup.users) == 1


async def test_fk(collector: AdminCollector, setup_user: t.Generator) -> None:
    # create
    request = build_request()

    user = {"name": "test", "age": 10, "id": -1}
    book_list = [
        {"title": "test", "author": "test", "id": -1, "__status": "create"},
        {"title": "test2", "author": "test2", "id": -1, "__status": "create"},
    ]

    ret = await AdminModelService.model_save(
        "FKUserAdmin", user, {"InlineFKBookAdmin": book_list}, request
    )

    assert ret.name == "test"
    assert await Book.all().count() == 2

    # update

    user = {"name": "testupdate", "age": 11, "id": ret.id}

    book1 = await Book.get(title="test")
    book2 = await Book.get(title="test2")
    book_list = [
        {
            "title": "testupdate",
            "author": "test",
            "id": book1.id,
            "owner_id": ret.id,
            "__status": "update",
        },
        {
            "title": "test2",
            "author": "test2",
            "id": book2.id,
            "owner_id": ret.id,
            "__status": "do_nothing",
        },
    ]

    ret = await AdminModelService.model_save(
        "FKUserAdmin", user, {"InlineFKBookAdmin": book_list}, request
    )

    assert ret.name == "testupdate"
    assert await Book.filter(title="testupdate").count() == 1
    assert await Book.filter(title="test").count() == 0

    # delete
    user = {"name": "testupdate", "age": 11, "id": ret.id}
    book1 = await Book.get(title="testupdate")
    book2 = await Book.get(title="test2")
    book_list = [
        {
            "title": "testupdate",
            "author": "test",
            "id": book1.id,
            "owner_id": ret.id,
            "__status": "update",
        },
        {
            "title": "test2",
            "author": "test2",
            "id": book2.id,
            "owner_id": ret.id,
            "__status": "delete",
        },
    ]
    ret = await AdminModelService.model_save(
        "FKUserAdmin", user, {"InlineFKBookAdmin": book_list}, request
    )

    theuser = await User.get(pk=ret.id)
    await theuser.fetch_related("books")
    assert len(theuser.books) == 1

    # bk fk relation

    with pytest.raises(ValueError):
        book = {"title": "test", "author": "test", "id": -1, "owner_id": -1}
        user_list = [
            {"name": "test", "age": 10, "id": -1, "__status": "create"},
        ]

        await AdminModelService.model_save(
            "BkFKBookAdmin", book, {"InlineBkFKUserAdmin": user_list}, request
        )


async def test_o2o(collector: AdminCollector, setup_user: t.Generator) -> None:
    # create
    request = build_request()

    user = {"name": "test", "age": 10, "id": -1}
    profile = {"avatar": "test", "id": -1, "__status": "create"}

    ret = await AdminModelService.model_save(
        "O2OUserAdmin", user, {"InlineO2OProfileAdmin": [profile]}, request
    )

    assert ret.name == "test"
    assert await Profile.all().count() == 1

    # update
    profile_ins = await Profile.get(user_id=ret.id)
    user = {"name": "testupdate", "age": 11, "id": ret.id}
    profile = {
        "avatar": "testupdate",
        "id": profile_ins.id,
        "user_id": ret.id,
        "__status": "update",
    }

    ret = await AdminModelService.model_save(
        "O2OUserAdmin", user, {"InlineO2OProfileAdmin": [profile]}, request
    )

    assert ret.name == "testupdate"
    assert await Profile.filter(avatar="testupdate").count() == 1
    assert await Profile.filter(avatar="test").count() == 0

    # no action

    profile = {
        "avatar": "testupdate",
        "id": profile_ins.id,
        "user_id": ret.id,
        "__status": "no_action",
    }

    ret = await AdminModelService.model_save(
        "O2OUserAdmin", user, {"InlineO2OProfileAdmin": [profile]}, request
    )
    assert ret.name == "testupdate"
    assert await Profile.filter(avatar="testupdate").count() == 1
    assert await Profile.filter(avatar="test").count() == 0

    # delete
    user = {"name": "testupdate", "age": 11, "id": ret.id}
    profile = {
        "avatar": "testupdate",
        "id": profile_ins.id,
        "user_id": ret.id,
        "__status": "delete",
    }

    ret = await AdminModelService.model_save(
        "O2OUserAdmin", user, {"InlineO2OProfileAdmin": [profile]}, request
    )

    theuser = await User.get(pk=ret.id)
    await theuser.fetch_related("profile")
    assert theuser.profile is None

    # bk o2o relation
    with pytest.raises(ValueError):
        profile = {"avatar": "test", "id": -1, "user_id": -1}
        user_list = [
            {"name": "test", "age": 10, "id": -1, "__status": "create"},
        ]

        await AdminModelService.model_save(
            "BKO2OProfileAdmin", profile, {"InlineBKO2OUserAdmin": user_list}, request
        )


def build_request_without_super():
    class User:
        is_superuser = False

    class Request:
        user = User()

    return Request()


async def test_permission_denied(collector: AdminCollector) -> None:
    request = build_request_without_super()

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_desc("ArticleAdmin", request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_detail("ArticleAdmin", {}, request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_data("ArticleAdmin", [], 1, 10, request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_save("ArticleAdmin", {}, {}, request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_delete("ArticleAdmin", {}, request)

    with pytest.raises(PermissionDenied):
        await AdminModelService.model_action("ArticleAdmin", "sync_method", {}, request)


async def test_failed(collector: AdminCollector) -> None:
    request = build_request()

    with pytest.raises(KeyError):
        await AdminModelService.model_action(
            "ArticleAdmin", "unknownaction", {}, request
        )

    # no relation
    with pytest.raises(ValueError):
        article = {"title": "test", "content": "test", "author": "test", "id": -1}
        user = {"name": "test", "age": 10, "id": -1}

        await AdminModelService.model_save(
            "WithOutUserAdmin", user, {"WithOutArticleAdmin": [article]}, request
        )
