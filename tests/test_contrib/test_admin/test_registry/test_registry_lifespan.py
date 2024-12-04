from unfazed.conf import UnfazedSettings
from unfazed.contrib.admin.registry import admin_collector
from unfazed.contrib.admin.registry.lifespan import AdminWakeup
from unfazed.core import Unfazed

_Settings = {
    "INSTALLED_APPS": [
        "tests.apps.admin.account",
        "tests.apps.admin.article",
        "unfazed.contrib.admin",
    ],
}


async def test_registry_lifespan() -> None:
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(_Settings))
    await unfazed.setup()

    admin_collector.clear()

    lifespan = AdminWakeup(unfazed)

    await lifespan.on_startup()

    assert "ArticleAdmin" in admin_collector
    assert "UserAdmin" in admin_collector
