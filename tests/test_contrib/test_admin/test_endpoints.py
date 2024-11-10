import os
import typing as t
from unittest.mock import patch

import pytest_asyncio

from tests.apps.admin.article.models import Author
from unfazed.contrib.admin.registry import ModelAdmin, action, admin_collector, register
from unfazed.core import Unfazed
from unfazed.db.tortoise.serializer import TSerializer
from unfazed.http import HttpRequest
from unfazed.test import Requestfactory


class User:
    is_superuser = True
    username = "unfazed"
    email = "user@unfazed.com"


async def reiceive(*args, **kwargs):
    pass


async def send(*args, **kwargs):
    pass


@pytest_asyncio.fixture(scope="session")
async def setup_env():
    import asyncio

    loop = asyncio.get_running_loop()
    print(f"setup_env {loop} - {id(loop)}")

    admin_collector.clear()
    await Author.all().delete()

    class AuthorSerializer(TSerializer):
        class Meta:
            model = Author

    @register(AuthorSerializer)
    class AuthorAdmin(ModelAdmin):
        @action(name="test_action1", confirm=True)
        async def test_action1(
            self, data: t.Dict, request: HttpRequest | None = None
        ) -> str:
            return "test_action"

        @action(name="test_action2")
        async def test_action2(
            self, data: t.Dict, request: HttpRequest | None = None
        ) -> t.Dict:
            return {"foo": "bar"}

        @action(name="test_action3")
        async def test_action3(
            self, data: t.Dict, request: HttpRequest | None = None
        ) -> t.List:
            return [{"foo": "bar"}]

        @property
        def name(self):
            return "AuthorAdmin"

    yield

    admin_collector.clear()
    await Author.all().delete()


_Settings = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_db",
    "ROOT_URLCONF": "tests.apps.routes",
    "INSTALLED_APPS": [
        "tests.apps.orm.common",
        "tests.apps.orm.serializer",
        "tests.apps.admin.account",
        "tests.apps.admin.article",
        "unfazed.contrib.admin",
    ],
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "unfazed.db.tortoise.backends.mysql",
                "CREDENTIALS": {
                    "HOST": os.environ.get("MYSQL_HOST", "mysql"),
                    "PORT": int(os.environ.get("MYSQL_PORT", 3306)),
                    "USER": "root",
                    "PASSWORD": "app",
                    "DATABASE": "test_app",
                },
            }
        }
    },
}


# async def test_endpoints_with_scope(setup_env: t.Generator) -> None:
#     unfazed = Unfazed(settings=UnfazedSettings(**_Settings))
#     await unfazed.setup()

#     ret = await unfazed(
#         scope={
#             "type": "http",
#             "method": "GET",
#             "scheme": "https",
#             "server": ("www.example.org", 80),
#             "path": "/api/contrib/admin/route-list",
#             "user": User(),
#         },
#         receive=reiceive,
#         send=send,
#     )

#     assert ret is None


async def test_endpoints(setup_env: t.Generator, prepare_unfazed: Unfazed) -> None:
    # unfazed = Unfazed(settings=UnfazedSettings(**_Settings))

    # await unfazed.setup()

    import asyncio

    loop = asyncio.get_running_loop()
    print(f"test_endpoints {loop} - {id(loop)}")

    with patch.object(HttpRequest, "user", User()):
        request = Requestfactory(prepare_unfazed)

        resp = await request.get("/api/contrib/admin/route-list")
        assert resp.status_code == 200

        resp = await request.get("/api/contrib/admin/settings")
        assert resp.status_code == 200

        resp = await request.post(
            "/api/contrib/admin/model-desc", json={"name": "AuthorAdmin"}
        )
        assert resp.status_code == 200

        resp = await request.post(
            "/api/contrib/admin/model-detail",
            json={"name": "AuthorAdmin", "data": {}},
        )
        assert resp.status_code == 200

        resp = await request.post(
            "/api/contrib/admin/model-action",
            json={
                "name": "AuthorAdmin",
                "action": "test_action1",
                "data": {},
            },
        )

        assert resp.status_code == 200


# resp = request.post(
#     "/api/contrib/admin/model-action",
#     json={
#         "name": "AuthorAdmin",
#         "action": "test_action2",
#         "data": {},
#     },
# )

# assert resp.status_code == 200

# resp = request.post(
#     "/api/contrib/admin/model-action",
#     json={
#         "name": "AuthorAdmin",
#         "action": "test_action3",
#         "data": {},
#     },
# )

# assert resp.status_code == 200


#         resp = request.post(
#             "/api/contrib/admin/model-save",
#             json={
#                 "name": "AuthorAdmin",
#                 "data": {
#                     "name": "test_endpoints",
#                     "age": 18,
#                     "id": -1,
#                 },
#                 "inlines": {},
#             },
#         )

#         assert resp.status_code == 200

# resp = request.post(
#     "/api/contrib/admin/model-data",
#     json={"name": "ArticleAdmin", "cond": {}, "page": 1, "size": 10},
# )
