import os
import typing as t

import pytest
from tortoise import Tortoise

from unfazed.conf import settings
from unfazed.core import Unfazed


@pytest.fixture(scope="package", autouse=True)
async def setup_admin_unfazed() -> t.AsyncGenerator[Unfazed, None]:
    # clear Tortoise apps
    Tortoise.apps = {}
    Tortoise._inited = False
    os.environ["UNFAZED_SETTINGS_MODULE"] = (
        "tests.test_contrib.test_admin.entry.settings"
    )

    settings.clear()

    unfazed = Unfazed()

    await unfazed.setup()

    print(f"admin settings: {os.environ['UNFAZED_SETTINGS_MODULE']}")
    print(f"admin settings: {settings['UNFAZED_SETTINGS']}")
    await unfazed.migrate()

    yield unfazed
