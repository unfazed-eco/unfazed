import pytest
from pydantic import BaseModel

from unfazed.conf import settings
from unfazed.core import Unfazed


class App3Settings(BaseModel):
    name: str = "app1"


async def test_setting_proxy(setup_conf_unfazed: Unfazed) -> None:
    unfazed = setup_conf_unfazed

    assert unfazed.settings.PROJECT_NAME == "test_conf"

    unfazed_setting = settings["UNFAZED_SETTINGS"]
    app1_setting = settings["APP1_SETTINGS"]

    assert unfazed_setting.PROJECT_NAME == "test_conf"

    assert app1_setting.name == "app1"

    # test not found
    with pytest.raises(KeyError):
        settings["notfound"]

    # test set
    settings["APP3_SETTINGS"] = App3Settings()

    del settings["APP3_SETTINGS"]

    with pytest.raises(KeyError):
        settings["APP3_SETTINGS"]

    with pytest.warns(UserWarning):
        settings.register_client_cls("APP1_SETTINGS", App3Settings)

    settings.clear()
