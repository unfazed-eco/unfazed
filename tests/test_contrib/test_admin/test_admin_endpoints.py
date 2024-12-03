import typing as t
from unittest.mock import patch

import pytest_asyncio

from tests.apps.admin.article.models import Author
from unfazed.contrib.admin.registry import ModelAdmin, action, admin_collector, register
from unfazed.core import Unfazed
from unfazed.http import HttpRequest, HttpResponse
from unfazed.serializer.tortoise import TSerializer
from unfazed.test import Requestfactory


class User:
    is_superuser = True
    username = "unfazed"
    email = "user@unfazed.com"


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_endpoint_env() -> t.AsyncGenerator[None, None]:
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

        @action(name="test_action4")
        async def test_action4(
            self, data: t.Dict, request: HttpRequest | None = None
        ) -> HttpResponse:
            return HttpResponse("hello, unfazed")

    yield

    admin_collector.clear()
    await Author.all().delete()


async def test_endpoints(setup_admin_unfazed: Unfazed) -> None:
    with patch.object(HttpRequest, "user", User()):
        request = Requestfactory(setup_admin_unfazed)

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

        resp = await request.post(
            "/api/contrib/admin/model-action",
            json={
                "name": "AuthorAdmin",
                "action": "test_action2",
                "data": {},
            },
        )

        assert resp.status_code == 200

        resp = await request.post(
            "/api/contrib/admin/model-action",
            json={
                "name": "AuthorAdmin",
                "action": "test_action4",
                "data": {},
            },
        )

        assert resp.status_code == 200

        resp = await request.post(
            "/api/contrib/admin/model-action",
            json={
                "name": "AuthorAdmin",
                "action": "test_action3",
                "data": {},
            },
        )

        assert resp.status_code == 200

        resp = await request.post(
            "/api/contrib/admin/model-save",
            json={
                "name": "AuthorAdmin",
                "data": {
                    "name": "test_endpoints",
                    "age": 18,
                    "id": -1,
                },
                "inlines": {},
            },
        )

        assert resp.status_code == 200
        ret = resp.json()

        resp = await request.post(
            "/api/contrib/admin/model-data",
            json={"name": "AuthorAdmin", "cond": [], "page": 1, "size": 10},
        )

        assert resp.status_code == 200

        resp = await request.post(
            "/api/contrib/admin/model-delete",
            json={
                "name": "AuthorAdmin",
                "data": {"id": ret["id"]},
            },
        )

        assert resp.status_code == 200
