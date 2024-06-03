import os

from unfazed.core import Unfazed


def test_setup_settings():
    os.environ["UNFAZED_SETTINGS_MODULE"] = "unfazedproject.settings"
    unfazed = Unfazed()

    unfazed.setup_settings()

    assert unfazed.settings.INSTALLED_APPS == ["unfazedproject.app"]
    assert unfazed.settings.MIDDLEWARE == [
        "unfazedproject.middlewares.m1.CustomMiddleware1"
    ]
    assert unfazed.settings.DEBUG is True
    assert unfazed.settings.ROOT_URLCONF == "unfazedproject.routes"
    assert unfazed.settings.PROJECT_NAME == "unfazedproject"
