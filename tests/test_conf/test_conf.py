import os
import sys

import pytest
from pydantic import BaseModel

from unfazed.conf import settings
from unfazed.core import Unfazed


class App3Settings(BaseModel):
    name: str = "app1"


def add_app2_to_sys():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../apps/conf")

    sys.path.append(path)


async def test_setting_proxy() -> None:
    add_app2_to_sys()

    os.environ["UNFAZED_SETTINGS_MODULE"] = "tests.apps.conf.entry.settings"

    unfazed = Unfazed()
    await unfazed.setup()

    assert unfazed.settings.PROJECT_NAME == "test_conf"

    unfazed_setting = settings["UNFAZED_SETTINGS"]
    app1_setting = settings["APP1_SETTINGS"]

    assert unfazed_setting.PROJECT_NAME == "test_conf"

    assert app1_setting.name == "app1"

    app2_setting = settings["APP2_SETTINGS"]

    assert app2_setting.name == "app2"

    # test not found
    with pytest.raises(KeyError):
        settings["notfound"]

    # test set
    settings["APP3_SETTINGS"] = App3Settings()

    del settings["APP3_SETTINGS"]

    with pytest.raises(KeyError):
        settings["APP3_SETTINGS"]

    settings.clear()
