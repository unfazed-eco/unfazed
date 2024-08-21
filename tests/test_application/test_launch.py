import threading
import time
import typing as t
from unittest.mock import patch

import pytest

from unfazed import utils
from unfazed.app import AppCenter
from unfazed.core import Unfazed

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_app_launch(mocker: "MockerFixture") -> None:
    return_value = {
        "UNFAZED_SETTINGS": {
            "DEBUG": True,
            "PROJECT_NAME": "test_app_launch",
            "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
            "ROOT_URLCONF": "tests.test_application.mainapp.routes",
            "INSTALLED_APPS": ["tests.test_application.success"],
        }
    }
    with mocker.patch.object(utils, "import_setting", return_value=return_value):
        unfazed = Unfazed()
        unfazed.setup()

        assert unfazed.ready is True

        # 1、test repeated setup
        unfazed.setup()

        # 2、test loading state
        def new_app_center_setup(self):
            time.sleep(1)

        # with mocker.patch.object(AppCenter, "setup", new=new_app_center_setup):
        with patch.object(AppCenter, "setup", new=new_app_center_setup):
            unfazed = Unfazed()
            with pytest.raises(RuntimeError):
                threading.Thread(target=unfazed.setup).start()
                time.sleep(0.1)
                unfazed.setup()
