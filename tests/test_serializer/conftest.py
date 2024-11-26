import os

import pytest
from tortoise import Tortoise

from unfazed.conf import settings
from unfazed.core import Unfazed


@pytest.fixture(scope="package", autouse=True)
async def setup_serializer_unfazed():
    # clear Tortoise apps
    Tortoise.apps = {}
    Tortoise._inited = False
    os.environ["UNFAZED_SETTINGS_MODULE"] = "tests.test_serializer.entry.settings"

    settings.clear()

    unfazed = Unfazed()

    await unfazed.setup()
    await unfazed.migrate()

    yield unfazed
