import typing as t

import pytest

from tests.apps.admin.registry.models import T1User
from unfazed.contrib.admin.registry import admin_collector, register


@pytest.fixture
def setup_route_service_env() -> t.AsyncGenerator:
    admin_collector.clear()

    class T1UserSerializer(Serializer):
        class Meta:
            model = T1User

    @register(T1UserSerializer)
    class T1UserAdmin(ModelAdmin):
        pass

    yield

    admin_collector.clear()
