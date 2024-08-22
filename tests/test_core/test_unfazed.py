import threading
import time
import typing as t
from unittest.mock import patch

import pytest

from tests.decorators import mock_unfazed_settings
from unfazed.app import AppCenter
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture


_Setting = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_launch",
    "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
    "ROOT_URLCONF": "tests.apps.core.routes",
    "INSTALLED_APPS": ["tests.apps.core.common"],
}

Setting = UnfazedSettings(**_Setting)


@mock_unfazed_settings(Setting)
def test_app_launch(mocker: "MockerFixture") -> None:
    unfazed = Unfazed()

    unfazed.setup()

    assert unfazed.ready is True
    # test repeated setup
    unfazed.setup()
    assert unfazed.ready is True


@mock_unfazed_settings(Setting)
def test_loading_state(mocker: "MockerFixture") -> None:
    unfazed = Unfazed()

    # test loading state
    def new_app_center_setup(self):
        time.sleep(1)

    with patch.object(AppCenter, "setup", new=new_app_center_setup):
        with pytest.raises(RuntimeError):
            threading.Thread(target=unfazed.setup).start()
            time.sleep(0.1)
            unfazed.setup()
