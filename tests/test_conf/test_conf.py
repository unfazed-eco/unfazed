import typing as t

import pytest
from pydantic import BaseModel

from unfazed.conf import settings

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture


class Conf(BaseModel):
    name: str = "Unfazed"


def test_setting_proxy(mocker: "MockerFixture") -> None:
    settings._settingskv = {}

    s = Conf()
    settings["test"] = s

    assert settings["test"] == s
    assert settings["test"].name == "Unfazed"

    with pytest.raises(KeyError):
        settings["notfound"]

    del settings["test"]

    with pytest.raises(KeyError):
        settings["test"]

    # reset
    settings._settingskv = None
