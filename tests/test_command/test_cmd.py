import typing as t

import pytest

from tests.decorators import mock_unfazed_settings
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture


SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_command_center",
    "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
    "ROOT_URLCONF": "tests.apps.cmd.routes",
}


@mock_unfazed_settings(
    UnfazedSettings(**SETTINGS, INSTALLED_APPS=["tests.apps.cmd.common"])
)
def test_cmd_common(mocker: "MockerFixture") -> None:
    unfazed = Unfazed()
    unfazed.setup()
    assert "common" in unfazed.command_center.commands
    assert "_ignore" not in unfazed.command_center.commands
    cmd = unfazed.command_center.commands["common"]
    assert cmd._callback() is None


@mock_unfazed_settings(
    UnfazedSettings(**SETTINGS, INSTALLED_APPS=["tests.apps.cmd.wrong"])
)
def test_cmd_noasync(mocker: "MockerFixture") -> None:
    # 1、test if handle method is not a coroutine
    unfazed = Unfazed()
    unfazed.setup()
    with pytest.raises(TypeError):
        cmd = unfazed.command_center.commands["noasync"]
        cmd._callback()


@mock_unfazed_settings(
    UnfazedSettings(**SETTINGS, INSTALLED_APPS=["tests.apps.cmd.wrong"])
)
def test_cmd_wrong(mocker: "MockerFixture") -> None:
    # 2、test if handle method exists
    unfazed = Unfazed()
    unfazed.setup()
    with pytest.raises(NotImplementedError):
        cmd = unfazed.command_center.commands["nohandle"]
        cmd._callback()


@mock_unfazed_settings(
    UnfazedSettings(**SETTINGS, INSTALLED_APPS=["tests.apps.cmd.failed"])
)
def test_cmd_failed(mocker: "MockerFixture") -> None:
    # 3、test if Command is not a subclass of BaseCommand
    unfazed = Unfazed()
    with pytest.raises(TypeError):
        unfazed.setup()
