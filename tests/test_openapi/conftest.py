import os
import sys
import typing as t

import pytest
from tortoise import Tortoise

from unfazed.conf import settings
from unfazed.core import Unfazed


@pytest.fixture(scope="package", autouse=True)
async def setup_openapi_unfazed() -> t.AsyncGenerator[Unfazed, None]:
    common_dir_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../apps/openapi")
    )

    sys.path.append(common_dir_path)
    # clear Tortoise apps
    Tortoise.apps = {}
    Tortoise._inited = False

    os.environ["UNFAZED_SETTINGS_MODULE"] = "tests.test_openapi.entry.settings"

    settings.clear()
    unfazed = Unfazed()

    await unfazed.setup()

    yield unfazed
