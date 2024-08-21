import typing as t

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
            "INSTALLED_APPS": ["tests.test_application.success"],
        }
    }
    with mocker.patch.object(utils, "import_setting", return_value=return_value):
        unfazed = Unfazed()

        # success case
        unfazed.setup()
        assert "cmd" in unfazed.command_center.commands
