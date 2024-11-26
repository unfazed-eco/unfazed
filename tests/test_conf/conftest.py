import os
import sys

import pytest

from unfazed.conf import settings
from unfazed.core import Unfazed


@pytest.fixture(autouse=True, scope="package")
async def setup_conf_unfazed():
    settings.clear()

    os.environ["UNFAZED_SETTINGS_MODULE"] = "tests.test_conf.entry.settings"
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../apps/conf")

    sys.path.append(path)

    unfazed = Unfazed()
    await unfazed.setup()

    yield unfazed
