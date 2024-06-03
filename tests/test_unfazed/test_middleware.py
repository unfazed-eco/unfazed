import os

from unfazed.core import Unfazed


def test_middleware_collect():
    os.environ["UNFAZED_SETTINGS_MODULE"] = "unfazedproject.settings"

    unfazed = Unfazed()
    unfazed.setup_middlewares()

    assert len(unfazed.settings.MIDDLEWARE) == 1
