import typing as t

import pytest

from unfazed import utils
from unfazed.core import Unfazed

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_command_center(mocker: "MockerFixture") -> None:
    return_value = {
        "UNFAZED_SETTINGS": {
            "DEBUG": True,
            "PROJECT_NAME": "test_command_center",
            "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
        }
    }
    with mocker.patch.object(utils, "import_setting", return_value=return_value):
        # success case
        unfazed = Unfazed()
        unfazed.settings.INSTALLED_APPS = ["tests.test_application.success"]
        unfazed.setup()
        assert "cmd" in unfazed.command_center.commands
        assert "_ignore" not in unfazed.command_center.commands
        cmd = unfazed.command_center.commands["cmd"]
        assert cmd._callback() is None

        # 1、test if handle method is not a coroutine
        unfazed = Unfazed()
        unfazed.settings.INSTALLED_APPS = ["tests.test_application.wrongcommand"]
        unfazed.setup()
        with pytest.raises(TypeError):
            cmd = unfazed.command_center.commands["noasync"]
            cmd._callback()

        # 2、test if handle method exists
        unfazed = Unfazed()
        unfazed.settings.INSTALLED_APPS = ["tests.test_application.wrongcommand"]
        unfazed.setup()
        with pytest.raises(NotImplementedError):
            cmd = unfazed.command_center.commands["nohandle"]
            cmd._callback()

        # 3、test if Command is not a subclass of BaseCommand
        unfazed = Unfazed()
        unfazed.settings.INSTALLED_APPS = ["tests.test_application.failedcommand"]
        with pytest.raises(TypeError):
            unfazed.setup()
