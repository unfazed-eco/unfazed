import typing as t

import pytest

from tests.apps.admin.registry.models import T1User, T2User
from unfazed.contrib.admin.registry import (
    CustomAdmin,
    ModelAdmin,
    admin_collector,
    fields,
    register,
)
from unfazed.contrib.admin.services import AdminModelService
from unfazed.http import HttpRequest
from unfazed.serializer import Serializer


class _SuperUser:
    is_superuser = True


class _NonSuperUser:
    is_superuser = False


def build_request() -> HttpRequest:
    request = HttpRequest(scope={"type": "http", "method": "GET", "user": _SuperUser()})
    return request


def build_non_super_request() -> HttpRequest:
    request = HttpRequest(
        scope={"type": "http", "method": "GET", "user": _NonSuperUser()}
    )
    return request


@pytest.fixture
def setup_route_service_env() -> t.AsyncGenerator:
    admin_collector.clear()

    class T1UserSerializer(Serializer):
        class Meta:
            model = T1User

    class T2UserSerializer(Serializer):
        class Meta:
            model = T2User

    @register(T1UserSerializer)
    class T1UserAdmin(ModelAdmin):
        async def has_view_perm(self, request: HttpRequest) -> bool:
            return request.user.is_superuser

    @register(T1UserSerializer)
    class T1UserAdmin2(ModelAdmin):
        async def has_view_perm(self, request: HttpRequest) -> bool:
            return request.user.is_superuser

        def to_route(self) -> None:
            return None

    @register(T2UserSerializer)
    class T2UserAdmin(ModelAdmin):
        async def has_view_perm(self, request: HttpRequest) -> bool:
            return request.user.is_superuser

    @register()
    class T1CustomAdmin(CustomAdmin):
        fields_set = [
            fields.CharField(name="name"),
            fields.IntegerField(name="age"),
        ]

        async def has_view_perm(self, request: HttpRequest) -> bool:
            return request.user.is_superuser

    yield

    admin_collector.clear()


async def test_route_service(setup_route_service_env: t.AsyncGenerator) -> None:
    # Test list_route method with superuser
    top_routes = await AdminModelService.list_route(build_request())

    # Assert that routes are returned
    assert isinstance(top_routes, list)
    assert len(top_routes) == 2

    # Check ModelAdmin route
    model_admin_route = None
    custom_admin_route = None

    for sub_route in top_routes:
        for route in sub_route.routes:
            if route.name == "T1UserAdmin":
                model_admin_route = route
            elif route.name == "T1CustomAdmin":
                custom_admin_route = route

    # Assert ModelAdmin route exists and has correct properties
    assert model_admin_route is not None
    assert model_admin_route.name == "T1UserAdmin"
    assert model_admin_route.label == "T1useradmin"
    assert model_admin_route.path == "/T1UserAdmin"
    assert model_admin_route.routes == []

    # Assert CustomAdmin route exists and has correct properties
    assert custom_admin_route is not None
    assert custom_admin_route.name == "T1CustomAdmin"
    assert custom_admin_route.label == "T1customadmin"
    assert custom_admin_route.path == "/T1CustomAdmin"
    assert custom_admin_route.routes == []

    # Test with non-superuser (should return empty list due to permission check)
    routes_non_super = await AdminModelService.list_route(build_non_super_request())
    assert isinstance(routes_non_super, list)
    assert len(routes_non_super) == 0  # No routes for non-superuser
