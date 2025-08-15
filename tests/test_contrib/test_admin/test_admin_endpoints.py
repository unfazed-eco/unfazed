import typing as t
from unittest.mock import patch

import pytest_asyncio

from tests.apps.admin.article.models import Author
from unfazed.contrib.admin.registry import (
    ActionKwargs,
    ModelAdmin,
    action,
    admin_collector,
    register,
)
from unfazed.core import Unfazed
from unfazed.http import HttpRequest, HttpResponse
from unfazed.serializer import Serializer
from unfazed.test import Requestfactory


class User:
    is_superuser = True
    account = "unfazed"
    email = "user@unfazed.com"


class UnkownUser:
    is_superuser = True
    account = ""
    email = ""


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_endpoint_env() -> t.AsyncGenerator[None, None]:
    admin_collector.clear()
    await Author.all().delete()

    class AuthorSerializer(Serializer):
        class Meta:
            model = Author

    @register(AuthorSerializer)
    class AuthorAdmin(ModelAdmin):
        @action(name="test_action1", confirm=True)
        async def test_action1(self, ctx: ActionKwargs) -> str:
            return "test_action"

        @action(name="test_action2")
        async def test_action2(self, ctx: ActionKwargs) -> t.Dict:
            return {"foo": "bar"}

        @action(name="test_action3")
        async def test_action3(self, ctx: ActionKwargs) -> t.List:
            return [{"foo": "bar"}]

        @action(name="test_action4")
        async def test_action4(self, ctx: ActionKwargs) -> HttpResponse:
            return HttpResponse("hello, unfazed")

    yield

    admin_collector.clear()
    await Author.all().delete()


async def test_endpoints(setup_admin_unfazed: Unfazed) -> None:
    with patch.object(HttpRequest, "user", User()):
        request = Requestfactory(setup_admin_unfazed)

        resp1 = await request.get("/api/contrib/admin/route-list")
        assert resp1.status_code == 200

        resp2 = await request.get("/api/contrib/admin/settings")
        assert resp2.status_code == 200

        resp3 = await request.post(
            "/api/contrib/admin/model-desc", json={"name": "AuthorAdmin"}
        )
        assert resp3.status_code == 200

        resp4 = await request.post(
            "/api/contrib/admin/model-inlines",
            json={"name": "AuthorAdmin", "data": {}},
        )
        assert resp4.status_code == 200

        resp5 = await request.post(
            "/api/contrib/admin/model-action",
            json={
                "name": "AuthorAdmin",
                "action": "test_action1",
                "form_data": {},
                "input_data": {},
                "search_condition": [],
            },
        )

        assert resp5.status_code == 200

        resp6 = await request.post(
            "/api/contrib/admin/model-action",
            json={
                "name": "AuthorAdmin",
                "action": "test_action2",
                "form_data": {},
                "input_data": {},
                "search_condition": [],
            },
        )

        assert resp6.status_code == 200

        resp7 = await request.post(
            "/api/contrib/admin/model-action",
            json={
                "name": "AuthorAdmin",
                "action": "test_action4",
                "form_data": {},
                "input_data": {},
                "search_condition": [],
            },
        )

        assert resp7.status_code == 200

        resp8 = await request.post(
            "/api/contrib/admin/model-action",
            json={
                "name": "AuthorAdmin",
                "action": "test_action3",
                "form_data": {},
                "input_data": {},
                "search_condition": [],
            },
        )

        assert resp8.status_code == 200

        resp9 = await request.post(
            "/api/contrib/admin/model-save",
            json={
                "name": "AuthorAdmin",
                "data": {
                    "name": "test_endpoints",
                    "age": 18,
                    "id": -1,
                },
            },
        )

        assert resp9.status_code == 200
        ret = resp9.json()["data"]

        resp10 = await request.post(
            "/api/contrib/admin/model-data",
            json={"name": "AuthorAdmin", "cond": [], "page": 1, "size": 10},
        )

        assert resp10.status_code == 200

        resp11 = await request.post(
            "/api/contrib/admin/model-delete",
            json={
                "name": "AuthorAdmin",
                "data": {"id": ret["id"]},
            },
        )

        assert resp11.status_code == 200

        # test openapi integration
        resp12 = await request.get("/openapi/openapi.json")
        assert resp12.status_code == 200


async def test_endpoints_with_unknown_user(setup_admin_unfazed: Unfazed) -> None:
    with patch.object(HttpRequest, "user", UnkownUser()):
        with patch.object(HttpRequest, "client", None):
            request = Requestfactory(setup_admin_unfazed)

            resp5 = await request.post(
                "/api/contrib/admin/model-action",
                json={
                    "name": "AuthorAdmin",
                    "action": "test_action1",
                    "form_data": {},
                    "input_data": {},
                    "search_condition": [],
                },
            )

            assert resp5.status_code == 200
