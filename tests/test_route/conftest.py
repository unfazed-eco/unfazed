import os
import sys
import typing as t

import pytest

from unfazed.conf import settings
from unfazed.core import Unfazed


@pytest.fixture(scope="package", autouse=True)
async def setup_route_unfazed() -> t.AsyncGenerator[Unfazed, None]:
    common_dir_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../apps/route")
    )

    sys.path.append(common_dir_path)

    os.environ["UNFAZED_SETTINGS_MODULE"] = "tests.test_route.entry.settings"

    settings.clear()
    unfazed = Unfazed()

    await unfazed.setup()

    yield unfazed
